from fastapi import APIRouter, Depends
import difflib
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.models import Product, ProductImage, SearchHistory, Shop, ShopAddress, ProductCategory, ShopProduct
from math import radians, sin, cos, sqrt, atan2


router = APIRouter()

def score_match(name: str, q: str) -> float:
    if not name:
        return 0.0
    name_l = name.lower()
    q_l = q.lower()
    if name_l == q_l:
        return 100.0
    if name_l.startswith(q_l):
        return 90.0
    if q_l in name_l:
        return 75.0
    return difflib.SequenceMatcher(None, name_l, q_l).ratio() * 60.0

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


@router.get("/products")
async def search_products(q: str, user_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_session)):
    res = await db.execute(
        select(Product, ProductCategory)
        .join(ProductCategory, ProductCategory.category_id == Product.category_id, isouter=True)
        .where(Product.product_name.ilike(f"%{q}%"))
    )
    rows = res.all()
    product_ids = [p.product_id for p, _ in rows]
    img_map = {}
    if product_ids:
        imgs = await db.execute(select(ProductImage).where(ProductImage.product_id.in_(product_ids)))
        for img in imgs.scalars().all():
            # take first image per product
            img_map.setdefault(img.product_id, img.image_url)
    if user_id is not None:
        db.add(SearchHistory(user_id=user_id, search_item=q))
        await db.commit()
    out = []
    for p, cat in rows:
        name = p.product_name or ""
        brand = p.brand or ""
        cat_name = (cat.category_name if cat else "") or ""
        base = score_match(name, q)
        bonus = 0.0
        if q.lower() in brand.lower():
            bonus += 12.0
        if q.lower() in cat_name.lower():
            bonus += 10.0
        out.append({
            "product_id": p.product_id,
            "product_name": p.product_name,
            "brand": p.brand,
            "color": p.color,
            "image_url": img_map.get(p.product_id),
            "_score": base + bonus,
        })
    out.sort(key=lambda x: x["_score"], reverse=True)
    return [{k: v for k, v in d.items() if k != "_score"} for d in out]


@router.get("/shops")
async def search_shops(q: str, db: AsyncSession = Depends(get_session)):
    res = await db.execute(
        select(Shop, ShopAddress).join(ShopAddress, ShopAddress.shop_id == Shop.shop_id).where(Shop.shop_name.ilike(f"%{q}%"))
    )
    rows = res.all()
    out = []
    for s, addr in rows:
        out.append({
            "shop_id": s.shop_id,
            "shop_name": s.shop_name,
            "city": addr.city,
            "area": addr.area,
            "shop_image": s.shop_image,
            "_score": score_match(s.shop_name or "", q),
        })
    out.sort(key=lambda x: x["_score"], reverse=True)
    return [{k: v for k, v in d.items() if k != "_score"} for d in out]


@router.get("/categories")
async def search_by_category(q: str, db: AsyncSession = Depends(get_session)):
    res = await db.execute(
        select(Product, ProductCategory)
        .join(ProductCategory, ProductCategory.category_id == Product.category_id, isouter=True)
        .where(ProductCategory.category_name.ilike(f"%{q}%"))
    )
    rows = res.all()
    product_ids = [p.product_id for p, _ in rows]
    img_map = {}
    if product_ids:
        imgs = await db.execute(select(ProductImage).where(ProductImage.product_id.in_(product_ids)))
        for img in imgs.scalars().all():
            img_map.setdefault(img.product_id, img.image_url)
    out = []
    for p, cat in rows:
        out.append({
            "product_id": p.product_id,
            "product_name": p.product_name,
            "brand": p.brand,
            "color": p.color,
            "category": cat.category_name if cat else None,
            "image_url": img_map.get(p.product_id),
            "_score": score_match((cat.category_name if cat else "") or "", q),
        })
    out.sort(key=lambda x: x["_score"], reverse=True)
    return [{k: v for k, v in d.items() if k != "_score"} for d in out]

@router.get("/products_nearby")
async def products_nearby(q: str | None = None, lat: float = None, lon: float = None, radius_km: float = 5.0, db: AsyncSession = Depends(get_session)):
    if lat is None or lon is None:
        # fallback to normal search
        return await search_products(q or "", db=db)
    # find nearby shops
    res = await db.execute(select(Shop, ShopAddress).join(ShopAddress, ShopAddress.shop_id == Shop.shop_id))
    shops = []
    for s, addr in res.all():
        if addr.latitude is None or addr.longitude is None:
            continue
        distance = haversine(float(addr.latitude), float(addr.longitude), lat, lon)
        if distance <= radius_km:
            shops.append(s.shop_id)
    if not shops:
        return []
    # fetch products available in those shops
    res2 = await db.execute(
        select(ShopProduct, Product, ProductCategory)
        .join(Product, Product.product_id == ShopProduct.product_id)
        .join(ProductCategory, ProductCategory.category_id == Product.category_id, isouter=True)
        .where(ShopProduct.shop_id.in_(shops))
    )
    rows = res2.all()
    product_ids = list({p.product_id for _, p, _ in rows})
    img_map = {}
    if product_ids:
        imgs = await db.execute(select(ProductImage).where(ProductImage.product_id.in_(product_ids)))
        for img in imgs.scalars().all():
            img_map.setdefault(img.product_id, img.image_url)
    out = []
    for sp, p, cat in rows:
        if q and q.strip():
            name = p.product_name or ""
            brand = p.brand or ""
            cat_name = (cat.category_name if cat else "") or ""
            base = score_match(name, q)
            bonus = (12.0 if q.lower() in brand.lower() else 0.0) + (10.0 if q.lower() in cat_name.lower() else 0.0)
            total = base + bonus
        else:
            # no query: prefer availability and lower price
            total = 50.0 - (float(sp.price) if sp.price is not None else 0.0)
        out.append({
            "product_id": p.product_id,
            "product_name": p.product_name,
            "brand": p.brand,
            "color": p.color,
            "image_url": img_map.get(p.product_id),
            "_score": total,
        })
    # deduplicate by product_id keeping highest score
    best = {}
    for d in out:
        pid = d["product_id"]
        if pid not in best or d["_score"] > best[pid]["_score"]:
            best[pid] = d
    final = list(best.values())
    final.sort(key=lambda x: x["_score"], reverse=True)
    return [{k: v for k, v in d.items() if k != "_score"} for d in final]

@router.get("/popular")
async def popular_products(lat: float | None = None, lon: float | None = None, radius_km: float = 5.0, limit: int = 12, db: AsyncSession = Depends(get_session)):
    # popularity from search history counts
    res = await db.execute(select(Product))
    products = res.scalars().all()
    # nearby shops filter if location provided
    nearby_shop_ids = None
    if lat is not None and lon is not None:
        res_shops = await db.execute(select(Shop, ShopAddress).join(ShopAddress, ShopAddress.shop_id == Shop.shop_id))
        nearby_shop_ids = []
        for s, addr in res_shops.all():
            if addr.latitude is None or addr.longitude is None:
                continue
            distance = haversine(float(addr.latitude), float(addr.longitude), lat, lon)
            if distance <= radius_km:
                nearby_shop_ids.append(s.shop_id)
    # calculate popularity
    # naive approach: presence in nearby shops and global name frequency in search history
    freq = {}
    hist = await db.execute(select(SearchHistory))
    for h in hist.scalars().all():
        key = (h.search_item or "").strip().lower()
        if key:
            freq[key] = freq.get(key, 0) + 1
    # image map
    ids = [p.product_id for p in products]
    img_map = {}
    if ids:
        imgs = await db.execute(select(ProductImage).where(ProductImage.product_id.in_(ids)))
        for img in imgs.scalars().all():
            img_map.setdefault(img.product_id, img.image_url)
    scored = []
    for p in products:
        base = freq.get((p.product_name or "").lower(), 0) * 5.0
        availability_bonus = 0.0
        if nearby_shop_ids is not None and nearby_shop_ids:
            sp = await db.execute(select(ShopProduct).where(ShopProduct.product_id == p.product_id, ShopProduct.shop_id.in_(nearby_shop_ids)))
            if sp.scalars().all():
                availability_bonus = 20.0
        scored.append({
            "product_id": p.product_id,
            "product_name": p.product_name,
            "brand": p.brand,
            "image_url": img_map.get(p.product_id),
            "_score": base + availability_bonus,
        })
    scored.sort(key=lambda x: x["_score"], reverse=True)
    return [{k: v for k, v in d.items() if k != "_score"} for d in scored[:limit]]
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.db.session import get_session
from app.core.auth import get_current_owner
from app.models import Product, ShopProduct, Shop, ShopAddress, ProductImage, Log, ProductCreate, ProductRead
from app.core.imagekit import ImageKitClient
from sqlalchemy.exc import IntegrityError


router = APIRouter()


@router.post("/", response_model=ProductRead)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_session), owner=Depends(get_current_owner)):
    name = (payload.product_name or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="Product name is required")
    cat_key = str(payload.category_id) if payload.category_id is not None else None
    try:
        prow = (await db.execute(text(
            "INSERT INTO Products (product_id, product_name, category_key, brand, description, color, created_at) "
            "VALUES (randomblob(16), :name, :cat_key, :brand, :desc, :color, CURRENT_TIMESTAMP) "
            "RETURNING product_id, product_name, category_key, brand, description, color"
        ), {"name": name, "cat_key": cat_key, "brand": payload.brand, "desc": payload.description, "color": payload.color})).first()
        if not prow:
            raise HTTPException(status_code=500, detail="Failed to create product")
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Product already exists")
    pid, pname, pcat, pbrand, pdesc, pcolor = prow
    return {
        "product_id": (pid.hex() if isinstance(pid, (bytes, bytearray)) else pid),
        "product_name": pname,
        "brand": pbrand,
        "description": pdesc,
        "color": pcolor,
        "category_id": pcat,
    }


@router.get("/")
async def list_products(db: AsyncSession = Depends(get_session)):
    res = await db.execute(text(
        "SELECT product_id, product_name, brand, description, color FROM Products ORDER BY created_at DESC"
    ))
    rows = res.all()
    items = []
    for pid, pname, pbrand, pdesc, pcolor in rows:
        items.append({
            "product_id": (pid.hex() if isinstance(pid, (bytes, bytearray)) else pid),
            "product_name": pname,
            "brand": pbrand,
            "description": pdesc,
            "color": pcolor,
            "category_id": None,
        })
    return items


# ProductPrice endpoints removed to comply strictly with db.txt

@router.get("/id/{product_id}")
async def product_detail(product_id: str, db: AsyncSession = Depends(get_session)):
    pid_bytes = None
    pid_int = None
    try:
        pid_bytes = bytes.fromhex(product_id)
    except ValueError:
        try:
            pid_int = int(product_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid product id format")
    if pid_bytes is not None:
        from sqlalchemy import text
        row = (await db.execute(text(
            "SELECT product_id, product_name, brand, color, description "
            "FROM Products WHERE product_id = :pid"
        ), {"pid": pid_bytes})).first()
        if not row:
            raise HTTPException(status_code=404, detail="Product not found")
        img = await db.execute(select(ProductImage).where(ProductImage.product_id == pid_bytes))
        image_url = None
        first = img.scalars().first()
        if first:
            image_url = first.image_url
        return {
            "product_id": product_id,
            "product_name": row[1],
            "brand": row[2],
            "color": row[3],
            "description": row[4],
            "image_url": image_url,
        }
    # integer fallback
    res = await db.execute(select(Product).where(Product.product_id == pid_int))
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    img = await db.execute(select(ProductImage).where(ProductImage.product_id == pid_int))
    image_url = None
    first = img.scalars().first()
    if first:
        image_url = first.image_url
    return {
        "product_id": product.product_id,
        "product_name": product.product_name,
        "brand": product.brand,
        "color": product.color,
        "description": product.description,
        "image_url": image_url,
    }

@router.get("/{product_id}")
async def product_detail_alias(product_id: str, db: AsyncSession = Depends(get_session)):
    return await product_detail(product_id, db)


@router.post("/{product_id}/image")
async def upload_product_image(
    product_id: int,
    file: UploadFile | None = File(default=None),
    file_url: str | None = Form(default=None),
    file_name: str | None = Form(default=None),
    db: AsyncSession = Depends(get_session),
    request: Request = None,
):
    # verify product exists
    res = await db.execute(select(Product).where(Product.product_id == product_id))
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    # Log attempted upload and reject
    try:
        db.add(Log(
            user_id=None,
            action_type="image_upload_attempt",
            description="uploads_disabled",
            ip_address=(request.client.host if request and request.client else None),
            status_code=403,
        ))
        await db.commit()
    except Exception:
        # Non-blocking: logging should not prevent response
        pass
    raise HTTPException(status_code=403, detail="Image uploads are currently disabled")


@router.post("/create_with_image")
async def create_product_with_image(
    product_name: str = Form(...),
    category_id: int | None = Form(default=None),
    brand: str | None = Form(default=None),
    description: str | None = Form(default=None),
    color: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    file_url: str | None = Form(default=None),
    db: AsyncSession = Depends(get_session),
    request: Request = None,
):
    # create product
    product = Product(product_name=product_name, category_id=category_id, brand=brand, description=description, color=color)
    db.add(product)
    await db.flush()

    # Reject any image upload attempts
    if file or file_url:
        try:
            db.add(Log(
                user_id=None,
                action_type="image_upload_attempt",
                description="uploads_disabled",
                ip_address=(request.client.host if request and request.client else None),
                status_code=403,
            ))
            await db.commit()
        except Exception:
            pass
        raise HTTPException(status_code=403, detail="Image uploads are currently disabled")

    await db.commit()
    await db.refresh(product)
    return {"product_id": product.product_id, "product_name": product.product_name, "image_url": None}


@router.get("/in_city")
async def products_in_city(city: str, db: AsyncSession = Depends(get_session)):
    # Products available (via ShopProduct) in shops located in the given city
    # Prefer Shops.city; fall back to Shop_Address.city when Shops.city is NULL; require available stock
    from app.models.shop import Shop, ShopAddress
    from sqlalchemy import or_
    stmt = (
        select(Product, ShopProduct, Shop, ShopAddress)
        .join(ShopProduct, ShopProduct.product_id == Product.product_id)
        .join(Shop, Shop.shop_id == ShopProduct.shop_id)
        .join(ShopAddress, ShopAddress.shop_id == ShopProduct.shop_id, isouter=True)
        .where(or_(Shop.city.ilike(f"%{city}%"), ShopAddress.city.ilike(f"%{city}%")))
        .where((ShopProduct.stock.is_not(None)) & (ShopProduct.stock > 0))
    )
    res = await db.execute(stmt)
    rows = res.all()
    out = []
    for p, sp, s, addr in rows:
        pid = p.product_id
        if isinstance(pid, (bytes, bytearray)):
            pid = pid.hex()
        out.append({
            "product_id": pid,
            "product_name": p.product_name,
            "brand": p.brand,
            "price": float(sp.price) if sp.price is not None else None,
            "stock": sp.stock,
            "city": getattr(addr, "city", None),
        })
    # deduplicate by product_id keeping the lowest price
    dedup: dict[int, dict] = {}
    for item in out:
        pid = item["product_id"]
        if pid not in dedup or (
            (item["price"] is not None and (dedup[pid]["price"] is None or item["price"] < dedup[pid]["price"]))
        ):
            dedup[pid] = item
    return list(dedup.values())


@router.get("/{product_id}/prices")
async def product_prices(product_id: str, db: AsyncSession = Depends(get_session)):
    pid_bytes = None
    pid_int = None
    try:
        pid_bytes = bytes.fromhex(product_id)
    except ValueError:
        try:
            pid_int = int(product_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid product id format")
    if pid_bytes is not None:
        from sqlalchemy import text
        rows = (await db.execute(text(
            "SELECT sp.shop_id, s.shop_name, sp.price, sp.stock "
            "FROM Shop_Product sp JOIN Shops s ON sp.shop_id = s.shop_id "
            "WHERE sp.product_id = :pid"
        ), {"pid": pid_bytes})).all()
        out = []
        for sid, sname, price, stock in rows:
            out.append({
                "shop_id": (sid.hex() if isinstance(sid, (bytes, bytearray)) else sid),
                "shop_name": sname,
                "price": float(price) if price is not None else None,
                "stock": stock,
            })
        return sorted(out, key=lambda x: (x["price"] is None, x["price"] or 0.0))
    # integer fallback
    stmt = (
        select(ShopProduct, Shop, ShopAddress)
        .join(Shop, Shop.shop_id == ShopProduct.shop_id)
        .join(ShopAddress, ShopAddress.shop_id == ShopProduct.shop_id, isouter=True)
        .where(ShopProduct.product_id == pid_int)
    )
    res = await db.execute(stmt)
    rows = res.all()
    out = []
    for sp, s, addr in rows:
        out.append({
            "shop_id": s.shop_id,
            "shop_name": s.shop_name,
            "price": float(sp.price) if sp.price is not None else None,
            "stock": sp.stock,
            "city": getattr(addr, "city", None),
            "area": getattr(addr, "area", None),
            "shop_image": s.shop_image,
        })
    return sorted(out, key=lambda x: (x["price"] is None, x["price"] or 0.0))

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.core.auth import get_current_owner
from app.models import Product, ShopProduct, Shop, ProductImage, AuthLog
from app.core.imagekit import ImageKitClient
from app.schemas.product import ProductCreate, ProductRead
from app.schemas.shop import ShopPrice


router = APIRouter()


@router.post("/", response_model=ProductRead)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_session), owner=Depends(get_current_owner)):
    product = Product(
        product_name=payload.product_name,
        category_id=payload.category_id,
        brand=payload.brand,
        description=payload.description,
        color=payload.color,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/", response_model=list[ProductRead])
async def list_products(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Product))
    return res.scalars().all()


@router.get("/{product_id}/prices", response_model=list[ShopPrice])
async def price_comparison(product_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    res = await db.execute(
        select(ShopProduct, Shop).join(Shop, Shop.shop_id == ShopProduct.shop_id).where(ShopProduct.product_id == product_id)
    )
    rows = res.all()
    output = [
        ShopPrice(shop_id=s.Shop.shop_id, shop_name=s.Shop.shop_name, price=float(s.ShopProduct.price) if s.ShopProduct.price else None, stock=s.ShopProduct.stock)
        for s in [type("Row", (), {"ShopProduct": r[0], "Shop": r[1]}) for r in rows]
    ]
    # Sort by price ascending, treating None as high
    output.sort(key=lambda x: (x.price is None, x.price))
    return output

@router.get("/{product_id}")
async def product_detail(product_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Product).where(Product.product_id == product_id))
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    img = await db.execute(select(ProductImage).where(ProductImage.product_id == product_id))
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


@router.post("/{product_id}/image")
async def upload_product_image(
    product_id: uuid.UUID,
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
        db.add(AuthLog(
            principal_type="user",
            principal_id=None,
            event_type="image_upload_attempt",
            success=False,
            reason="uploads_disabled",
            ip=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None,
        ))
        await db.commit()
    except Exception:
        # Non-blocking: logging should not prevent response
        pass
    raise HTTPException(status_code=403, detail="Image uploads are currently disabled")


@router.post("/create_with_image")
async def create_product_with_image(
    product_name: str = Form(...),
    category_id: uuid.UUID | None = Form(default=None),
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
            db.add(AuthLog(
                principal_type="user",
                principal_id=None,
                event_type="image_upload_attempt",
                success=False,
                reason="uploads_disabled",
                ip=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None,
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
    # Case-insensitive, partial city match; require stock > 0
    from app.models.shop import ShopAddress
    stmt = (
        select(Product, ShopProduct, ShopAddress)
        .join(ShopProduct, ShopProduct.product_id == Product.product_id)
        .join(ShopAddress, ShopAddress.shop_id == ShopProduct.shop_id)
        .where(ShopAddress.city.ilike(f"%{city}%"))
        .where(ShopProduct.stock.isnot(None))
        .where(ShopProduct.stock > 0)
    )
    res = await db.execute(stmt)
    rows = res.all()
    out = []
    for p, sp, addr in rows:
        out.append({
            "product_id": p.product_id,
            "product_name": p.product_name,
            "brand": p.brand,
            "price": float(sp.price) if sp.price is not None else None,
            "stock": sp.stock,
            "city": addr.city,
        })
    # deduplicate by product_id keeping the lowest price
    dedup: dict[uuid.UUID, dict] = {}
    for item in out:
        pid = item["product_id"]
        if pid not in dedup or (
            (item["price"] is not None and (dedup[pid]["price"] is None or item["price"] < dedup[pid]["price"]))
        ):
            dedup[pid] = item
    return list(dedup.values())
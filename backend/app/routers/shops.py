from math import radians, sin, cos, sqrt, atan2
import uuid
import os
import time
from collections import deque
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.core.auth import get_current_owner, ensure_owner_of_shop
from app.models import Shop, ShopAddress, ShopProduct, Product, ShopOwner, ProductImage, AuthLog, OwnerSecurity
from app.core.imagekit import ImageKitClient
from app.schemas.shop import ShopCreate, ShopRead, ShopRegister, ShopProductAdd
from app.routers.realtime import notify_shop_update
from sqlalchemy import update
from app.core.security import get_password_hash
from datetime import datetime


router = APIRouter()


# Simple in-memory rate limiter per owner: max 5 uploads per minute
_UPLOAD_WINDOW_SECONDS = 60
_UPLOAD_MAX_REQUESTS = 5
_owner_upload_events: dict[str, deque] = {}

# Storage directory for shop images (not publicly served by default)
_SHOP_IMAGES_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media", "shop_images")
os.makedirs(_SHOP_IMAGES_ROOT, exist_ok=True)


def _rate_limit_check(owner_id: uuid.UUID) -> bool:
    now = time.time()
    key = str(owner_id)
    dq = _owner_upload_events.setdefault(key, deque())
    # prune old events
    while dq and (now - dq[0]) > _UPLOAD_WINDOW_SECONDS:
        dq.popleft()
    if len(dq) >= _UPLOAD_MAX_REQUESTS:
        return False
    dq.append(now)
    return True


def _detect_image_magic(header: bytes) -> str | None:
    # Return one of 'jpg','png','webp' or None
    if len(header) >= 3 and header[0:3] == b"\xFF\xD8\xFF":
        return "jpg"
    if len(header) >= 8 and header[0:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if len(header) >= 12 and header[0:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "webp"
    return None


def _content_type_to_ext(content_type: str) -> str | None:
    mapping = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }
    return mapping.get(content_type)


@router.post("/", response_model=ShopRead)
async def create_shop(payload: ShopCreate, db: AsyncSession = Depends(get_session)):
    # Ensure GSTIN is unique if provided
    if payload.gstin:
        existing = await db.execute(select(Shop).where(Shop.gstin == payload.gstin))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Shop with this GSTIN already exists")
    shop = Shop(shop_name=payload.shop_name, owner_id=payload.owner_id, shop_image=payload.shop_image, gstin=payload.gstin)
    db.add(shop)
    await db.commit()
    await db.refresh(shop)
    return shop


@router.post("/register", response_model=ShopRead)
async def register_shop(payload: ShopRegister, db: AsyncSession = Depends(get_session)):
    # Validate GSTIN uniqueness
    if payload.gstin:
        existing = await db.execute(select(Shop).where(Shop.gstin == payload.gstin))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Shop with this GSTIN already exists")

    # Create or find owner by email/phone
    owner_id = None
    if payload.owner_email or payload.owner_phone:
        q = await db.execute(
            select(ShopOwner).where(
                ((ShopOwner.email == payload.owner_email) if payload.owner_email else False) |
                ((ShopOwner.phone == payload.owner_phone) if payload.owner_phone else False)
            )
        )
        owner = q.scalar_one_or_none()
        if not owner:
            owner = ShopOwner(owner_name=payload.owner_name, phone=payload.owner_phone, email=payload.owner_email)
            db.add(owner)
            await db.flush()  # get owner_id
            # If password provided, set it for newly created owner
            if payload.owner_password:
                owner.password_hash = get_password_hash(payload.owner_password)
            # Create OwnerSecurity and auto-verify for immediate login
            db.add(OwnerSecurity(
                owner_id=owner.owner_id,
                email_verified_at=datetime.utcnow(),
                phone_verified_at=datetime.utcnow(),
            ))
        else:
            # If existing owner without password and one is provided, set it
            if payload.owner_password and not owner.password_hash:
                owner.password_hash = get_password_hash(payload.owner_password)
            # Ensure OwnerSecurity exists and mark verified for immediate login
            sec = (await db.execute(select(OwnerSecurity).where(OwnerSecurity.owner_id == owner.owner_id))).scalar_one_or_none()
            if not sec:
                db.add(OwnerSecurity(
                    owner_id=owner.owner_id,
                    email_verified_at=datetime.utcnow(),
                    phone_verified_at=datetime.utcnow(),
                ))
            else:
                sec.email_verified_at = datetime.utcnow()
                sec.phone_verified_at = datetime.utcnow()
        owner_id = owner.owner_id

    # Create shop
    shop = Shop(shop_name=payload.shop_name, owner_id=owner_id, shop_image=payload.shop_image, gstin=payload.gstin)
    db.add(shop)
    await db.flush()  # obtain shop_id

    # Optional address
    if any([payload.city, payload.country, payload.pincode, payload.landmark, payload.area, payload.latitude, payload.longitude]):
        addr = ShopAddress(
            shop_id=shop.shop_id,
            city=payload.city,
            country=payload.country,
            pincode=payload.pincode,
            landmark=payload.landmark,
            area=payload.area,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        db.add(addr)

    await db.commit()
    await db.refresh(shop)
    return shop


@router.get("/", response_model=list[ShopRead])
async def list_shops(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Shop))
    return res.scalars().all()


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


@router.get("/nearby")
async def nearby_shops(lat: float, lon: float, radius_km: float = 5.0, db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Shop, ShopAddress).join(ShopAddress, ShopAddress.shop_id == Shop.shop_id))
    rows = res.all()
    out = []
    for shop, addr in rows:
        if addr.latitude is None or addr.longitude is None:
            continue
        distance = haversine(float(addr.latitude), float(addr.longitude), lat, lon)
        if distance <= radius_km:
            out.append({
                "shop_id": shop.shop_id,
                "shop_name": shop.shop_name,
                "distance_km": round(distance, 2),
                "city": addr.city,
                "area": addr.area,
                "shop_image": shop.shop_image,
            })
    return sorted(out, key=lambda x: x["distance_km"])


@router.get("/by_city")
async def shops_by_city(city: str, db: AsyncSession = Depends(get_session)):
    res = await db.execute(
        select(Shop, ShopAddress).join(ShopAddress, ShopAddress.shop_id == Shop.shop_id)
    )
    rows = res.all()
    city_lower = city.lower()
    out = []
    for shop, addr in rows:
        if (addr.city or "").lower().strip() == city_lower.strip():
            out.append({
                "shop_id": shop.shop_id,
                "shop_name": shop.shop_name,
                "city": addr.city,
                "area": addr.area,
                "shop_image": shop.shop_image,
            })
    return out


@router.get("/{shop_id}/availability")
async def shop_availability(shop_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Shop).where(Shop.shop_id == shop_id))
    shop = res.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    # Eagerly load timings
    await db.refresh(shop)
    return {"shop_id": shop.shop_id, "shop_name": shop.shop_name, "is_open": shop.is_open()}


@router.get("/{shop_id}/products")
async def shop_products(shop_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    res = await db.execute(
        select(ShopProduct, Product).join(Product, Product.product_id == ShopProduct.product_id).where(ShopProduct.shop_id == shop_id)
    )
    rows = res.all()
    product_ids = [p.product_id for _, p in rows]
    img_map = {}
    if product_ids:
        from app.models import ProductImage
        imgs = await db.execute(select(ProductImage).where(ProductImage.product_id.in_(product_ids)))
        for img in imgs.scalars().all():
            img_map.setdefault(img.product_id, img.image_url)
    return [
        {
            "product_id": p.product_id,
            "product_name": p.product_name,
            "price": float(sp.price) if sp.price is not None else None,
            "stock": sp.stock,
            "image_url": img_map.get(p.product_id),
        }
        for sp, p in rows
    ]


@router.post("/{shop_id}/products")
async def add_product_to_shop(
    shop_id: uuid.UUID,
    payload: ShopProductAdd,
    db: AsyncSession = Depends(get_session),
    owner=Depends(get_current_owner),
):
    await ensure_owner_of_shop(shop_id, owner, db)
    # Validate shop exists
    shop_res = await db.execute(select(Shop).where(Shop.shop_id == shop_id))
    if not shop_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Shop not found")
    # Validate product exists
    prod_res = await db.execute(select(Product).where(Product.product_id == payload.product_id))
    if not prod_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")
    # Upsert shop-product entry
    existing = await db.execute(
        select(ShopProduct).where((ShopProduct.shop_id == shop_id) & (ShopProduct.product_id == payload.product_id))
    )
    sp = existing.scalar_one_or_none()
    if sp:
        sp.price = payload.price
        sp.stock = payload.stock
    else:
        sp = ShopProduct(shop_id=shop_id, product_id=payload.product_id, price=payload.price, stock=payload.stock)
        db.add(sp)
    await db.commit()
    return {"shop_id": shop_id, "product_id": payload.product_id, "price": payload.price, "stock": payload.stock}


@router.delete("/{shop_id}/products/{product_id}")
async def delete_product_from_shop(
    shop_id: uuid.UUID,
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    owner=Depends(get_current_owner),
):
    # Ensure the requester owns the shop
    await ensure_owner_of_shop(shop_id, owner, db)

    # Check if mapping exists
    existing = await db.execute(
        select(ShopProduct).where((ShopProduct.shop_id == shop_id) & (ShopProduct.product_id == product_id))
    )
    sp = existing.scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="Product not linked to this shop")

    # Delete the mapping
    await db.delete(sp)
    await db.commit()
    # Notify realtime subscribers (if any) that shop inventory changed
    try:
        await notify_shop_update(shop_id, {
            "event": "product_removed",
            "shop_id": str(shop_id),
            "product_id": str(product_id),
        })
    except Exception:
        # Non-blocking: ignore realtime errors
        pass
    return {"ok": True}


@router.post("/{shop_id}/products/create")
async def create_product_for_shop(
    shop_id: uuid.UUID,
    product_name: str = Form(...),
    category_id: uuid.UUID | None = Form(default=None),
    brand: str | None = Form(default=None),
    description: str | None = Form(default=None),
    color: str | None = Form(default=None),
    price: float | None = Form(default=None),
    stock: int | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    file_url: str | None = Form(default=None),
    db: AsyncSession = Depends(get_session),
    owner=Depends(get_current_owner),
):
    await ensure_owner_of_shop(shop_id, owner, db)
    # Validate shop exists
    shop_res = await db.execute(select(Shop).where(Shop.shop_id == shop_id))
    if not shop_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Shop not found")

    # Create product
    product = Product(product_name=product_name, category_id=category_id, brand=brand, description=description, color=color)
    db.add(product)
    await db.flush()

    # Image handling policy: accept local file upload and store via ImageKit
    image_url = None
    if file_url:
        raise HTTPException(status_code=400, detail="Only local file upload is allowed for product images")

    if file is not None:
        # Validate content type
        if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
            try:
                db.add(AuthLog(
                    principal_type="owner",
                    principal_id=str(owner.owner_id),
                    event_type="image_upload_attempt",
                    success=False,
                    reason="invalid_type",
                ))
                await db.commit()
            except Exception:
                pass
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, WEBP are allowed.")

        # Read and size enforcement (2MB)
        MAX_BYTES = 2 * 1024 * 1024
        total = 0
        chunks: list[bytes] = []
        while True:
            chunk = await file.read(64 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_BYTES:
                try:
                    db.add(AuthLog(
                        principal_type="owner",
                        principal_id=str(owner.owner_id),
                        event_type="image_upload_attempt",
                        success=False,
                        reason="too_large",
                    ))
                    await db.commit()
                except Exception:
                    pass
                raise HTTPException(status_code=413, detail="File too large. Maximum size is 2MB.")
            chunks.append(chunk)

        data = b"".join(chunks)
        header = data[:12]

        # Magic header validation and extension determination
        magic_ext = _detect_image_magic(header)
        if not magic_ext:
            try:
                db.add(AuthLog(
                    principal_type="owner",
                    principal_id=str(owner.owner_id),
                    event_type="image_upload_attempt",
                    success=False,
                    reason="invalid_magic",
                ))
                await db.commit()
            except Exception:
                pass
            raise HTTPException(status_code=400, detail="Invalid image content detected.")

        ct_ext = _content_type_to_ext(file.content_type)
        if not ct_ext or ct_ext != magic_ext:
            try:
                db.add(AuthLog(
                    principal_type="owner",
                    principal_id=str(owner.owner_id),
                    event_type="image_upload_attempt",
                    success=False,
                    reason="type_magic_mismatch",
                ))
                await db.commit()
            except Exception:
                pass
            raise HTTPException(status_code=400, detail="File type does not match content.")

        # Upload to ImageKit
        client = ImageKitClient()
        if not client.is_configured():
            raise HTTPException(status_code=500, detail="ImageKit is not configured. Set IMAGEKIT_* keys in environment.")

        import uuid as _uuid
        fname = f"{_uuid.uuid4().hex}.{magic_ext}"
        try:
            result = client.upload(file_bytes=data, file_name=fname)
        except Exception:
            try:
                db.add(AuthLog(
                    principal_type="owner",
                    principal_id=str(owner.owner_id),
                    event_type="image_upload",
                    success=False,
                    reason="imagekit_error",
                ))
                await db.commit()
            except Exception:
                pass
            raise HTTPException(status_code=502, detail="Failed to upload to ImageKit.")

        image_url = result.get("url") or result.get("filePath")
        if not image_url:
            raise HTTPException(status_code=502, detail="ImageKit did not return a URL.")

        # Persist ProductImage mapping
        from app.models import ProductImage
        db.add(ProductImage(product_id=product.product_id, image_url=image_url))

    # Link product to shop with price/stock
    sp = ShopProduct(shop_id=shop_id, product_id=product.product_id, price=price, stock=stock)
    db.add(sp)

    await db.commit()
    return {
        "shop_id": shop_id,
        "product_id": product.product_id,
        "product_name": product.product_name,
        "price": price,
        "stock": stock,
        "image_url": image_url,
    }


@router.post("/{shop_id}/images/upload")
async def upload_shop_image(
    shop_id: uuid.UUID,
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    owner: ShopOwner = Depends(get_current_owner),
):
    # Access Control: owner must own the shop
    await ensure_owner_of_shop(shop_id, owner, db)

    # Rate limiting
    if not _rate_limit_check(owner.owner_id):
        try:
            db.add(AuthLog(
                principal_type="owner",
                principal_id=str(owner.owner_id),
                event_type="image_upload_attempt",
                success=False,
                reason="rate_limited",
                ip=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None,
            ))
            await db.commit()
        except Exception:
            pass
        raise HTTPException(status_code=429, detail="Too many upload attempts. Please try again later.")

    # Content type validation
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        try:
            db.add(AuthLog(
                principal_type="owner",
                principal_id=str(owner.owner_id),
                event_type="image_upload_attempt",
                success=False,
                reason="invalid_type",
                ip=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None,
            ))
            await db.commit()
        except Exception:
            pass
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, WEBP are allowed.")

    # Read and size enforcement (2MB)
    MAX_BYTES = 2 * 1024 * 1024
    total = 0
    chunks: list[bytes] = []
    while True:
        chunk = await file.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_BYTES:
            try:
                db.add(AuthLog(
                    principal_type="owner",
                    principal_id=str(owner.owner_id),
                    event_type="image_upload_attempt",
                    success=False,
                    reason="too_large",
                    ip=request.client.host if request and request.client else None,
                    user_agent=request.headers.get("user-agent") if request else None,
                ))
                await db.commit()
            except Exception:
                pass
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 2MB.")
        chunks.append(chunk)

    data = b"".join(chunks)
    header = data[:12]

    # Magic header validation and extension determination
    magic_ext = _detect_image_magic(header)
    if not magic_ext:
        try:
            db.add(AuthLog(
                principal_type="owner",
                principal_id=str(owner.owner_id),
                event_type="image_upload_attempt",
                success=False,
                reason="invalid_magic",
                ip=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None,
            ))
            await db.commit()
        except Exception:
            pass
        raise HTTPException(status_code=400, detail="Invalid image content detected.")

    ct_ext = _content_type_to_ext(file.content_type)
    if not ct_ext or ct_ext != magic_ext:
        try:
            db.add(AuthLog(
                principal_type="owner",
                principal_id=str(owner.owner_id),
                event_type="image_upload_attempt",
                success=False,
                reason="type_magic_mismatch",
                ip=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None,
            ))
            await db.commit()
        except Exception:
            pass
        raise HTTPException(status_code=400, detail="File type does not match content.")

    # Upload to ImageKit (publicly served)
    client = ImageKitClient()
    if not client.is_configured():
        raise HTTPException(status_code=500, detail="ImageKit is not configured. Set IMAGEKIT_* keys in environment.")

    fname = f"{uuid.uuid4().hex}.{magic_ext}"
    try:
        result = client.upload(file_bytes=data, file_name=fname)
    except Exception:
        try:
            db.add(AuthLog(
                principal_type="owner",
                principal_id=str(owner.owner_id),
                event_type="image_upload",
                success=False,
                reason="imagekit_error",
                ip=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None,
            ))
            await db.commit()
        except Exception:
            pass
        raise HTTPException(status_code=502, detail="Failed to upload to ImageKit.")

    image_url = result.get("url") or result.get("filePath")
    if not image_url:
        raise HTTPException(status_code=502, detail="ImageKit did not return a URL.")

    # Persist on Shop
    res = await db.execute(select(Shop).where(Shop.shop_id == shop_id))
    shop = res.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    shop.shop_image = image_url
    await db.commit()

    # Audit log: success
    try:
        db.add(AuthLog(
            principal_type="owner",
            principal_id=str(owner.owner_id),
            event_type="image_upload",
            success=True,
            reason="ok",
            ip=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None,
        ))
        await db.commit()
    except Exception:
        pass

    return {
        "shop_id": str(shop_id),
        "file_name": fname,
        "image_url": image_url,
        "size_bytes": total,
        "content_type": file.content_type,
    }

@router.get("/{shop_id}")
async def shop_detail(shop_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    from app.models.shop import ShopTiming
    res = await db.execute(select(Shop, ShopAddress).join(ShopAddress, ShopAddress.shop_id == Shop.shop_id, isouter=True).where(Shop.shop_id == shop_id))
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Shop not found")
    shop, addr = row
    timings_q = await db.execute(select(ShopTiming).where(ShopTiming.shop_id == shop_id))
    timings = [
        {
            "day": t.day,
            "opens_at": t.open_time,
            "closes_at": t.close_time,
        }
        for t in timings_q.scalars().all()
    ]
    return {
        "shop_id": shop.shop_id,
        "shop_name": shop.shop_name,
        "shop_image": shop.shop_image,
        "city": getattr(addr, "city", None),
        "area": getattr(addr, "area", None),
        "landmark": getattr(addr, "landmark", None),
        "pincode": getattr(addr, "pincode", None),
        "is_open": shop.is_open(),
        "timings": timings,
    }
@router.patch("/{shop_id}/availability")
async def update_availability(shop_id: uuid.UUID, is_available: bool, owner: ShopOwner = Depends(get_current_owner), db: AsyncSession = Depends(get_session)):
    await ensure_owner_of_shop(shop_id, owner, db)
    stmt = update(Shop).where(Shop.shop_id == shop_id).values(shop_image=Shop.shop_image)  # no-op to ensure row exists
    await db.execute(stmt)
    # For simplicity, broadcast only; actual persisted field can be added in a future migration
    await notify_shop_update(shop_id, {"is_available": is_available})
    return {"shop_id": str(shop_id), "is_available": is_available}
from math import radians, sin, cos, sqrt, atan2
import os
import time
from collections import deque
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Response, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
from app.db.session import get_session
from app.core.auth import get_current_owner, ensure_owner_of_shop
from app.core.config import settings
from app.models import Shop, ShopAddress, ShopProduct, Product, ShopOwner, ProductImage
from app.core.imagekit import ImageKitClient
from app.models.shop import ShopCreate, ShopRead, ShopRegister, ShopProductAdd, ShopInventoryUpdate
from app.routers.realtime import notify_shop_update
from sqlalchemy import update
from datetime import datetime


router = APIRouter()


# Simple in-memory rate limiter per owner: max 5 uploads per minute
_UPLOAD_WINDOW_SECONDS = 60
_UPLOAD_MAX_REQUESTS = 5
_owner_upload_events: dict[str, deque] = {}

# Storage directory for shop images (not publicly served by default)
_SHOP_IMAGES_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media", "shop_images")
os.makedirs(_SHOP_IMAGES_ROOT, exist_ok=True)


def _rate_limit_check(owner_id: int) -> bool:
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
    # db.txt: no GSTIN field; create with allowed columns only
    shop = Shop(shop_name=payload.shop_name, owner_id=payload.owner_id, shop_image=payload.shop_image)
    db.add(shop)
    await db.commit()
    await db.refresh(shop)
    return shop


@router.post("/register", response_model=ShopRead)
async def register_shop(payload: ShopRegister, db: AsyncSession = Depends(get_session)):
    # Password validation: required with strength and confirmation
    if not payload.owner_password or not payload.owner_password_confirm:
        raise HTTPException(status_code=422, detail="Password and confirmation are required")
    pw = payload.owner_password
    confirm = payload.owner_password_confirm
    import re
    if len(pw) < 8 or not re.search(r"[A-Z]", pw) or not re.search(r"\d", pw) or not re.search(r"[^A-Za-z0-9]", pw):
        raise HTTPException(status_code=422, detail="Password must be 8+ chars with uppercase, number, and special character")
    if pw != confirm:
        raise HTTPException(status_code=422, detail="Passwords do not match")

    # Create or find owner by email/phone
    owner_id = None
    owner = None
    if payload.owner_email or payload.owner_phone:
        q = await db.execute(
            select(ShopOwner).where(
                ((ShopOwner.email == payload.owner_email) if payload.owner_email else False) |
                ((ShopOwner.phone == payload.owner_phone) if payload.owner_phone else False)
            )
        )
        owner = q.scalar_one_or_none()
        if not owner:
            from app.core.security import get_password_hash
            await db.execute(
                text(
                    "INSERT INTO Shop_Owners (owner_id, owner_name, phone, email, password_hash, created_at) "
                    "VALUES (randomblob(16), :owner_name, :phone, :email, :password_hash, CURRENT_TIMESTAMP)"
                ),
                {
                    "owner_name": payload.owner_name,
                    "phone": payload.owner_phone,
                    "email": payload.owner_email,
                    "password_hash": get_password_hash(pw),
                },
            )
            q2 = await db.execute(select(ShopOwner).where(ShopOwner.email == payload.owner_email))
            owner = q2.scalar_one()
        else:
            from app.core.security import get_password_hash
            await db.execute(
                text("UPDATE Shop_Owners SET password_hash = :ph WHERE email = :email"),
                {"ph": get_password_hash(pw), "email": payload.owner_email},
            )
            # Fetch owner_id via raw SQL
            q3 = await db.execute(text("SELECT owner_id FROM Shop_Owners WHERE email = :email"), {"email": payload.owner_email})
            owner_row = q3.first()
            owner_id = owner_row[0] if owner_row else None
        if owner_id is None:
            # fallback: fetch by phone if email missing
            q4 = await db.execute(text("SELECT owner_id FROM Shop_Owners WHERE phone = :phone"), {"phone": payload.owner_phone})
            owner_row2 = q4.first()
            owner_id = owner_row2[0] if owner_row2 else owner_id

    # Ensure GSTIN uniqueness
    if payload.gstin:
        dup = (await db.execute(text("SELECT shop_id FROM Shops WHERE gstin = :gstin"), {"gstin": payload.gstin})).first()
        if dup:
            raise HTTPException(status_code=409, detail="GSTIN already registered")

    # Create shop via raw SQL to align with SQLite BLOB keys
    await db.execute(
        text(
            "INSERT INTO Shops (shop_id, shop_name, gstin, owner_id, shop_image, created_at, city, contact_number) "
            "VALUES (randomblob(16), :shop_name, :gstin, :owner_id, :shop_image, CURRENT_TIMESTAMP, :city, :contact_number)"
        ),
        {
            "shop_name": payload.shop_name,
            "gstin": getattr(payload, "gstin", None),
            "owner_id": owner_id,
            "shop_image": payload.shop_image,
            "city": payload.city,
            "contact_number": payload.owner_phone,
        },
    )
    q_shop = await db.execute(
        text(
            "SELECT shop_id, shop_name, shop_image FROM Shops WHERE owner_id = :owner_id AND shop_name = :shop_name ORDER BY created_at DESC LIMIT 1"
        ),
        {"owner_id": owner_id, "shop_name": payload.shop_name},
    )
    row = q_shop.first()

    # Optional address
    if row and any([payload.city, payload.country, payload.pincode, payload.landmark, payload.area, payload.latitude, payload.longitude]):
        await db.execute(
            text(
                "INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at) "
                "VALUES (randomblob(16), :shop_id, :city, :country, :pincode, :landmark, :area, :latitude, :longitude, CURRENT_TIMESTAMP)"
            ),
            {
                "shop_id": row[0],
                "city": payload.city,
                "country": payload.country,
                "pincode": payload.pincode,
                "landmark": payload.landmark,
                "area": payload.area,
                "latitude": payload.latitude,
                "longitude": payload.longitude,
            },
        )

    await db.commit()
    sid = row[0]
    if isinstance(sid, (bytes, bytearray)):
        sid = sid.hex()
    return {"shop_id": sid, "shop_name": row[1], "shop_image": row[2]}


@router.get("/")
async def list_shops(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Shop))
    items = []
    for s in res.scalars().all():
        sid = s.shop_id
        if isinstance(sid, (bytes, bytearray)):
            sid = sid.hex()
        items.append({
            "shop_id": sid,
            "shop_name": s.shop_name,
            "shop_image": s.shop_image,
        })
    return items


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


@router.get("/nearby")
async def nearby_shops(lat: float, lon: float, radius_km: float = 5.0, db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Shop, ShopAddress).join(ShopAddress, ShopAddress.shop_id == Shop.shop_id, isouter=True))
    rows = res.all()
    out = []
    for shop, addr in rows:
        if not addr or addr.latitude is None or addr.longitude is None:
            continue
        try:
            lat1 = float(addr.latitude)
            lon1 = float(addr.longitude)
        except Exception:
            # skip invalid coordinates
            continue
        distance = haversine(lat1, lon1, float(lat), float(lon))
        if distance <= radius_km:
            sid = shop.shop_id
            if isinstance(sid, (bytes, bytearray)):
                sid = sid.hex()
            out.append({
                "shop_id": sid,
                "shop_name": shop.shop_name,
                "distance_km": round(distance, 2),
                "city": addr.city,
                "area": addr.area,
                "shop_image": shop.shop_image,
                "lat": lat1,
                "lon": lon1,
            })
    return sorted(out, key=lambda x: x["distance_km"])


@router.get("/by_city")
async def shops_by_city(city: str, db: AsyncSession = Depends(get_session)):
    from sqlalchemy import text
    norm = city.strip()
    try:
        rows = (await db.execute(
            text("SELECT shop_id, shop_name, city, shop_image FROM Shops WHERE LOWER(city) = LOWER(:city)"),
            {"city": norm},
        )).all()
    except Exception:
        import logging
        logging.exception("shops_by_city query failed for city=%r", norm)
        rows = []
    out = []
    for sid, name, c, img in rows:
        sid_out = sid.hex() if isinstance(sid, (bytes, bytearray)) else sid
        out.append({
            "shop_id": sid_out,
            "shop_name": name,
            "city": c,
            "shop_image": img,
        })
    return out


@router.get("/{shop_id}/availability")
async def shop_availability(shop_id: int, db: AsyncSession = Depends(get_session)):
    stmt = select(Shop).where(Shop.shop_id == shop_id).options(selectinload(Shop.timings))
    res = await db.execute(stmt)
    shop = res.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    # Timings are eagerly loaded above; compute open status safely
    return {"shop_id": shop.shop_id, "shop_name": shop.shop_name, "is_open": shop.is_open()}


@router.get("/owner/products")
async def owner_products_hex(db: AsyncSession = Depends(get_session), owner=Depends(get_current_owner), request: Request = None, response: Response = None):
    oid_hex = owner.get("owner_id")
    oid_bytes = bytes.fromhex(oid_hex) if isinstance(oid_hex, str) else oid_hex
    rows = (await db.execute(text(
        "SELECT sp.shop_product_id, s.shop_id, s.shop_name, p.product_id, p.product_name, p.brand, sp.price, sp.stock "
        "FROM Shop_Product sp JOIN Shops s ON sp.shop_id = s.shop_id JOIN Products p ON sp.product_id = p.product_id "
        "WHERE s.owner_id = :oid"
    ), {"oid": oid_bytes})).all()
    out = []
    for spid, sid, sname, pid, name, brand, price, stock in rows:
        out.append({
            "shop_product_id": (spid.hex() if isinstance(spid, (bytes, bytearray)) else spid),
            "shop_id": (sid.hex() if isinstance(sid, (bytes, bytearray)) else sid),
            "shop_name": sname,
            "product_id": (pid.hex() if isinstance(pid, (bytes, bytearray)) else pid),
            "product_name": name,
            "brand": brand,
            "price": float(price) if price is not None else None,
            "stock": stock,
        })
    try:
        origin = request.headers.get("origin") if request else None
        if origin and (origin in (settings.cors_origins or [])):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers.setdefault("Vary", "Origin")
    except Exception:
        pass
    return out

@router.get("/{shop_id}/products")
async def shop_products(shop_id: str = Path(..., pattern=r"^[0-9a-fA-F]{32}$"), db: AsyncSession = Depends(get_session)):
    sid_bytes = bytes.fromhex(shop_id)
    rows = (await db.execute(text(
        "SELECT sp.product_id, p.product_name, sp.price, sp.stock "
        "FROM Shop_Product sp JOIN Products p ON sp.product_id = p.product_id "
        "WHERE sp.shop_id = :sid"
    ), {"sid": sid_bytes})).all()
    out = []
    for pid, name, price, stock in rows:
        out.append({
            "product_id": (pid.hex() if isinstance(pid, (bytes, bytearray)) else pid),
            "product_name": name,
            "price": float(price) if price is not None else None,
            "stock": stock,
            "image_url": None,
        })
    return out


@router.post("/{shop_id}/products")
async def add_product_to_shop(
    shop_id: str,
    payload: ShopProductAdd,
    db: AsyncSession = Depends(get_session),
    owner=Depends(get_current_owner),
):
    try:
        sid_bytes = bytes.fromhex(shop_id)
    except ValueError:
        sid_bytes = None
    if sid_bytes is not None:
        oid_bytes = bytes.fromhex(owner.get("owner_id"))
        chk = (await db.execute(text("SELECT owner_id FROM Shops WHERE shop_id = :sid"), {"sid": sid_bytes})).first()
        if not chk or chk[0] != oid_bytes:
            raise HTTPException(status_code=403, detail="Not authorized for this shop")
        pid = payload.product_id
        pid_bytes = pid if isinstance(pid, (bytes, bytearray)) else (bytes.fromhex(str(pid)) if isinstance(pid, str) else None)
        if pid_bytes is None:
            raise HTTPException(status_code=422, detail="Invalid product ID")
        await db.execute(text(
            "INSERT INTO Shop_Product (shop_product_id, shop_id, product_id, price, stock, created_at) "
            "VALUES (randomblob(16), :sid, :pid, :price, :stock, CURRENT_TIMESTAMP) ON CONFLICT(shop_id, product_id) DO UPDATE SET price=:price, stock=:stock"
        ), {"sid": sid_bytes, "pid": pid_bytes, "price": payload.price, "stock": payload.stock})
        try:
            db.add(Log(user_id=None, action_type="shop_product_upsert", description=f"sid={shop_id}, pid={product_id}", status_code=200))
        except Exception:
            pass
        await db.commit()
        return {"shop_id": shop_id, "product_id": (pid.hex() if isinstance(pid, (bytes, bytearray)) else pid), "price": payload.price, "stock": payload.stock}
    # Fallback integer handling
    shop_id_int = int(shop_id)
    await ensure_owner_of_shop(shop_id_int, owner, db)
    prod_res = await db.execute(select(Product).where(Product.product_id == payload.product_id))
    if not prod_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")
    existing = await db.execute(
        select(ShopProduct).where((ShopProduct.shop_id == shop_id_int) & (ShopProduct.product_id == payload.product_id))
    )
    sp = existing.scalar_one_or_none()
    if sp:
        sp.price = payload.price
        sp.stock = payload.stock
    else:
        sp = ShopProduct(shop_id=shop_id_int, product_id=payload.product_id, price=payload.price, stock=payload.stock)
        db.add(sp)
    try:
        db.add(Log(user_id=None, action_type="shop_product_upsert", description=f"sid={shop_id_int}, pid={payload.product_id}", status_code=200))
    except Exception:
        pass
    await db.commit()
    return {"shop_id": shop_id_int, "product_id": payload.product_id, "price": payload.price, "stock": payload.stock}

@router.patch("/{shop_id}/products/{product_id}/inventory")
async def update_shop_product_inventory(
    shop_id: int,
    product_id: int,
    payload: ShopInventoryUpdate,
    db: AsyncSession = Depends(get_session),
    owner=Depends(get_current_owner),
):
    await ensure_owner_of_shop(shop_id, owner, db)
    existing = await db.execute(
        select(ShopProduct).where((ShopProduct.shop_id == shop_id) & (ShopProduct.product_id == product_id))
    )
    sp = existing.scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="Product not linked to this shop")
    if payload.price is not None:
        sp.price = payload.price
    if payload.stock is not None:
        sp.stock = payload.stock
    await db.commit()
    return {
        "shop_id": shop_id,
        "product_id": product_id,
        "price": float(sp.price) if sp.price is not None else None,
        "stock": sp.stock,
    }


@router.delete("/{shop_id}/products/{product_id}")
async def delete_product_from_shop(
    shop_id: str,
    product_id: str,
    db: AsyncSession = Depends(get_session),
    owner=Depends(get_current_owner),
):
    try:
        sid_bytes = bytes.fromhex(shop_id)
        pid_bytes = bytes.fromhex(product_id)
    except ValueError:
        sid_bytes = None
    if sid_bytes is not None:
        oid_bytes = bytes.fromhex(owner.get("owner_id"))
        chk = (await db.execute(text("SELECT owner_id FROM Shops WHERE shop_id = :sid"), {"sid": sid_bytes})).first()
        if not chk or chk[0] != oid_bytes:
            raise HTTPException(status_code=403, detail="Not authorized for this shop")
        await db.execute(text("DELETE FROM Shop_Product WHERE shop_id=:sid AND product_id=:pid"), {"sid": sid_bytes, "pid": pid_bytes})
        await db.commit()
        try:
            await notify_shop_update(shop_id, {"event": "product_removed", "shop_id": shop_id, "product_id": product_id})
        except Exception:
            pass
        return {"ok": True}
    # Fallback integer handling
    shop_id_int = int(shop_id)
    product_id_int = int(product_id)
    await ensure_owner_of_shop(shop_id_int, owner, db)
    existing = await db.execute(
        select(ShopProduct).where((ShopProduct.shop_id == shop_id_int) & (ShopProduct.product_id == product_id_int))
    )
    sp = existing.scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="Product not linked to this shop")
    await db.delete(sp)
    await db.commit()
    try:
        await notify_shop_update(shop_id_int, {"event": "product_removed", "shop_id": shop_id_int, "product_id": product_id_int})
    except Exception:
        pass
    return {"ok": True}


@router.post("/{shop_id}/products/create")
async def create_product_for_shop(
    shop_id: int,
    product_name: str = Form(...),
    category_id: int | None = Form(default=None),
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
    # Store category as string key
    cat_key = str(category_id) if category_id is not None else None
    # validate category key format if provided
    if cat_key is not None:
        import re
        if not re.fullmatch(r"[A-Za-z0-9_-]{2,40}", cat_key):
            raise HTTPException(status_code=422, detail="Invalid category ID format")
    product = Product(product_name=product_name, category_key=cat_key, brand=brand, description=description, color=color)
    db.add(product)
    await db.flush()

    # Image handling policy: accept local file upload and store via ImageKit
    image_url = None
    if file_url:
        raise HTTPException(status_code=400, detail="Only local file upload is allowed for product images")

    if file is not None:
        # Validate content type
        if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
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
                raise HTTPException(status_code=413, detail="File too large. Maximum size is 2MB.")
            chunks.append(chunk)

        data = b"".join(chunks)
        header = data[:12]

        # Magic header validation and extension determination
        magic_ext = _detect_image_magic(header)
        if not magic_ext:
            raise HTTPException(status_code=400, detail="Invalid image content detected.")

        ct_ext = _content_type_to_ext(file.content_type)
        if not ct_ext or ct_ext != magic_ext:
            raise HTTPException(status_code=400, detail="File type does not match content.")

        # Upload to ImageKit
        client = ImageKitClient()
        if not client.is_configured():
            raise HTTPException(status_code=500, detail="ImageKit is not configured. Set IMAGEKIT_* keys in environment.")

        fname = f"shopprod_{int(datetime.utcnow().timestamp())}.{magic_ext}"
        try:
            result = client.upload(file_bytes=data, file_name=fname)
        except Exception:
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

@router.post("/manage/{shop_id}/products/create")
async def create_product_for_shop_hex(
    shop_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_session),
    owner=Depends(get_current_owner),
):
    sid_bytes = bytes.fromhex(shop_id)
    oid_bytes = bytes.fromhex(owner.get("owner_id"))
    chk = (await db.execute(text("SELECT owner_id FROM Shops WHERE shop_id = :sid"), {"sid": sid_bytes})).first()
    if not chk or chk[0] != oid_bytes:
        raise HTTPException(status_code=403, detail="Not authorized for this shop")
    name = (payload.get("product_name") or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="Product name is required")
    prow = (await db.execute(text(
        "INSERT INTO Products (product_id, product_name, category_key, brand, description, color, created_at) "
        "VALUES (randomblob(16), :name, :cat_key, :brand, :desc, :color, CURRENT_TIMESTAMP) "
        "RETURNING product_id, product_name"
    ), {"name": name, "cat_key": (str(payload.get("category_id")) if payload.get("category_id") is not None else None), "brand": payload.get("brand"), "desc": payload.get("description"), "color": payload.get("color")})).first()
    if not prow:
        raise HTTPException(status_code=500, detail="Failed to create product")
    pid = prow[0]
    await db.execute(text(
        "INSERT INTO Shop_Product (shop_product_id, shop_id, product_id, price, stock, created_at) "
        "VALUES (randomblob(16), :sid, :pid, :price, :stock, CURRENT_TIMESTAMP)"
    ), {"sid": sid_bytes, "pid": pid, "price": payload.get("price"), "stock": payload.get("stock")})
    await db.commit()
    return {"product_id": (pid.hex() if isinstance(pid, (bytes, bytearray)) else pid), "product_name": prow[1], "shop_id": shop_id}


@router.post("/{shop_id}/images/upload")
async def upload_shop_image(
    shop_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    owner: ShopOwner = Depends(get_current_owner),
):
    # Access Control: owner must own the shop (hex-safe)
    try:
        sid_bytes = bytes.fromhex(shop_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid shop id format")
    from sqlalchemy import text
    row = (await db.execute(text("SELECT owner_id FROM Shops WHERE shop_id = :sid"), {"sid": sid_bytes})).first()
    if not row or (row[0] != owner.owner_id):
        raise HTTPException(status_code=403, detail="You are not the owner of this shop")

    # Rate limiting
    if not _rate_limit_check(owner.owner_id):
        raise HTTPException(status_code=429, detail="Too many upload attempts. Please try again later.")

    # Content type validation
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
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
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 2MB.")
        chunks.append(chunk)

    data = b"".join(chunks)
    header = data[:12]

    # Magic header validation and extension determination
    magic_ext = _detect_image_magic(header)
    if not magic_ext:
        raise HTTPException(status_code=400, detail="Invalid image content detected.")

    ct_ext = _content_type_to_ext(file.content_type)
    if not ct_ext or ct_ext != magic_ext:
        raise HTTPException(status_code=400, detail="File type does not match content.")

    # Upload to ImageKit (publicly served)
    client = ImageKitClient()
    if not client.is_configured():
        raise HTTPException(status_code=500, detail="ImageKit is not configured. Set IMAGEKIT_* keys in environment.")

    fname = f"shop_{int(datetime.utcnow().timestamp())}.{magic_ext}"
    try:
        result = client.upload(file_bytes=data, file_name=fname)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to upload to ImageKit.")

    image_url = result.get("url") or result.get("filePath")
    if not image_url:
        raise HTTPException(status_code=502, detail="ImageKit did not return a URL.")

    # Persist on Shop (hex-safe update)
    await db.execute(text("UPDATE Shops SET shop_image = :img WHERE shop_id = :sid"), {"img": image_url, "sid": sid_bytes})
    await db.commit()

    return {
        "shop_id": shop_id,
        "file_name": fname,
        "image_url": image_url,
        "size_bytes": total,
        "content_type": file.content_type,
    }

@router.get("/{shop_id}")
async def shop_detail(shop_id: str, db: AsyncSession = Depends(get_session)):
    try:
        sid_bytes = bytes.fromhex(shop_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid shop id format")
    row = (await db.execute(text(
        "SELECT s.shop_id, s.shop_name, s.shop_image, a.city, a.area, a.landmark, a.pincode "
        "FROM Shops s LEFT JOIN Shop_Address a ON a.shop_id = s.shop_id "
        "WHERE s.shop_id = :sid"
    ), {"sid": sid_bytes})).first()
    if not row:
        raise HTTPException(status_code=404, detail="Shop not found")
    sid, name, img, city, area, landmark, pincode = row
    return {
        "shop_id": (sid.hex() if isinstance(sid, (bytes, bytearray)) else sid),
        "shop_name": name,
        "shop_image": img,
        "city": city,
        "area": area,
        "landmark": landmark,
        "pincode": pincode,
        "is_open": False,
        "timings": [],
    }
@router.patch("/{shop_id}/availability")
async def update_availability(shop_id: int, is_available: bool, owner: ShopOwner = Depends(get_current_owner), db: AsyncSession = Depends(get_session)):
    await ensure_owner_of_shop(shop_id, owner, db)
    stmt = update(Shop).where(Shop.shop_id == shop_id).values(shop_image=Shop.shop_image)  # no-op to ensure row exists
    await db.execute(stmt)
    # For simplicity, broadcast only; actual persisted field can be added in a future migration
    await notify_shop_update(shop_id, {"is_available": is_available})
    return {"shop_id": shop_id, "is_available": is_available}
@router.get("/owner/products")
async def owner_products_hex(db: AsyncSession = Depends(get_session), owner=Depends(get_current_owner), request: Request = None, response: Response = None):
    oid_hex = owner.get("owner_id")
    oid_bytes = bytes.fromhex(oid_hex) if isinstance(oid_hex, str) else oid_hex
    rows = (await db.execute(text(
        "SELECT sp.shop_product_id, s.shop_id, p.product_id, p.product_name, p.brand, sp.price, sp.stock "
        "FROM Shop_Product sp JOIN Shops s ON sp.shop_id = s.shop_id JOIN Products p ON sp.product_id = p.product_id "
        "WHERE s.owner_id = :oid"
    ), {"oid": oid_bytes})).all()
    out = []
    for spid, sid, pid, name, brand, price, stock in rows:
        out.append({
            "shop_product_id": (spid.hex() if isinstance(spid, (bytes, bytearray)) else spid),
            "shop_id": (sid.hex() if isinstance(sid, (bytes, bytearray)) else sid),
            "product_id": (pid.hex() if isinstance(pid, (bytes, bytearray)) else pid),
            "product_name": name,
            "brand": brand,
            "price": float(price) if price is not None else None,
            "stock": stock,
        })
    try:
        origin = request.headers.get("origin") if request else None
        if origin and (origin in (settings.cors_origins or [])):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers.setdefault("Vary", "Origin")
    except Exception:
        pass
    return out

@router.put("/manage/{shop_id}/products/{product_id}")
async def update_shop_product_hex(shop_id: str, product_id: str, payload: dict, db: AsyncSession = Depends(get_session), owner=Depends(get_current_owner)):
    sid_bytes = bytes.fromhex(shop_id)
    pid_bytes = bytes.fromhex(product_id)
    oid_bytes = bytes.fromhex(owner.get("owner_id"))
    chk = (await db.execute(text("SELECT owner_id FROM Shops WHERE shop_id = :sid"), {"sid": sid_bytes})).first()
    if not chk or chk[0] != oid_bytes:
        raise HTTPException(status_code=403, detail="Not authorized for this shop")
    await db.execute(text("UPDATE Shop_Product SET price=:price, stock=:stock, updated_at=CURRENT_TIMESTAMP WHERE shop_id=:sid AND product_id=:pid"), {"price": payload.get("price"), "stock": payload.get("stock"), "sid": sid_bytes, "pid": pid_bytes})
    try:
        db.add(Log(user_id=None, action_type="shop_product_update", description=f"sid={shop_id}, pid={product_id}", status_code=200))
    except Exception:
        pass
    await db.commit()
    return {"ok": True}

@router.delete("/manage/{shop_id}/products/{product_id}")
async def delete_shop_product_hex(shop_id: str, product_id: str, db: AsyncSession = Depends(get_session), owner=Depends(get_current_owner)):
    sid_bytes = bytes.fromhex(shop_id)
    pid_bytes = bytes.fromhex(product_id)
    oid_bytes = bytes.fromhex(owner.get("owner_id"))
    chk = (await db.execute(text("SELECT owner_id FROM Shops WHERE shop_id = :sid"), {"sid": sid_bytes})).first()
    if not chk or chk[0] != oid_bytes:
        raise HTTPException(status_code=403, detail="Not authorized for this shop")
    await db.execute(text("DELETE FROM Shop_Product WHERE shop_id=:sid AND product_id=:pid"), {"sid": sid_bytes, "pid": pid_bytes})
    try:
        db.add(Log(user_id=None, action_type="shop_product_delete", description=f"sid={shop_id}, pid={product_id}", status_code=200))
    except Exception:
        pass
    await db.commit()
    return {"ok": True}

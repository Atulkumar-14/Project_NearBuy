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
    product_id: str,
    file: UploadFile | None = File(default=None),
    file_url: str | None = Form(default=None),
    file_name: str | None = Form(default=None),
    db: AsyncSession = Depends(get_session),
    request: Request = None,
):
    # verify product exists (hex or int)
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
        prow = (await db.execute(text("SELECT product_id FROM Products WHERE product_id = :pid"), {"pid": pid_bytes})).first()
        if not prow:
            raise HTTPException(status_code=404, detail="Product not found")
        product_key = pid_bytes
    else:
        res = await db.execute(select(Product).where(Product.product_id == pid_int))
        product = res.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        product_key = pid_int

    # Validate input
    if file_url and not file:
        # allow direct URL upload via ImageKit
        pass
    elif not file:
        raise HTTPException(status_code=400, detail="No file provided")

    # File validation
    if file is not None:
        if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, WEBP are allowed.")
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
        def _detect_image_magic(h: bytes) -> str | None:
            if len(h) >= 3 and h[0:3] == b"\xFF\xD8\xFF":
                return "jpg"
            if len(h) >= 8 and h[0:8] == b"\x89PNG\r\n\x1a\n":
                return "png"
            if len(h) >= 12 and h[0:4] == b"RIFF" and h[8:12] == b"WEBP":
                return "webp"
            return None
        magic_ext = _detect_image_magic(header)
        if not magic_ext:
            raise HTTPException(status_code=400, detail="Invalid image content detected.")
        ct_map = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
        if ct_map.get(file.content_type) != magic_ext:
            raise HTTPException(status_code=400, detail="File type does not match content.")

    # Upload
    try:
        client = ImageKitClient()
        if not client.is_configured():
            raise HTTPException(status_code=500, detail="ImageKit is not configured. Set IMAGEKIT_* keys in environment.")
        fname = file_name or f"product_{datetime.utcnow().timestamp()}"
        if file is not None:
            result = client.upload(file_bytes=data, file_name=fname)
        else:
            result = client.upload(file_url=file_url, file_name=fname)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to upload to ImageKit.")

    image_url = result.get("url") or result.get("filePath")
    if not image_url:
        raise HTTPException(status_code=502, detail="ImageKit did not return a URL.")

    # Persist ProductImage mapping
    db.add(ProductImage(product_id=product_key, image_url=image_url))
    # Audit log
    try:
        db.add(Log(user_id=None, action_type="product_image_upload", description=f"pid={product_id}", ip_address=(request.client.host if request and request.client else None), status_code=200))
    except Exception:
        pass
    await db.commit()
    return {"product_id": product_id, "image_url": image_url}


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
async def products_in_city(city: str, q: str | None = None, db: AsyncSession = Depends(get_session)):
    from sqlalchemy import text
    city_norm = (city or "").strip()
    if not city_norm:
        raise HTTPException(status_code=400, detail="City is required")
    import re
    if not re.fullmatch(r"[A-Za-z\s\-]{2,100}", city_norm):
        raise HTTPException(status_code=422, detail="Invalid city format")
    exists = (await db.execute(text(
        "SELECT 1 FROM Shops WHERE LOWER(city) = LOWER(:c) UNION SELECT 1 FROM Shop_Address WHERE LOWER(city) = LOWER(:c) LIMIT 1"
    ), {"c": city_norm})).first()
    if not exists:
        raise HTTPException(status_code=404, detail="City not found")
    sql = (
        "SELECT p.product_id, p.product_name, p.brand, p.description, sp.price, sp.stock, a.city "
        "FROM Shop_Product sp "
        "JOIN Shops s ON sp.shop_id = s.shop_id "
        "LEFT JOIN Shop_Address a ON a.shop_id = s.shop_id "
        "JOIN Products p ON p.product_id = sp.product_id "
        "WHERE (LOWER(s.city) = LOWER(:c) OR LOWER(a.city) = LOWER(:c)) "
        "AND (sp.stock IS NOT NULL AND sp.stock > 0)"
    )
    params = {"c": city_norm}
    if q and q.strip():
        params["pat"] = f"%{q}%"
        sql += " AND (LOWER(p.product_name) LIKE LOWER(:pat) OR LOWER(p.brand) LIKE LOWER(:pat) OR LOWER(p.description) LIKE LOWER(:pat))"
    rows = (await db.execute(text(sql), params)).all()
    out = []
    def _hex_or_plain(val):
        if isinstance(val, (bytes, bytearray)):
            return val.hex()
        try:
            if type(val).__name__ == 'memoryview':
                return bytes(val).hex()
        except Exception:
            pass
        return val
    for pid, pname, brand, desc, price, stock, c in rows:
        out.append({
            "product_id": _hex_or_plain(pid),
            "product_name": pname,
            "brand": brand,
            "description": desc,
            "price": float(price) if price is not None else None,
            "stock": stock,
            "city": c,
        })
    dedup: dict[str, dict] = {}
    for item in out:
        pid = str(item["product_id"])
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

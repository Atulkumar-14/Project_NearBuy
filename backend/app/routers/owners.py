from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.auth import get_current_owner
from app.db.session import get_session
from sqlalchemy import text

router = APIRouter()


@router.get("/me")
async def owners_me(owner: dict = Depends(get_current_owner), db: AsyncSession = Depends(get_session)):
    oid_hex = owner.get("owner_id")
    oid_bytes = bytes.fromhex(oid_hex) if isinstance(oid_hex, str) else oid_hex
    rows = (await db.execute(text("SELECT shop_id, shop_name, shop_image FROM Shops WHERE owner_id = :oid"), {"oid": oid_bytes})).all() or []
    shops = [
        {
            "shop_id": (sid.hex() if isinstance(sid, (bytes, bytearray)) else sid),
            "shop_name": name,
            "shop_image": img,
        }
        for (sid, name, img) in rows
    ]
    return {
        "owner_id": oid_hex,
        "owner_name": owner.get("owner_name"),
        "email": owner.get("email"),
        "phone": owner.get("phone"),
        "shops": shops,
    }


@router.get("/me/shops")
async def owners_me_shops(owner: dict = Depends(get_current_owner), db: AsyncSession = Depends(get_session)):
    oid_hex = owner.get("owner_id")
    oid_bytes = bytes.fromhex(oid_hex) if isinstance(oid_hex, str) else oid_hex
    rows = (await db.execute(text("SELECT shop_id, shop_name, shop_image FROM Shops WHERE owner_id = :oid"), {"oid": oid_bytes})).all() or []
    shops = [
        {
            "shop_id": (sid.hex() if isinstance(sid, (bytes, bytearray)) else sid),
            "shop_name": name,
            "shop_image": img,
        }
        for (sid, name, img) in rows
    ]
    return {"shops": shops}

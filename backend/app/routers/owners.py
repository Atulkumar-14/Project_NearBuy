from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.auth import get_current_owner
from app.db.session import get_session
from app.models import ShopOwner, Shop

router = APIRouter()


@router.get("/me")
async def owners_me(owner: ShopOwner = Depends(get_current_owner), db: AsyncSession = Depends(get_session)):
    # Fetch shops owned by the current owner
    res = await db.execute(select(Shop).where(Shop.owner_id == owner.owner_id))
    shops = res.scalars().all() or []

    return {
        "owner_id": owner.owner_id,
        "owner_name": owner.owner_name,
        "email": owner.email,
        "phone": owner.phone,
        "created_at": owner.created_at,
        "last_login_at": owner.last_login_at,
        "shops": [
            {
                "shop_id": s.shop_id,
                "shop_name": s.shop_name,
                "shop_image": s.shop_image,
            }
            for s in shops
        ],
    }


@router.get("/me/shops")
async def owners_me_shops(owner: ShopOwner = Depends(get_current_owner), db: AsyncSession = Depends(get_session)):
    # Return richer shop details including address and timings for the current owner
    stmt = (
        select(Shop)
        .where(Shop.owner_id == owner.owner_id)
        .options(selectinload(Shop.address), selectinload(Shop.timings))
    )
    res = await db.execute(stmt)
    shops = res.scalars().all() or []

    def serialize_shop(s: Shop):
        addr = s.address
        timings = s.timings or []
        return {
            "shop_id": s.shop_id,
            "shop_name": s.shop_name,
            "shop_image": s.shop_image,
            "address": (
                {
                    "city": addr.city,
                    "country": addr.country,
                    "pincode": addr.pincode,
                    "landmark": addr.landmark,
                    "area": addr.area,
                    "latitude": float(addr.latitude) if addr.latitude is not None else None,
                    "longitude": float(addr.longitude) if addr.longitude is not None else None,
                }
                if addr
                else None
            ),
            "timings": [
                {
                    "day": t.day,
                    "open_time": t.open_time,
                    "close_time": t.close_time,
                }
                for t in timings
            ],
        }

    return {"shops": [serialize_shop(s) for s in shops]}
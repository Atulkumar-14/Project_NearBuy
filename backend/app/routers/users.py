from fastapi import APIRouter, Depends
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.models import User, PurchaseHistory
from app.core.auth import get_current_user
from app.schemas.user import UserRead


router = APIRouter()

@router.get("/", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(User))
    return res.scalars().all()


@router.get("/{user_id}/purchases")
async def user_purchases(user_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(PurchaseHistory).where(PurchaseHistory.user_id == user_id))
    items = res.scalars().all()
    return [
        {
            "purchase_id": i.purchase_id,
            "shop_id": i.shop_id,
            "product_id": i.product_id,
            "quantity": i.quantity,
            "total_price": float(i.total_price) if i.total_price is not None else None,
            "purchased_at": i.purchased_at,
        }
        for i in items
    ]


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.models import User, UserRead
from app.core.auth import get_current_user


router = APIRouter()

@router.get("/")
async def list_users(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(User))
    items = []
    for u in res.scalars().all():
        uid = u.user_id
        if isinstance(uid, (bytes, bytearray)):
            uid = uid.hex()
        items.append({
            "user_id": uid,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "created_at": u.created_at,
        })
    return items


# Purchases endpoint removed to comply with db.txt (no PurchaseHistory)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

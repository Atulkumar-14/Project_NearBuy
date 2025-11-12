from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_session
from app.models import User, Shop, Product, ProductReview
from app.core.auth import get_current_admin


router = APIRouter()


@router.get("/stats")
async def admin_stats(db: AsyncSession = Depends(get_session), admin=Depends(get_current_admin)):
    users = (await db.execute(select(func.count(User.user_id)))).scalar() or 0
    shops = (await db.execute(select(func.count(Shop.shop_id)))).scalar() or 0
    products = (await db.execute(select(func.count(Product.product_id)))).scalar() or 0
    reviews = (await db.execute(select(func.count(ProductReview.review_id)))).scalar() or 0
    return {
        "users": users,
        "shops": shops,
        "products": products,
        "reviews": reviews,
    }
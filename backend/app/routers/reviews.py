from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.models import ProductReview, Product, User, ReviewCreate, ReviewRead


router = APIRouter()


@router.post("/", response_model=ReviewRead)
async def add_review(user_id: int, payload: ReviewCreate, db: AsyncSession = Depends(get_session)):
    # Validate user and product
    if not (await db.execute(select(User).where(User.user_id == user_id))).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")
    if not (await db.execute(select(Product).where(Product.product_id == payload.product_id))).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")

    review = ProductReview(
        user_id=user_id,
        product_id=payload.product_id,
        rating=payload.rating,
        review_text=payload.review_text,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


@router.get("/product/{product_id}", response_model=list[ReviewRead])
async def list_reviews(product_id: int, db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(ProductReview).where(ProductReview.product_id == product_id))
    return res.scalars().all()

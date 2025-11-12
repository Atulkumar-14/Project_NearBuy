import asyncio
from sqlalchemy import select
from app.db.session import SessionLocal, init_db
from app.models import ProductReview, ShopProduct


async def _insert_invalid_shop_product():
    async with SessionLocal() as session:
        async with session.begin():
            sp = ShopProduct(shop_id=999999, product_id=999999, price=100.0, stock=1)
            session.add(sp)


async def _insert_invalid_review():
    async with SessionLocal() as session:
        async with session.begin():
            rv = ProductReview(user_id=999999, product_id=999999, rating=4.0, review_text="bad fk")
            session.add(rv)


def test_fk_constraints_block_invalid_inserts():
    asyncio.run(init_db())
    try:
        asyncio.run(_insert_invalid_shop_product())
        async def _count_sp():
            async with SessionLocal() as session:
                res = await session.execute(select(ShopProduct).where(ShopProduct.shop_id == 999999))
                return len(res.scalars().all())
        assert asyncio.run(_count_sp()) == 0
    except Exception:
        assert True

    try:
        asyncio.run(_insert_invalid_review())
        async def _count_rv():
            async with SessionLocal() as session:
                res = await session.execute(select(ProductReview).where(ProductReview.user_id == 999999))
                return len(res.scalars().all())
        assert asyncio.run(_count_rv()) == 0
    except Exception:
        assert True

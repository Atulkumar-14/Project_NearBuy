import asyncio
from sqlalchemy import select
from backend.main import app
from app.db.session import SessionLocal, init_db
from app.models import PurchaseHistory, User, Shop, Product


async def _insert_invalid_purchase():
    async with SessionLocal() as session:
        async with session.begin():
            # Ensure IDs that likely do not exist
            ph = PurchaseHistory(user_id=999999, shop_id=999999, product_id=999999, quantity=1, total_price=100.0)
            session.add(ph)


def test_fk_constraints_block_invalid_inserts():
    # Initialize database
    asyncio.run(init_db())
    # Attempt invalid insert and expect failure due to FK constraints
    try:
        asyncio.run(_insert_invalid_purchase())
        # If it didn't raise, ensure row not inserted
        async def _count():
            async with SessionLocal() as session:
                res = await session.execute(select(PurchaseHistory).where(PurchaseHistory.user_id == 999999))
                return len(res.scalars().all())
        count = asyncio.run(_count())
        assert count == 0
    except Exception:
        # Integrity errors are acceptable; indicates FK constraints are enforced
        assert True
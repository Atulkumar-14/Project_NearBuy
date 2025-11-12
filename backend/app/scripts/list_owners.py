import asyncio
from sqlalchemy import select
from app.db.session import SessionLocal, init_db
from app.core.config import settings
from app.models import ShopOwner, Shop


async def main():
    await init_db()
    async with SessionLocal() as session:
        # Try to fetch the configured dummy owner first
        q = await session.execute(select(ShopOwner).where(ShopOwner.email == settings.owner_dummy_email))
        dummy = q.scalar_one_or_none()
        if dummy:
            shops = (await session.execute(select(Shop).where(Shop.owner_id == dummy.owner_id))).scalars().all()
            shops_count = len(shops)
            print(f"Dummy Owner: {dummy.owner_name} | email={dummy.email} | owner_id={dummy.owner_id} | shops={shops_count}")
        else:
            print("Dummy owner not found; listing first 10 owners below:")
        res = await session.execute(select(ShopOwner))
        owners = res.scalars().all()
        for o in owners[:10]:
            shops = (await session.execute(select(Shop).where(Shop.owner_id == o.owner_id))).scalars().all()
            shops_count = len(shops)
            print(f"Owner: {o.owner_name} | email={o.email} | owner_id={o.owner_id} | shops={shops_count}")


if __name__ == "__main__":
    asyncio.run(main())
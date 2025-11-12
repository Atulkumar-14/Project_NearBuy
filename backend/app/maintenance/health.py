import asyncio
from sqlalchemy import select, func
from app.db.session import SessionLocal, init_db
from app.models import Shop, ShopAddress, Product, ProductImage
from app.models.product import ProductPrice, ShopProduct

ALLOWED_CITIES = {"Bhopal", "Indore", "Jabalpur"}

async def verify_db_integrity():
    await init_db()
    async with SessionLocal() as session:
        async with session.begin():
            # Counts
            counts = {}
            for model in [Shop, ShopAddress, Product, ProductImage, ShopProduct, ProductPrice]:
                res = await session.execute(select(func.count()).select_from(model))
                counts[model.__tablename__] = res.scalar_one()

            # City validation
            addr_rows = (await session.execute(select(ShopAddress))).scalars().all()
            invalid_cities = [a.city for a in addr_rows if a.city and a.city not in ALLOWED_CITIES]

            # Duplicate checks for keys
            # ShopProduct unique (shop_id, product_id)
            dup_shop_products = (
                await session.execute(
                    select(ShopProduct.shop_id, ShopProduct.product_id, func.count())
                    .group_by(ShopProduct.shop_id, ShopProduct.product_id)
                    .having(func.count() > 1)
                )
            ).all()

            # ProductPrice duplicates (product_id, shop_id, price, currency)
            dup_product_prices = (
                await session.execute(
                    select(ProductPrice.product_id, ProductPrice.shop_id, ProductPrice.price, ProductPrice.currency, func.count())
                    .group_by(ProductPrice.product_id, ProductPrice.shop_id, ProductPrice.price, ProductPrice.currency)
                    .having(func.count() > 1)
                )
            ).all()

            return {
                "counts": counts,
                "invalid_cities": invalid_cities,
                "dup_shop_products": [(str(r[0]), str(r[1]), int(r[2])) for r in dup_shop_products],
                "dup_product_prices": [
                    (str(r[0]), str(r[1]), float(r[2]), r[3], int(r[4])) for r in dup_product_prices
                ],
            }


if __name__ == "__main__":
    out = asyncio.run(verify_db_integrity())
    print(out)
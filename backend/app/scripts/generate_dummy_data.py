import asyncio
import random
from datetime import datetime, timedelta, time

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal, init_db
from app.models import (
    ShopOwner,
    Shop,
    ShopAddress,
    ShopTiming,
    ProductCategory,
    Product,
    ProductImage,
    ShopProduct,
    User,
    ProductReview,
    SearchHistory,
)


# --- Config ---
CITIES = {
    "Patan": {
        "state": "Gujarat",
        "pincodes": ["384265", "384255", "384260"],
        "landmarks": ["Sahakari Mandli", "Rani ki Vav", "College Road", "Station Road"],
        "areas": ["Subhash Nagar", "Anand Nagar", "Patolia Street", "GEB Colony"],
        "latlon": [(23.8500, 72.1200), (23.8455, 72.1305), (23.8420, 72.1150)],
    },
    "Bhopal": {
        "state": "Madhya Pradesh",
        "pincodes": ["462001", "462002", "462003"],
        "landmarks": ["New Market", "MP Nagar", "Habibganj", "Lake View"],
        "areas": ["Arera Colony", "Shahpura", "BHEL", "Kolar Road"],
        "latlon": [(23.2599, 77.4126), (23.2500, 77.4200), (23.2700, 77.4000)],
    },
    "Indore": {
        "state": "Madhya Pradesh",
        "pincodes": ["452001", "452002", "452003"],
        "landmarks": ["Rajwada", "Sarafa", "Vijay Nagar", "Palasia"],
        "areas": ["Scheme 54", "Bengali Square", "Tilak Nagar", "Sudama Nagar"],
        "latlon": [(22.7196, 75.8577), (22.7200, 75.8700), (22.7100, 75.8600)],
    },
}

CATEGORY_NAMES = [
    "Groceries", "Electronics", "Mobiles", "Fashion", "Footwear", "Home & Kitchen",
    "Stationery", "Health & Personal Care", "Sports", "Toys", "Automotive",
    "Books", "Computer Accessories", "Gaming", "Beauty", "Watches", "Bags",
    "Jewellery", "Baby Care", "Pet Supplies",
]

BRANDS = ["Tata", "Godrej", "Philips", "Samsung", "Mi", "HP", "Dell", "Lenovo", "Sony", "Boat", "LG", "Puma", "Adidas"]

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Krishna", "Atharv", "Aryan", "Ananya",
    "Aadhya", "Diya", "Ishita", "Prachi", "Nisha", "Riya", "Sanya", "Tanvi", "Suhana", "Aarohi",
]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Gupta", "Yadav", "Singh", "Chouhan", "Bansal", "Jain", "Dubey", "Trivedi", "Ghosh", "Roy"]


def rand_dt_within_2y() -> datetime:
    days = random.randint(0, 730)
    seconds = random.randint(0, 24 * 3600)
    return datetime.utcnow() - timedelta(days=days, seconds=seconds)


async def ensure_min_categories(session: AsyncSession, min_count: int = 20) -> list[ProductCategory]:
    existing = (await session.execute(select(ProductCategory))).scalars().all()
    by_name = {c.category_name.lower(): c for c in existing}
    created: list[ProductCategory] = []
    for name in CATEGORY_NAMES:
        if name.lower() not in by_name:
            created.append(ProductCategory(category_name=name, category_description=f"{name} category", created_at=rand_dt_within_2y()))
    # Add extra categories if still below min_count
    suffix = 1
    while len(existing) + len(created) < min_count:
        nm = f"Misc {suffix}"
        created.append(ProductCategory(category_name=nm, category_description="Miscellaneous", created_at=rand_dt_within_2y()))
        suffix += 1
    if created:
        session.add_all(created)
        await session.flush()
    return (await session.execute(select(ProductCategory))).scalars().all()


async def generate_owners_shops(session: AsyncSession):
    # Create owners
    owners: list[ShopOwner] = []
    existing_emails = set((await session.execute(select(ShopOwner.email))).scalars().all())
    existing_phones = set((await session.execute(select(ShopOwner.phone))).scalars().all())
    for i in range(30):
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        email = f"{fname.lower()}.{lname.lower()}{random.randint(100,999)}@example.com"
        phone = f"+91{random.randint(7000000000, 9999999999)}"
        if email in existing_emails or phone in existing_phones:
            continue
        owners.append(ShopOwner(owner_name=f"{fname} {lname}", email=email, phone=phone))
        existing_emails.add(email)
        existing_phones.add(phone)
    if owners:
        session.add_all(owners)
        await session.flush()

    # Create shops with address and timings
    shops: list[Shop] = []
    addresses: list[ShopAddress] = []
    timings: list[ShopTiming] = []
    for city, cfg in CITIES.items():
        for i in range(10):
            owner = random.choice(owners) if owners else (await session.execute(select(ShopOwner))).scalars().first()
            shop = Shop(shop_name=f"{city} Bazaar {i+1}", owner_id=owner.owner_id if owner else None, created_at=rand_dt_within_2y())
            shops.append(shop)
            # Address
            pincode = random.choice(cfg["pincodes"]) 
            landmark = random.choice(cfg["landmarks"]) 
            area = random.choice(cfg["areas"]) 
            lat, lon = random.choice(cfg["latlon"]) 
            addresses.append(ShopAddress(shop_id=shop.shop_id, city=city, country="India", pincode=pincode, landmark=landmark, area=area, latitude=lat, longitude=lon))
            # Timings for 7 days
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for d in days:
                ot = time(hour=random.choice([9, 10, 11]))
                ct = time(hour=random.choice([18, 19, 20]))
                timings.append(ShopTiming(shop_id=shop.shop_id, day=d, open_time=ot, close_time=ct))
    if shops:
        session.add_all(shops)
        await session.flush()
    if addresses:
        session.add_all(addresses)
        await session.flush()
    if timings:
        session.add_all(timings)
        await session.flush()


async def generate_products(session: AsyncSession, categories: list[ProductCategory]):
    products: list[Product] = []
    images: list[ProductImage] = []
    for i in range(60):
        brand = random.choice(BRANDS)
        category = random.choice(categories)
        color = random.choice(["Black", "White", "Blue", "Red", "Green"])
        name = f"{brand} Item {i+1}"
        p = Product(product_name=name, category_id=category.category_id, brand=brand, description=f"{brand} {name}", color=color, created_at=rand_dt_within_2y())
        products.append(p)
        # image_url can be any placeholder; FK will attach after flush
        images.append(ProductImage(product_id=0, image_url=f""))
    session.add_all(products)
    await session.flush()
    # Now attach images to created products deterministically
    for p in products:
        images.append(ProductImage(product_id=p.product_id, image_url=f"https://img.example.com/{p.product_id}.jpg"))
    session.add_all(images)
    await session.flush()

    # Link products to shops with price/stock
    res = await session.execute(select(Shop))
    shops = res.scalars().all()
    links: list[ShopProduct] = []
    for p in products:
        for shop in random.sample(shops, k=min(3, len(shops))):
            price = round(random.uniform(100, 5000), 2)
            stock = random.randint(0, 200)
            links.append(ShopProduct(shop_id=shop.shop_id, product_id=p.product_id, price=price, stock=stock))
    session.add_all(links)
    await session.flush()


async def generate_users_and_activity(session: AsyncSession):
    users: list[User] = []
    existing_emails = set((await session.execute(select(User.email))).scalars().all())
    existing_phones = set((await session.execute(select(User.phone))).scalars().all())
    for i in range(40):
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        email = f"{fname.lower()}.{lname.lower()}{random.randint(100,999)}@mail.com"
        phone = f"+91{random.randint(7000000000, 9999999999)}"
        if email in existing_emails or phone in existing_phones:
            continue
        city = random.choice(list(CITIES.keys()))
        users.append(User(name=f"{fname} {lname}", email=email, phone=phone, password="dummy", created_at=rand_dt_within_2y()))
        existing_emails.add(email)
        existing_phones.add(phone)
    session.add_all(users)
    await session.flush()

    # Fetch products and shops and existing links for purchases
    products = (await session.execute(select(Product))).scalars().all()
    shops = (await session.execute(select(Shop))).scalars().all()
    reviews: list[ProductReview] = []
    searches: list[SearchHistory] = []
    for u in users:
        # Search history
        for _ in range(random.randint(1, 3)):
            term = random.choice(products).product_name.split()[0]
            searches.append(SearchHistory(user_id=u.user_id, search_item=term, timestamp=rand_dt_within_2y()))
        # Reviews
        for p in random.sample(products, k=min(3, len(products))):
            rating = round(random.uniform(2.5, 5.0), 1)
            reviews.append(ProductReview(user_id=u.user_id, product_id=p.product_id, rating=rating, review_text=f"Review for {p.product_name}", created_at=rand_dt_within_2y()))

    if reviews:
        session.add_all(reviews)
        await session.flush()
    if searches:
        session.add_all(searches)
        await session.flush()


async def verify_counts(session: AsyncSession):
    def count(model):
        return session.execute(select(model))

    models = [
        ShopOwner, Shop, ShopAddress, ShopTiming, ProductCategory, Product, ProductImage, ShopProduct, User, ProductReview, SearchHistory, PurchaseHistory,
    ]
    results = {}
    for m in models:
        res = await count(m)
        rows = res.scalars().all()
        results[m.__tablename__] = len(rows)
    return results


async def main():
    await init_db()
    async with SessionLocal() as session:
        try:
            # Ensure categories
            cats = await ensure_min_categories(session, min_count=20)
            # Owners/Shops/Addresses/Timings
            await generate_owners_shops(session)
            # Products + images + shop links
            await generate_products(session, cats)
            # Users + reviews + searches + purchases
            await generate_users_and_activity(session)

            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            print("IntegrityError encountered:", e.orig)
        except Exception as e:
            await session.rollback()
            print("Unexpected error:", e)

        # Verify
        counts = await verify_counts(session)
        for tbl, cnt in counts.items():
            print(f"{tbl}: {cnt}")


if __name__ == "__main__":
    asyncio.run(main())
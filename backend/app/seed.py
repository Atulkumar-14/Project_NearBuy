import asyncio
from datetime import time, datetime

from sqlalchemy import select

from app.db.session import SessionLocal, init_db
from app.core.security import get_password_hash
from app.core.config import settings
from app.models import (
    ProductCategory,
    Product,
    ProductImage,
    ShopOwner,
    Shop,
    ShopAddress,
    ShopTiming,
    ShopProduct,
    User,
    Admin,
    OwnerSecurity,
)
from app.models.product import ProductPrice


async def ensure_unique(session, model, where_clause):
    res = await session.execute(select(model).where(where_clause))
    return res.scalar_one_or_none()


async def seed_categories(session):
    categories = [
        ("Electronics", "Phones, laptops, accessories"),
        ("Mobiles", "Smartphones and mobile accessories"),
        ("Laptops", "Personal and business laptops"),
        ("Groceries", "Daily essentials and packaged foods"),
    ]
    created = []
    for name, desc in categories:
        existing = await ensure_unique(session, ProductCategory, ProductCategory.category_name == name)
        if not existing:
            obj = ProductCategory(category_name=name, category_description=desc)
            session.add(obj)
            created.append(obj)
    return created


async def seed_products(session):
    products = [
        ("iPhone 14", "Mobiles", "Apple", "128GB, Midnight", "Black"),
        ("Samsung Galaxy S23", "Mobiles", "Samsung", "256GB, Phantom Black", "Black"),
        ("Dell Inspiron 15", "Laptops", "Dell", "i5, 16GB RAM, 512GB SSD", "Silver"),
        ("Redmi Note 12", "Mobiles", "Xiaomi", "128GB, Blue", "Blue"),
        ("Amul Milk 1L", "Groceries", "Amul", "Toned milk, 1L carton", "White"),
        ("Aashirvaad Atta 5kg", "Groceries", "ITC", "Whole wheat flour, 5kg", "Brown"),
    ]
    created = []
    for p_name, cat_name, brand, desc, color in products:
        category = await ensure_unique(session, ProductCategory, ProductCategory.category_name == cat_name)
        existing = await ensure_unique(session, Product, Product.product_name == p_name)
        if not existing:
            obj = Product(
                product_name=p_name,
                category_id=category.category_id if category else None,
                brand=brand,
                description=desc,
                color=color,
            )
            session.add(obj)
            created.append(obj)
    return created


async def seed_images(session, products):
    for p in products:
        # Placeholder image URLs; replace with ImageKit URLs if available
        img = ProductImage(product_id=p.product_id, image_url=f"https://via.placeholder.com/600x400?text={p.product_name.replace(' ', '+')}")
        session.add(img)


async def seed_owners_and_shops(session):
    owners = [
        ("Rohit Sharma", "9876543210", "rohit.owner@example.com"),
        ("Neha Verma", "9123456780", "neha.owner@example.com"),
        ("Aman Gupta", "9988776655", "aman.owner@example.com"),
    ]
    shop_specs = [
        ("DB Mall Electronics", 0, "Arera Hills", "Near DB City Mall", "Bhopal", "India", "462011", 23.2350, 77.4330, "https://images.unsplash.com/photo-1515165562835-c3b8b4e0b1bb?q=80&w=1200&auto=format&fit=crop"),
        ("New Market Grocers", 1, "New Market", "Opposite TT Nagar Stadium", "Bhopal", "India", "462003", 23.2430, 77.4020, "https://images.unsplash.com/photo-1556741533-411cf82e4e2d?q=80&w=1200&auto=format&fit=crop"),
        ("MP Nagar Tech Hub", 2, "MP Nagar Zone 1", "Beside Jyoti Cineplex", "Bhopal", "India", "462011", 23.2335, 77.4340, "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1200&auto=format&fit=crop"),
    ]

    owner_objs = []
    for name, phone, email in owners:
        existing = await ensure_unique(session, ShopOwner, ShopOwner.email == email)
        if not existing:
            obj = ShopOwner(owner_name=name, phone=phone, email=email, password_hash=get_password_hash("Owner@123"))
            session.add(obj)
            owner_objs.append(obj)
        else:
            owner_objs.append(existing)

    # Ensure owners have verified security records
    # Flush so newly added owners have IDs
    await session.flush()
    for owner in owner_objs:
        sec = await ensure_unique(session, OwnerSecurity, OwnerSecurity.owner_id == owner.owner_id)
        if not sec:
            session.add(OwnerSecurity(owner_id=owner.owner_id, email_verified_at=datetime.utcnow(), phone_verified_at=datetime.utcnow()))

    shop_objs = []
    for shop_name, owner_idx, area, landmark, city, country, pincode, lat, lon, banner in shop_specs:
        existing = await ensure_unique(session, Shop, Shop.shop_name == shop_name)
        owner = owner_objs[owner_idx]
        if not existing:
            shop = Shop(shop_name=shop_name, owner_id=owner.owner_id, shop_image=banner)
            session.add(shop)
            shop_objs.append(shop)
        else:
            shop_objs.append(existing)

    # Addresses
    for (shop_name, owner_idx, area, landmark, city, country, pincode, lat, lon, banner), shop in zip(shop_specs, shop_objs):
        addr = await ensure_unique(session, ShopAddress, ShopAddress.shop_id == shop.shop_id)
        if not addr:
            session.add(
                ShopAddress(
                    shop_id=shop.shop_id,
                    city=city,
                    country=country,
                    pincode=pincode,
                    landmark=landmark,
                    area=area,
                    latitude=lat,
                    longitude=lon,
                )
            )

    # Timings: cap total rows to 20 across all shops to satisfy demo requirement
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    from sqlalchemy import func
    total_timings = (await session.execute(select(func.count()).select_from(ShopTiming))).scalar_one()
    for shop in shop_objs:
        for d in days:
            if total_timings >= 20:
                break
            existing = await ensure_unique(session, ShopTiming, (ShopTiming.shop_id == shop.shop_id) & (ShopTiming.day == d))
            if not existing:
                if d == "Sunday":
                    session.add(ShopTiming(shop_id=shop.shop_id, day=d, open_time=None, close_time=None))
                else:
                    session.add(ShopTiming(shop_id=shop.shop_id, day=d, open_time=time(10, 0), close_time=time(21, 0)))
                total_timings += 1

    return shop_objs


async def seed_fill_to_20_shops_products(session):
    # Ensure exactly 20 shops across allowed cities
    allowed_cities = ["Bhopal", "Indore", "Jabalpur"]
    res_shops = await session.execute(select(Shop))
    shops = res_shops.scalars().all()
    count_shops = len(shops)
    owner = await ensure_unique(session, ShopOwner, ShopOwner.email == "seed.fill.owner@example.com")
    if not owner:
        owner = ShopOwner(owner_name="Seed Fill Owner", phone="9000000000", email="seed.fill.owner@example.com", password_hash=get_password_hash("Owner@123"))
        session.add(owner)
        await session.flush()
        session.add(OwnerSecurity(owner_id=owner.owner_id, email_verified_at=datetime.utcnow(), phone_verified_at=datetime.utcnow()))
    for i in range(count_shops, 20):
        name = f"Seed Shop {i+1}"
        shop = Shop(shop_name=name, owner_id=owner.owner_id, shop_image=None)
        session.add(shop)
        await session.flush()
        city = allowed_cities[i % len(allowed_cities)]
        session.add(ShopAddress(shop_id=shop.shop_id, city=city, country="India", pincode=f"462{100+i}", landmark=f"Landmark {i+1}", area=f"Area {i+1}", latitude=23.2300 + (i * 0.001), longitude=77.4300 + (i * 0.001)))

    # Ensure exactly 20 products
    res_prod = await session.execute(select(Product))
    products = res_prod.scalars().all()
    count_prod = len(products)
    for i in range(count_prod, 20):
        p = Product(product_name=f"Seed Product {i+1}", brand="SeedBrand", description="Seeded product", color="Color")
        session.add(p)
        await session.flush()
        session.add(ProductImage(product_id=p.product_id, image_url=f"https://via.placeholder.com/600x400?text=Seed+{i+1}"))


async def seed_shop_products(session, shops):
    # Map products into shops with prices/stock
    res = await session.execute(select(Product))
    products = res.scalars().all()
    price_map = {
        "iPhone 14": (69999.00, 8),
        "Samsung Galaxy S23": (79999.00, 5),
        "Dell Inspiron 15": (58999.00, 4),
        "Redmi Note 12": (15999.00, 20),
        "Amul Milk 1L": (62.00, 100),
        "Aashirvaad Atta 5kg": (285.00, 40),
    }
    from sqlalchemy import func
    total_sp = (await session.execute(select(func.count()).select_from(ShopProduct))).scalar_one()
    for shop in shops:
        for p in products:
            if total_sp >= 20:
                break
            existing = await ensure_unique(
                session,
                ShopProduct,
                (ShopProduct.shop_id == shop.shop_id) & (ShopProduct.product_id == p.product_id),
            )
            if not existing:
                price, stock = price_map.get(p.product_name, (0.0, 0))
                session.add(ShopProduct(shop_id=shop.shop_id, product_id=p.product_id, price=price, stock=stock))
                total_sp += 1

    # Also seed ProductPrice entries to demonstrate multiple prices
    # Ensure exactly 20 price records overall
    res_pp = await session.execute(select(ProductPrice))
    existing_pp = res_pp.scalars().all()
    if len(existing_pp) < 20:
        needed = 20 - len(existing_pp)
        shops_cycle = shops * ((needed // max(1, len(shops))) + 1)
        i = 0
        for p in products:
            if i >= needed:
                break
            s = shops_cycle[i]
            base, _ = price_map.get(p.product_name, (100.0, 0))
            session.add(ProductPrice(product_id=p.product_id, shop_id=s.shop_id, price=base + (i % 5) * 10, currency='INR'))
            i += 1


async def seed_users_and_admin(session):
    # Users (dummy)
    users = [
        (settings.user_dummy_name, settings.user_dummy_email, settings.user_dummy_password, settings.user_dummy_phone),
    ]
    for name, email, pwd, phone in users:
        existing = await ensure_unique(session, User, User.email == email)
        if not existing:
            session.add(User(name=name, email=email, password=get_password_hash(pwd), phone=phone))

    # Admin (dummy)
    admin_user_id = settings.admin_user_id
    existing_admin = await ensure_unique(session, Admin, Admin.userId == admin_user_id)
    if not existing_admin:
        session.add(Admin(userId=admin_user_id, password=get_password_hash(settings.admin_password)))

    # Owner (dummy)
    existing_owner = await ensure_unique(session, ShopOwner, ShopOwner.email == settings.owner_dummy_email)
    if not existing_owner:
        session.add(ShopOwner(
            owner_name=settings.owner_dummy_name,
            phone=settings.owner_dummy_phone,
            email=settings.owner_dummy_email,
            password_hash=get_password_hash(settings.owner_dummy_password),
        ))
        await session.flush()
        # Fetch created owner and ensure verified security
        demo_owner = await ensure_unique(session, ShopOwner, ShopOwner.email == settings.owner_dummy_email)
        if demo_owner:
            sec = await ensure_unique(session, OwnerSecurity, OwnerSecurity.owner_id == demo_owner.owner_id)
            if not sec:
                session.add(OwnerSecurity(owner_id=demo_owner.owner_id, email_verified_at=datetime.utcnow(), phone_verified_at=datetime.utcnow()))
    else:
        # Even if owner exists from prior seed, ensure security is verified
        sec = await ensure_unique(session, OwnerSecurity, OwnerSecurity.owner_id == existing_owner.owner_id)
        if not sec:
            session.add(OwnerSecurity(owner_id=existing_owner.owner_id, email_verified_at=datetime.utcnow(), phone_verified_at=datetime.utcnow()))


async def run():
    await init_db()
    async with SessionLocal() as session:
        async with session.begin():
            await seed_categories(session)
            products = await seed_products(session)
            await session.flush()
            await seed_images(session, products)
            shops = await seed_owners_and_shops(session)
            await session.flush()
            # Top up to exactly 20 shops and products (and images), ensuring allowed cities
            await seed_fill_to_20_shops_products(session)
            await session.flush()
            await seed_shop_products(session, shops)
            await seed_users_and_admin(session)

    print("Seed data inserted: products, images, shops, addresses, timings, shop-products, product-prices, users, admin.")


if __name__ == "__main__":
    asyncio.run(run())
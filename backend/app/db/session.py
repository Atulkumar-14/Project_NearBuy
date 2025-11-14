from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event
from pathlib import Path
from app.core.config import settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403 ensure models are imported


_db_url = settings.database_url
try:
    if _db_url.startswith("sqlite+aiosqlite:///"):
        rel = _db_url.split("sqlite+aiosqlite:///", 1)[1]
        p = Path(rel)
        if not p.is_absolute():
            base = Path(__file__).resolve().parent.parent.parent
            abs_path = (base / rel).resolve()
            _db_url = f"sqlite+aiosqlite:///{abs_path.as_posix()}"
except Exception:
    pass

engine = create_async_engine(
    _db_url,
    echo=False,
    future=True,
    connect_args={"timeout": 10.0},
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Ensure SQLite enforces foreign key constraints
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        # Indexes for search performance
        await conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_shops_city ON Shops(city)")
        await conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_shop_address_city ON Shop_Address(city)")
        # Seed: ensure 'Surf' product exists for search testing
        try:
            exists = await conn.exec_driver_sql("SELECT COUNT(1) FROM Products WHERE LOWER(product_name) = 'surf'")
            row = exists.first()
            count = row[0] if row else 0
            if not count:
                await conn.exec_driver_sql(
                    "INSERT INTO Products (product_id, product_name, brand, description, color, created_at) "
                    "VALUES (randomblob(16), 'Surf', 'Unilever', 'Detergent powder', 'Blue', CURRENT_TIMESTAMP)"
                )
        except Exception:
            # Non-blocking: seeding is optional
            pass
        # Seed: default admin credential
        try:
            from jose import jwt
            enc_user = jwt.encode({"u": settings.admin_user_id.lower()}, settings.secret_key, algorithm=settings.algorithm)
            exists_admin = await conn.exec_driver_sql("SELECT COUNT(1) FROM admin_credentials WHERE username = ?", (enc_user,))
            row2 = exists_admin.first()
            count2 = row2[0] if row2 else 0
            if not count2:
                from app.core.security import get_password_hash
                import os
                salt = os.urandom(16).hex()
                await conn.exec_driver_sql(
                    "INSERT INTO admin_credentials (username, password_hash, salt, last_login, failed_attempts) VALUES (?, ?, ?, NULL, 0)",
                    (enc_user, get_password_hash(settings.admin_password), salt)
                )
        except Exception:
            pass
        # Seed products for Indore and Banaras
        try:
            from sqlalchemy import text as _text
            # ensure seed shops exist with coordinates
            async def _ensure_shop(conn, name, city, lat, lon):
                row = (await conn.exec_driver_sql("SELECT shop_id FROM Shops WHERE shop_name = ? AND city = ?", (name, city))).first()
                if not row:
                    await conn.exec_driver_sql(
                        "INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at, city, contact_number) VALUES (randomblob(16), ?, NULL, NULL, CURRENT_TIMESTAMP, ?, NULL)",
                        (name, city)
                    )
                sid = (await conn.exec_driver_sql("SELECT shop_id FROM Shops WHERE shop_name = ? AND city = ? ORDER BY created_at DESC LIMIT 1", (name, city))).first()[0]
                addr = (await conn.exec_driver_sql("SELECT address_id FROM Shop_Address WHERE shop_id = ?", (sid,))).first()
                if not addr:
                    await conn.exec_driver_sql(
                        "INSERT INTO Shop_Address (address_id, shop_id, city, area, latitude, longitude, created_at) VALUES (randomblob(16), ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                        (sid, city, None, lat, lon)
                    )
                return sid
            indore_sid = await _ensure_shop(conn, "Indore Central Market", "Indore", 22.7196, 75.8577)
            banaras_sid = await _ensure_shop(conn, "Banaras Main Bazaar", "Banaras", 25.3176, 82.9739)
            # helper to insert products
            async def _seed_products(conn, sid, base_name):
                for i in range(1, 21):
                    pname = f"{base_name} {i}"
                    prow = (await conn.exec_driver_sql("SELECT product_id FROM Products WHERE product_name = ?", (pname,))).first()
                    if not prow:
                        await conn.exec_driver_sql(
                            "INSERT INTO Products (product_id, product_name, brand, description, color, created_at) VALUES (randomblob(16), ?, 'Generic', 'Seeded product', 'Black', CURRENT_TIMESTAMP)",
                            (pname,)
                        )
                        pid = (await conn.exec_driver_sql("SELECT product_id FROM Products WHERE product_name = ? ORDER BY created_at DESC LIMIT 1", (pname,))).first()[0]
                        await conn.exec_driver_sql(
                            "INSERT INTO Shop_Product (shop_product_id, shop_id, product_id, price, stock, created_at) VALUES (randomblob(16), ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                            (sid, pid, 99.0 + i, 10 + i)
                        )
            await _seed_products(conn, indore_sid, "Indore Product")
            await _seed_products(conn, banaras_sid, "Banaras Product")
        except Exception:
            pass

# Also enforce SQLite foreign keys for every new connection
@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=10000")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
    finally:
        cursor.close()


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

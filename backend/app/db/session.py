from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event
from app.core.config import settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403 ensure models are imported


engine = create_async_engine(
    settings.database_url,
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

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import MetaData, event
from app.core.config import settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403 ensure models are imported


engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Ensure SQLite enforces foreign key constraints
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        # Lightweight migrations: add missing columns if older DB exists
        await _ensure_columns(conn)

# Also enforce SQLite foreign keys for every new connection
@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def _ensure_columns(conn):
    """Ensure newer columns exist on older SQLite DBs without full migrations."""
    async def column_exists(table: str, column: str) -> bool:
        res = await conn.exec_driver_sql(f"PRAGMA table_info('{table}')")
        cols = [row[1] for row in res.fetchall()]  # row[1] is column name
        return column in cols

    async def add_column_if_missing(table: str, column: str, ddl: str):
        if not await column_exists(table, column):
            await conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")

    # Users: last_login_at was added later
    await add_column_if_missing("Users", "last_login_at", "DATETIME")
    # Owners: last_login_at too
    await add_column_if_missing("Shop_Owners", "last_login_at", "DATETIME")
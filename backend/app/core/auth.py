from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_session
from app.models import ShopOwner, Shop, User, Admin
import logging

# Allow absence of Authorization header to fall back to cookies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/owner/login", auto_error=False)
oauth2_scheme_user = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_owner(request: Request, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)):
    try:
        tok = token or request.cookies.get("owner_access_token")
        payload = jwt.decode(tok, settings.secret_key, algorithms=[settings.algorithm])
        sub = payload.get("sub")
        role = payload.get("role")
        if role and role != "owner":
            raise HTTPException(status_code=403, detail="Invalid role for owner access")
        oid_hex = str(sub)
        oid_bytes = bytes.fromhex(oid_hex)
    except (JWTError, ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    from sqlalchemy import text
    row = (await db.execute(text("SELECT owner_id, owner_name, email, phone FROM Shop_Owners WHERE owner_id = :oid"), {"oid": oid_bytes})).first()
    if not row:
        raise HTTPException(status_code=401, detail="Owner not found")
    return {
        "owner_id": oid_hex,
        "owner_name": row[1],
        "email": row[2],
        "phone": row[3],
    }


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme_user), db: AsyncSession = Depends(get_session)):
    try:
        tok = token or request.cookies.get("user_access_token")
        payload = jwt.decode(tok, settings.secret_key, algorithms=[settings.algorithm])
        sub = payload.get("sub")
        role = payload.get("role")
        if role and role != "user":
            raise HTTPException(status_code=403, detail="Invalid role for user access")
        uid_hex = str(sub)
        uid_bytes = bytes.fromhex(uid_hex)
    except (JWTError, ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    from sqlalchemy import text
    row = (await db.execute(
        text("SELECT user_id, name, email, phone, created_at FROM Users WHERE user_id = :uid"),
        {"uid": uid_bytes},
    )).first()
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    return {
        "user_id": uid_hex,
        "name": row[1],
        "email": row[2],
        "phone": row[3],
        "created_at": row[4],
    }


async def get_current_admin(token: str = Depends(oauth2_scheme_user), db: AsyncSession = Depends(get_session)) -> Admin:
    # Admin tokens can use the same scheme but include role="admin" and sub="admin:<userId>"
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        role = payload.get("role")
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin privileges required")
        sub = payload.get("sub")
        if not sub or not str(sub).startswith("admin:"):
            raise HTTPException(status_code=401, detail="Invalid admin token")
        user_id = str(sub).split(":", 1)[1]
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    res = await db.execute(select(Admin).where(Admin.userId == user_id))
    admin = res.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")
    # Log access attempt
    logging.info(f"Admin access by {admin.userId}")
    return admin


async def ensure_owner_of_shop(shop_id: int, owner: ShopOwner, db: AsyncSession) -> None:
    res = await db.execute(select(Shop).where(Shop.shop_id == shop_id))
    shop = res.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    if not shop.owner_id or shop.owner_id != owner.owner_id:
        raise HTTPException(status_code=403, detail="You are not the owner of this shop")

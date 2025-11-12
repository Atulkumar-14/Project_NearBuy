from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.session import get_session
from app.models import User, Admin, AdminLogin, ShopOwner, Log, UserCreate, UserLogin, UserRead, Token, OwnerLogin
from app.core.notify import send_email, send_sms
import logging
try:
    import pyotp
except Exception:
    pyotp = None


router = APIRouter()

# Simple per-IP rate limiter for auth endpoints: max 10 requests/minute
from collections import deque
import time
_AUTH_WINDOW_SECONDS = 60
_AUTH_MAX_REQUESTS = 10
_ip_events: dict[str, deque] = {}

def _auth_rate_limit_check(ip: str | None) -> bool:
    if not ip:
        return True
    now = time.time()
    dq = _ip_events.setdefault(ip, deque())
    while dq and (now - dq[0]) > _AUTH_WINDOW_SECONDS:
        dq.popleft()
    if len(dq) >= _AUTH_MAX_REQUESTS:
        return False
    dq.append(now)
    return True


@router.post("/register")
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_session), request: Request = None):
    ip = request.client.host if request and request.client else None
    if not _auth_rate_limit_check(ip):
        raise HTTPException(status_code=429, detail="Too many registration attempts. Please try again later.")
    from sqlalchemy import text
    exists = (await db.execute(
        text("SELECT user_id FROM Users WHERE email = :email OR phone = :phone"),
        {"email": payload.email, "phone": payload.phone},
    )).first()
    if exists:
        raise HTTPException(status_code=409, detail="User with email or phone already exists")
    try:
        await db.execute(
            text(
                "INSERT INTO Users (user_id, name, email, password, phone, created_at) "
                "VALUES (randomblob(16), :name, :email, :password, :phone, CURRENT_TIMESTAMP)"
            ),
            {
                "name": payload.name,
                "email": payload.email,
                "password": get_password_hash(payload.password),
                "phone": payload.phone,
            },
        )
        # Fetch the new user for response
        row = (await db.execute(
            text("SELECT user_id, name, email, phone, created_at FROM Users WHERE email = :email"),
            {"email": payload.email},
        )).first()
        if not row:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create user")
        # Notifications (best-effort)
        try:
            if row[2]:
                send_email(row[2], "Confirm your account", "Welcome to NearBuy! Please verify your email.")
            if row[3]:
                send_sms(row[3], "NearBuy: Please verify your phone number.")
        except Exception as e:
            logging.warning(f"Notification error: {e}")
        # Log registration
        uid = row[0]
        db.add(Log(action_type="register", description=f"user:{uid.hex() if isinstance(uid, (bytes, bytearray)) else uid}", status_code=200))
        await db.commit()
        # Serialize response
        uid_out = row[0]
        if isinstance(uid_out, (bytes, bytearray)):
            uid_out = uid_out.hex()
        return {
            "user_id": uid_out,
            "name": row[1],
            "email": row[2],
            "phone": row[3],
            "created_at": row[4],
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logging.error(f"User registration error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str, *, role: str):
    secure = settings.require_https
    # Access token cookie: shorter lived, used by APIs
    response.set_cookie(
        key=f"{role}_access_token",
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=int(timedelta(minutes=settings.access_token_expire_minutes).total_seconds()),
        path="/",
    )
    # Refresh token cookie: 24h inactivity window
    response.set_cookie(
        key=f"{role}_refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=int(timedelta(minutes=settings.refresh_token_expire_minutes).total_seconds()),
        path="/",
    )


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_session), request: Request = None):
    ip = request.client.host if request and request.client else None
    if not _auth_rate_limit_check(ip):
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
    from sqlalchemy import text
    row = (await db.execute(text("SELECT user_id, password FROM Users WHERE email = :email"), {"email": payload.email})).first()
    if not row or not row[1] or not verify_password(payload.password, row[1]):
        db.add(Log(action_type="login", description=f"user_invalid:{payload.email}", status_code=401))
        await db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")
    sub = row[0]
    if isinstance(sub, (bytes, bytearray)):
        sub = sub.hex()
    token = create_access_token(
        str(sub),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        role="user",
    )
    refresh = create_access_token(str(sub), expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes), role="user")
    await db.commit()
    response = Response()
    _set_auth_cookies(response, token, refresh, role="user")
    response.media_type = "application/json"
    response.body = (Token(access_token=token).model_dump_json()).encode("utf-8")
    return response


@router.post("/admin/login", response_model=Token)
async def admin_login(payload: AdminLogin, db: AsyncSession = Depends(get_session)):
    from jose import jwt
    from sqlalchemy import text
    # Determine encoded username
    uname = (payload.userId or "").strip().lower()
    if not uname or not payload.password:
        raise HTTPException(status_code=422, detail="Username and password are required")
    enc_user = jwt.encode({"u": uname}, settings.secret_key, algorithm=settings.algorithm)
    row = (await db.execute(text("SELECT username, password_hash, salt, last_login, failed_attempts FROM admin_credentials WHERE username = :u"), {"u": enc_user})).first()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    _, phash, salt, last_login, failed_attempts = row
    # Lockout check
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    if failed_attempts and failed_attempts >= 5 and last_login and (now - last_login) < timedelta(minutes=30):
        raise HTTPException(status_code=429, detail="Account locked due to failed attempts. Try again later.")
    from app.core.security import verify_password
    ok = verify_password(payload.password, phash)
    if not ok:
        await db.execute(text("UPDATE admin_credentials SET failed_attempts = failed_attempts + 1, last_login = :ts WHERE username = :u"), {"ts": now, "u": enc_user})
        await db.commit()
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    # Reset attempts on success
    await db.execute(text("UPDATE admin_credentials SET failed_attempts = 0, last_login = :ts WHERE username = :u"), {"ts": now, "u": enc_user})
    await db.commit()
    token = create_access_token(f"admin:{uname}", role="admin", expires_delta=timedelta(minutes=30))
    return Token(access_token=token)


@router.post("/owner/login", response_model=Token)
async def owner_login(payload: OwnerLogin, db: AsyncSession = Depends(get_session)):
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    from sqlalchemy import text
    row = (await db.execute(text("SELECT owner_id, password_hash FROM Shop_Owners WHERE LOWER(email) = LOWER(:email)"), {"email": payload.email.strip()})).first()
    if not row or not row[1] or not verify_password(payload.password, row[1]):
        db.add(Log(action_type="login", description=f"owner_invalid:{payload.email}", status_code=401))
        await db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")
    sub = row[0]
    if isinstance(sub, (bytes, bytearray)):
        sub = sub.hex()
    token = create_access_token(
        str(sub),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        role="owner",
    )
    refresh = create_access_token(str(sub), expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes), role="owner")
    db.add(Log(action_type="login", description=f"owner:{sub}", status_code=200))
    await db.commit()
    response = Response()
    _set_auth_cookies(response, token, refresh, role="owner")
    response.media_type = "application/json"
    response.body = (Token(access_token=token).model_dump_json()).encode("utf-8")
    return response


@router.post("/refresh")
async def refresh_token(request: Request):
    # Determine role by cookie keys present
    for role in ("user", "owner"):
        rt = request.cookies.get(f"{role}_refresh_token")
        if not rt:
            continue
        try:
            payload = jwt.decode(rt, settings.secret_key, algorithms=[settings.algorithm])
            sub = payload.get("sub")
            if not sub:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            # Issue new access and refresh tokens
            access = create_access_token(str(sub), expires_delta=timedelta(minutes=settings.access_token_expire_minutes), role=role)
            new_refresh = create_access_token(str(sub), expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes), role=role)
            response = Response()
            _set_auth_cookies(response, access, new_refresh, role=role)
            response.media_type = "application/json"
            response.body = b"{\"status\":\"ok\"}"
            return response
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    raise HTTPException(status_code=401, detail="No refresh token found")


@router.post("/logout")
async def logout():
    response = Response()
    # Clear both user and owner cookies
    for role in ("user", "owner"):
        response.delete_cookie(f"{role}_access_token", path="/")
        response.delete_cookie(f"{role}_refresh_token", path="/")
    response.media_type = "application/json"
    response.body = b"{\"status\":\"logged_out\"}"
    return response

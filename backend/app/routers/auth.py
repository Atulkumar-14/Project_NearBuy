from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Response, Request
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.session import get_session
from app.models import User, Admin, ShopOwner, UserVerification, OwnerSecurity, AuthLog
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.schemas.auth import Token, AdminLogin
from app.schemas.owner import OwnerLogin
from app.core.notify import send_email, send_sms
import logging
try:
    import pyotp
except Exception:
    pyotp = None


router = APIRouter()


@router.post("/register", response_model=UserRead)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_session)):
    q = await db.execute(select(User).where((User.email == payload.email) | (User.phone == payload.phone)))
    exists = q.scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="User with email/phone already exists")
    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password=get_password_hash(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    # Create verification record
    ver = UserVerification(user_id=user.user_id)
    # Auto-complete verification when policy does not require it
    if not settings.require_user_verification:
        from datetime import datetime
        ver.status = "verified"
        ver.registration_completed_at = datetime.utcnow()
    db.add(ver)
    await db.commit()
    # Send confirmation notifications (stubbed)
    try:
        if user.email:
            send_email(user.email, "Confirm your account", "Welcome to NearBuy! Please verify your email.")
        if user.phone:
            send_sms(user.phone, "NearBuy: Please verify your phone number.")
    except Exception as e:
        logging.warning(f"Notification error: {e}")
    # Log registration
    db.add(AuthLog(principal_type="user", principal_id=str(user.user_id), event_type="register", success=True, reason=None))
    await db.commit()
    return user


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
async def login(payload: UserLogin, db: AsyncSession = Depends(get_session)):
    q = await db.execute(select(User).where(User.email == payload.email))
    user = q.scalar_one_or_none()
    if not user or not user.password or not verify_password(payload.password, user.password):
        # Log failed login
        db.add(AuthLog(principal_type="user", principal_id=str(user.user_id) if user else None, event_type="login", success=False, reason="invalid_credentials"))
        await db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Check verification status when policy requires it
    if settings.require_user_verification:
        ver = (await db.execute(select(UserVerification).where(UserVerification.user_id == user.user_id))).scalar_one_or_none()
        if not ver or ver.status != "verified":
            db.add(AuthLog(principal_type="user", principal_id=str(user.user_id), event_type="login", success=False, reason="registration_incomplete"))
            await db.commit()
            raise HTTPException(status_code=403, detail="Registration incomplete. Please verify your account before login.")
    token = create_access_token(
        str(user.user_id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        role="user",
    )
    refresh = create_access_token(str(user.user_id), expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes), role="user")
    # Update last_login_at
    user.last_login_at = datetime.utcnow()
    await db.commit()
    # Set cookies and also return body for backward compatibility
    response = Response()
    _set_auth_cookies(response, token, refresh, role="user")
    response.media_type = "application/json"
    response.body = (Token(access_token=token, user_id=user.user_id).model_dump_json()).encode("utf-8")
    return response


@router.post("/admin/login", response_model=Token)
async def admin_login(payload: AdminLogin, db: AsyncSession = Depends(get_session)):
    q = await db.execute(select(Admin).where(Admin.userId == payload.userId))
    admin = q.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    # Admin passwords are pre-hashed when inserted; in real setup use passlib
    # For demo: store hashed and verify via passlib
    from app.core.security import verify_password
    if not verify_password(payload.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    token = create_access_token(f"admin:{admin.userId}", role="admin")
    return Token(access_token=token)


@router.post("/owner/login", response_model=Token)
async def owner_login(payload: OwnerLogin, db: AsyncSession = Depends(get_session)):
    # Email/password authentication for owners
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    q = await db.execute(select(ShopOwner).where(ShopOwner.email == payload.email))
    owner = q.scalar_one_or_none()
    if not owner or not owner.password_hash:
        db.add(AuthLog(principal_type="owner", principal_id=str(owner.owner_id) if owner else None, event_type="login", success=False, reason="invalid_credentials"))
        await db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(payload.password, owner.password_hash):
        db.add(AuthLog(principal_type="owner", principal_id=str(owner.owner_id), event_type="login", success=False, reason="invalid_credentials"))
        await db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Owner verification
    sec = (await db.execute(select(OwnerSecurity).where(OwnerSecurity.owner_id == owner.owner_id))).scalar_one_or_none()
    if not sec or not sec.email_verified_at or not sec.phone_verified_at:
        db.add(AuthLog(principal_type="owner", principal_id=str(owner.owner_id), event_type="login", success=False, reason="verification_required"))
        await db.commit()
        raise HTTPException(status_code=403, detail="Owner account not verified. Please complete email/phone verification.")
    # Two-factor authentication removed per requirements
    token = create_access_token(
        str(owner.owner_id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        role="owner",
    )
    refresh = create_access_token(str(owner.owner_id), expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes), role="owner")
    # Update last_login_at
    owner.last_login_at = datetime.utcnow()
    await db.commit()
    response = Response()
    _set_auth_cookies(response, token, refresh, role="owner")
    response.media_type = "application/json"
    response.body = (Token(access_token=token, user_id=owner.owner_id).model_dump_json()).encode("utf-8")
    # Log success
    db.add(AuthLog(principal_type="owner", principal_id=str(owner.owner_id), event_type="login", success=True, reason=None))
    await db.commit()
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
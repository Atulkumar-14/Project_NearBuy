from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.models import User, ShopOwner, UserVerification, OwnerSecurity, AuthLog
from app.core.auth import get_current_user, get_current_owner

router = APIRouter()


@router.post("/user/complete")
async def complete_user_registration(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    ver = (await db.execute(select(UserVerification).where(UserVerification.user_id == current_user.user_id))).scalar_one_or_none()
    if not ver:
        ver = UserVerification(user_id=current_user.user_id)
        db.add(ver)
    ver.registration_completed_at = datetime.utcnow()
    ver.status = "verified"
    await db.commit()
    db.add(AuthLog(principal_type="user", principal_id=str(current_user.user_id), event_type="verify", success=True, reason=None))
    await db.commit()
    return {"status": "verified"}


@router.post("/owner/verify/email")
async def owner_verify_email(current_owner: ShopOwner = Depends(get_current_owner), db: AsyncSession = Depends(get_session)):
    sec = (await db.execute(select(OwnerSecurity).where(OwnerSecurity.owner_id == current_owner.owner_id))).scalar_one_or_none()
    if not sec:
        sec = OwnerSecurity(owner_id=current_owner.owner_id)
        db.add(sec)
    sec.email_verified_at = datetime.utcnow()
    await db.commit()
    db.add(AuthLog(principal_type="owner", principal_id=str(current_owner.owner_id), event_type="verify", success=True, reason="email"))
    await db.commit()
    return {"status": "email_verified"}


@router.post("/owner/verify/phone")
async def owner_verify_phone(current_owner: ShopOwner = Depends(get_current_owner), db: AsyncSession = Depends(get_session)):
    sec = (await db.execute(select(OwnerSecurity).where(OwnerSecurity.owner_id == current_owner.owner_id))).scalar_one_or_none()
    if not sec:
        sec = OwnerSecurity(owner_id=current_owner.owner_id)
        db.add(sec)
    sec.phone_verified_at = datetime.utcnow()
    await db.commit()
    db.add(AuthLog(principal_type="owner", principal_id=str(current_owner.owner_id), event_type="verify", success=True, reason="phone"))
    await db.commit()
    return {"status": "phone_verified"}



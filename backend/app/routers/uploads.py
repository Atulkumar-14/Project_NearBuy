import hmac
import hashlib
import time
import secrets
from fastapi import APIRouter, HTTPException
from app.core.config import settings


router = APIRouter()


@router.get("/imagekit/auth")
def imagekit_auth():
    if not settings.imagekit_private_key:
        raise HTTPException(status_code=500, detail="ImageKit private key is not configured")
    token = secrets.token_hex(16)
    expire = int(time.time()) + 600
    signature = hmac.new(
        settings.imagekit_private_key.encode("utf-8"),
        f"{token}{expire}".encode("utf-8"),
        hashlib.sha1,
    ).hexdigest()
    return {
        "token": token,
        "expire": expire,
        "signature": signature,
        "publicKey": settings.imagekit_public_key,
        "urlEndpoint": settings.imagekit_url_endpoint,
    }
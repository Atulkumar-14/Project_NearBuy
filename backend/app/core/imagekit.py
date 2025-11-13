import base64
from typing import Optional
import requests
from app.core.config import settings


class ImageKitClient:
    def __init__(self):
        # Prefer app settings loaded from .env for consistency
        self.url_endpoint = settings.imagekit_url_endpoint
        self.private_key = settings.imagekit_private_key

    def is_configured(self) -> bool:
        return bool(self.private_key)

    def upload(self, *, file_bytes: Optional[bytes] = None, file_url: Optional[str] = None, file_name: str = "upload.jpg") -> dict:
        if not self.is_configured():
            raise RuntimeError("ImageKit not configured")
        if not file_bytes and not file_url:
            raise ValueError("Either file_bytes or file_url must be provided")
        auth = (self.private_key, "")
        data = {
            "fileName": file_name,
            "useUniqueFileName": "true",
        }
        files = None
        if file_bytes:
            # ImageKit expects base64 when sending content in form-data 'file'
            b64 = base64.b64encode(file_bytes).decode("utf-8")
            data["file"] = b64
        elif file_url:
            data["file"] = file_url

        resp = requests.post("https://upload.imagekit.io/api/v1/files/upload", data=data, auth=auth)
        resp.raise_for_status()
        return resp.json()
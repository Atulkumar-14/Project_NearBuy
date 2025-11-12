from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    app_name: str = "Nearbuy"
    secret_key: str = "change_me_secret"
    access_token_expire_minutes: int = 60 * 24
    refresh_token_expire_minutes: int = 60 * 24
    algorithm: str = "HS256"

    database_url: str = "sqlite+aiosqlite:///./nearbuy.db"

    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]

    imagekit_public_key: str = ""
    imagekit_private_key: str = ""
    imagekit_url_endpoint: str = ""

    # Dummy account seeds (optional)
    admin_user_id: str = "nearbuy-admin"
    admin_password: str = "Admin@123"
    owner_dummy_name: str = "Demo Owner"
    owner_dummy_email: str = "owner.demo@example.com"
    owner_dummy_phone: str = "9000000000"
    owner_dummy_password: str = "Owner@123"
    user_dummy_name: str = "Demo User"
    user_dummy_email: str = "user.demo@example.com"
    user_dummy_phone: str = "7000000000"
    user_dummy_password: str = "Password@123"

    # Security settings
    require_https: bool = False
    # Verification policy
    require_user_verification: bool = False

    # Pydantic v2-style settings config; ignore extra env keys
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from uuid import UUID


class OwnerLogin(BaseModel):
    email: EmailStr = Field(..., description="Valid email is required")
    password: str = Field(..., description="Password is required")


class OwnerRead(BaseModel):
    owner_id: UUID
    owner_name: str | None
    email: str | None
    phone: str | None
    created_at: datetime | None
    last_login_at: datetime | None

    class Config:
        from_attributes = True
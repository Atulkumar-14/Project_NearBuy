from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    user_id: UUID
    name: str | None
    email: EmailStr | None
    phone: str | None
    created_at: datetime | None
    last_login_at: datetime | None
    
    # Pydantic v2: enable ORM mode
    model_config = ConfigDict(from_attributes=True)
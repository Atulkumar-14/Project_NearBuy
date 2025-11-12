from pydantic import BaseModel
from uuid import UUID


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID | None = None


class AdminLogin(BaseModel):
    userId: str
    password: str
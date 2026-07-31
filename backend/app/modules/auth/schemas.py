from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email_or_username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

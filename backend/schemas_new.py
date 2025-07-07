from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class User(UserBase):
    id: int
    is_active: bool
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None
    is_admin: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class ActivityLogBase(BaseModel):
    action: str
    details: str
    ip_address: Optional[str] = None

class ActivityLog(ActivityLogBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserList(BaseModel):
    users: List[User]
    total: int
    page: int
    per_page: int 
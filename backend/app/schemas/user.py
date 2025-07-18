
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        from_attributes = True
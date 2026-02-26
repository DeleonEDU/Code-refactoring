from pydantic import BaseModel, EmailStr, Field, validator
from typing import List
from config import Category, Role, MIN_PASSWORD_LENGTH

class UserSchema(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.CUSTOMER  # Використовуємо Enum

    @validator("password")
    def validate_password(cls, v):
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError("Password too short")
        return v

class ItemSchema(BaseModel):
    category: Category
    price: float = Field(..., gt=0)

class PurchasePayload(BaseModel):
    user: UserSchema
    items: List[ItemSchema]
    payment: str
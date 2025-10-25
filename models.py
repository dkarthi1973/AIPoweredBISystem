from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional
from decimal import Decimal
from enum import Enum

# Role Enum for easy access
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

# Existing models remain the same...
class ProductCategoryBase(BaseModel):
    category_id: int = Field(..., gt=0, description="Category ID must be positive")
    subcategory_id: int = Field(..., gt=0, description="Subcategory ID must be positive")
    category_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ProductCategory(ProductCategoryBase):
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    category_id: int = Field(..., gt=0)
    subcategory_id: int = Field(..., gt=0)
    product_name: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., gt=0, description="Price must be positive")
    stock_quantity: int = Field(..., ge=0, description="Stock quantity cannot be negative")

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)

class Product(ProductBase):
    product_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Updated Auth Models with roles
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')  # Changed regex to pattern
    full_name: Optional[str] = Field(None, max_length=100)
    role_id: int = Field(default=3, ge=1, le=3, description="1=admin, 2=manager, 3=user")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    username: Optional[str] = None

# Role models
class Role(BaseModel):
    role_id: int
    role_name: str
    description: Optional[str]

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role_id: int
    role_name: str
    is_active: bool
    created_at: str
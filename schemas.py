from typing import List, Optional
from pydantic import BaseModel
from models import ProductCategory, Product

class ProductCategoryWithProducts(ProductCategory):
    products: List[Product] = []

class CRUDException(Exception):
    """Custom exception for CRUD operations"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# Auth schemas
class AuthenticatedUser(BaseModel):
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
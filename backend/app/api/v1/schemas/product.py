"""
Product schemas para validação de requisições/respostas.
"""
from typing import Optional, List, Union
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum


class ProductCategory(str, Enum):
    """Categorias de produtos"""
    ELECTRONICS = "electronics"
    FURNITURE = "furniture"
    BOOKS = "books"
    TOYS = "toys"
    CLOTHING = "clothing"
    SPORTS = "sports"
    TOOLS = "tools"
    OTHER = "other"


class ProductStatus(str, Enum):
    """Status do produto"""
    AVAILABLE = "available"
    SOLD = "sold"
    RESERVED = "reserved"
    INACTIVE = "inactive"


class ProductCreateRequest(BaseModel):
    """Schema para criação de produto"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=500)
    price: Decimal = Field(..., gt=0)
    category: Union[ProductCategory, str] = Field(default=ProductCategory.OTHER)
    quantity: int = Field(default=1, gt=0)
    images: Optional[List[str]] = Field(default=[], max_items=5)
    
    @validator('category', pre=True)
    def validate_category(cls, v):
        if isinstance(v, str):
            # Converter string para enum
            try:
                return ProductCategory(v.lower())
            except ValueError:
                return ProductCategory.OTHER
        return v
    
    @validator('price')
    def validate_price(cls, v):
        if v > 99999.99:
            raise ValueError('Preço não pode ser maior que R$ 99.999,99')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Notebook Dell",
                "description": "Notebook em bom estado, 8GB RAM",
                "price": 1500.00,
                "category": "electronics",
                "quantity": 1,
                "images": []
            }
        }


class ProductUpdateRequest(BaseModel):
    """Schema para atualização de produto"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[ProductCategory] = None
    quantity: Optional[int] = Field(None, gt=0)
    status: Optional[ProductStatus] = None
    images: Optional[List[str]] = Field(None, max_items=5)


class ProductResponse(BaseModel):
    """Schema de resposta para produto"""
    id: str
    seller_id: str
    name: str
    description: str
    price: Decimal
    category: ProductCategory
    quantity: int
    status: ProductStatus
    images: List[str]
    qr_code_url: Optional[str]
    views: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema para lista de produtos"""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
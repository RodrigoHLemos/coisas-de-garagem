"""
User schemas para validação de requisições/respostas.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserRole(str):
    """Roles de usuário"""
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class UserUpdateRequest(BaseModel):
    """Schema para atualização de usuário"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    store_name: Optional[str] = Field(None, max_length=100)
    store_description: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v:
            phone = re.sub(r'[^0-9]', '', v)
            if len(phone) not in [10, 11]:
                raise ValueError('Telefone deve ter 10 ou 11 dígitos')
            return phone
        return v


class UserProfileResponse(BaseModel):
    """Schema de perfil completo do usuário"""
    id: str
    email: str
    name: str
    cpf: str
    phone: str
    role: str
    is_active: bool
    is_verified: bool
    store_name: Optional[str]
    store_description: Optional[str]
    avatar_url: Optional[str]
    total_sales: int
    total_purchases: int
    rating: Optional[float]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema para lista de usuários"""
    items: List[UserProfileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SellerProfileResponse(BaseModel):
    """Schema de perfil público do vendedor"""
    id: str
    name: str
    store_name: Optional[str]
    store_description: Optional[str]
    avatar_url: Optional[str]
    total_products: int
    total_sales: int
    rating: Optional[float]
    member_since: datetime
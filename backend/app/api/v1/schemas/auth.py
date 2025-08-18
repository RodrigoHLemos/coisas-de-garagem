"""
Authentication schemas using Pydantic.
Handles request/response validation for auth endpoints.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserRegisterRequest(BaseModel):
    """User registration request schema"""
    email: EmailStr
    cpf: str = Field(..., min_length=11, max_length=14)
    name: str = Field(..., min_length=3, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8)
    role: str = Field(default="buyer", pattern="^(buyer|seller|admin)$")
    
    @validator('cpf')
    def validate_cpf(cls, v):
        # Remove non-numeric characters
        cpf = re.sub(r'[^0-9]', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF must have 11 digits')
        return cpf
    
    @validator('phone')
    def validate_phone(cls, v):
        # Remove non-numeric characters
        phone = re.sub(r'[^0-9]', '', v)
        if len(phone) not in [10, 11]:
            raise ValueError('Phone must have 10 or 11 digits')
        return phone
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "cpf": "123.456.789-00",
                "name": "João Silva",
                "phone": "(11) 98765-4321",
                "password": "SecurePass123"
            }
        }


class UserLoginRequest(BaseModel):
    """User login request schema"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    name: str
    cpf: str
    phone: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "name": "João Silva",
                "cpf": "123.456.789-00",
                "phone": "(11) 98765-4321",
                "role": "buyer",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "last_login": None
            }
        }
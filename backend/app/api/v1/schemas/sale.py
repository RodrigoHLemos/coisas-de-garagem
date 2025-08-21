"""
Sale schemas para validação de requisições/respostas.
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum


class SaleStatus(str, Enum):
    """Status da venda"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class SaleItemRequest(BaseModel):
    """Item de uma venda"""
    product_id: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0, decimal_places=2)


class SaleCreateRequest(BaseModel):
    """Schema para criar venda"""
    items: List[SaleItemRequest] = Field(..., min_items=1)
    buyer_notes: Optional[str] = Field(None, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "product_id": "123e4567-e89b-12d3-a456-426614174000",
                        "quantity": 2,
                        "unit_price": 50.00
                    }
                ],
                "buyer_notes": "Entregar após 18h"
            }
        }


class SaleItemResponse(BaseModel):
    """Resposta de item de venda"""
    id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class SaleResponse(BaseModel):
    """Schema de resposta para venda"""
    id: str
    seller_id: str
    buyer_id: str
    items: List[SaleItemResponse]
    total_amount: Decimal
    status: SaleStatus
    buyer_notes: Optional[str]
    seller_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SaleListResponse(BaseModel):
    """Schema para lista de vendas"""
    items: List[SaleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SaleUpdateRequest(BaseModel):
    """Schema para atualizar venda"""
    status: Optional[SaleStatus] = None
    seller_notes: Optional[str] = Field(None, max_length=500)
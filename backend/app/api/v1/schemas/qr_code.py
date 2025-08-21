"""
QR Code schemas para validação de requisições/respostas.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class QRCodeGenerateRequest(BaseModel):
    """Schema para gerar QR Code"""
    product_id: str
    size: Optional[int] = Field(default=10, ge=5, le=30)
    border: Optional[int] = Field(default=5, ge=0, le=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "size": 10,
                "border": 5
            }
        }


class QRCodeResponse(BaseModel):
    """Schema de resposta para QR Code"""
    id: str
    product_id: str
    qr_code_url: str
    scan_url: str
    created_at: datetime
    scans_count: int
    
    class Config:
        from_attributes = True


class QRCodeScanResponse(BaseModel):
    """Schema de resposta para scan de QR Code"""
    product_id: str
    product_name: str
    product_price: float
    seller_name: str
    seller_phone: str
    scan_count: int
    scanned_at: datetime
"""
Product repository interface.
Defines specific operations for product data access.
"""
from typing import List, Optional
from uuid import UUID

from .base import IRepository
from ..entities.product import Product, ProductStatus, ProductCategory


class IProductRepository(IRepository[Product]):
    """
    Product repository interface.
    Extends base repository with product-specific operations.
    """
    
    async def get_by_seller(
        self,
        seller_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products by seller ID"""
        pass
    
    async def get_by_category(
        self,
        category: ProductCategory,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products by category"""
        pass
    
    async def get_by_status(
        self,
        status: ProductStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products by status"""
        pass
    
    async def get_by_qr_code(self, qr_code_data: str) -> Optional[Product]:
        """Get product by QR code data"""
        pass
    
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Search products by name or description"""
        pass
    
    async def get_available_products(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get all available products"""
        pass
"""
Serviço de produtos - lógica de negócio para gerenciamento de produtos.
"""
from typing import List, Optional
from uuid import UUID, uuid4
from decimal import Decimal

from ...infrastructure.repositories.product_repository import SupabaseProductRepository
from ...domain.entities.product import Product
from ...domain.value_objects.money import Money
from ...api.v1.schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse
)


class ProductService:
    """
    Serviço responsável por:
    - Criar e gerenciar produtos
    - Buscar e filtrar produtos
    - Gerar QR codes para produtos
    """
    
    def __init__(self):
        self.repository = SupabaseProductRepository()
    
    async def create_product(
        self,
        seller_id: UUID,
        request: ProductCreateRequest,
        user_token: Optional[str] = None
    ) -> ProductResponse:
        """Criar novo produto"""
        product = Product(
            id=uuid4(),
            seller_id=seller_id,
            name=request.name,
            description=request.description,
            price=Money(request.price),
            category=request.category,
            quantity=request.quantity,
            status="available",
            images=request.images or []
        )
        
        created = await self.repository.create(product, user_token=user_token)
        return self._to_response(created)
    
    async def get_product(self, product_id: UUID, user_token: Optional[str] = None) -> Optional[ProductResponse]:
        """Buscar produto por ID"""
        product = await self.repository.get_by_id(product_id, user_token=user_token)
        if product:
            return self._to_response(product)
        return None
    
    async def update_product(
        self,
        product_id: UUID,
        seller_id: UUID,
        request: ProductUpdateRequest,
        user_token: Optional[str] = None
    ) -> Optional[ProductResponse]:
        """Atualizar produto (apenas o dono pode atualizar)"""
        product = await self.repository.get_by_id(product_id, user_token=user_token)
        
        if not product or product.seller_id != seller_id:
            return None
        
        # Atualizar campos fornecidos
        if request.name is not None:
            product.name = request.name
        if request.description is not None:
            product.description = request.description
        if request.price is not None:
            product.price = Money(request.price)
        if request.category is not None:
            product.category = request.category
        if request.quantity is not None:
            product.quantity = request.quantity
        if request.status is not None:
            product.status = request.status
        if request.images is not None:
            product.images = request.images
        
        updated = await self.repository.update(product, user_token=user_token)
        return self._to_response(updated)
    
    async def delete_product(
        self,
        product_id: UUID,
        seller_id: UUID,
        user_token: Optional[str] = None
    ) -> bool:
        """Deletar produto (apenas o dono pode deletar)"""
        product = await self.repository.get_by_id(product_id, user_token=user_token)
        
        if not product or product.seller_id != seller_id:
            return False
        
        return await self.repository.delete(product_id, user_token=user_token)
    
    async def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        page_size: int = 20,
        user_token: Optional[str] = None
    ) -> List[ProductResponse]:
        """Buscar produtos com filtros"""
        skip = (page - 1) * page_size
        
        products = await self.repository.search(
            query=query,
            category=category,
            min_price=Decimal(str(min_price)) if min_price else None,
            max_price=Decimal(str(max_price)) if max_price else None,
            skip=skip,
            limit=page_size,
            user_token=user_token
        )
        
        return [self._to_response(p) for p in products]
    
    async def get_seller_products(
        self,
        seller_id: UUID,
        user_token: Optional[str] = None
    ) -> List[ProductResponse]:
        """Buscar produtos de um vendedor"""
        products = await self.repository.get_by_seller(seller_id, user_token=user_token)
        return [self._to_response(p) for p in products]
    
    def _to_response(self, product: Product) -> ProductResponse:
        """Converter entidade para response schema"""
        return ProductResponse(
            id=str(product.id),
            seller_id=str(product.seller_id),
            name=product.name,
            description=product.description,
            price=product.price.amount,
            category=product.category,
            quantity=product.quantity,
            status=product.status,
            images=product.images,
            qr_code_url=None,  # Será gerado separadamente
            views=0,  # Será implementado depois
            created_at=product.created_at,
            updated_at=product.updated_at
        )
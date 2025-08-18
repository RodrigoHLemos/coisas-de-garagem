"""
Implementação do repositório de produtos usando Supabase.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from ...domain.repositories.product import ProductRepository
from ...domain.entities.product import Product
from ..supabase.client import SimpleSupabaseClient
import httpx


class SupabaseProductRepository(ProductRepository):
    """
    Implementação do ProductRepository usando Supabase.
    """
    
    def __init__(self):
        self.client = SimpleSupabaseClient()
        self.table_name = "products"
    
    async def create(self, product: Product) -> Product:
        """Criar novo produto"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers={
                    **self.client.headers,
                    "Prefer": "return=representation"
                },
                json={
                    "id": str(product.id),
                    "seller_id": str(product.seller_id),
                    "name": product.name,
                    "description": product.description,
                    "price": str(product.price.amount),
                    "category": product.category,
                    "quantity": product.quantity,
                    "status": product.status
                }
            )
            
            if response.status_code == 201:
                return product
            raise Exception(f"Erro ao criar produto: {response.text}")
    
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """Buscar produto por ID"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=self.client.headers,
                params={"id": f"eq.{product_id}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return self._to_entity(data[0])
            return None
    
    async def get_by_seller(self, seller_id: UUID) -> List[Product]:
        """Buscar produtos de um vendedor"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=self.client.headers,
                params={"seller_id": f"eq.{seller_id}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return [self._to_entity(item) for item in data]
            return []
    
    async def update(self, product: Product) -> Product:
        """Atualizar produto"""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers={
                    **self.client.headers,
                    "Prefer": "return=representation"
                },
                params={"id": f"eq.{product.id}"},
                json={
                    "name": product.name,
                    "description": product.description,
                    "price": str(product.price.amount),
                    "category": product.category,
                    "quantity": product.quantity,
                    "status": product.status,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            if response.status_code == 200:
                return product
            raise Exception(f"Erro ao atualizar produto: {response.text}")
    
    async def delete(self, product_id: UUID) -> bool:
        """Deletar produto (marca como inativo)"""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=self.client.headers,
                params={"id": f"eq.{product_id}"},
                json={
                    "status": "inactive",
                    "deleted_at": datetime.utcnow().isoformat()
                }
            )
            
            return response.status_code == 200
    
    async def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Product]:
        """Buscar produtos com filtros"""
        params = {
            "limit": limit,
            "offset": skip,
            "status": "eq.available"
        }
        
        if category:
            params["category"] = f"eq.{category}"
        
        if min_price:
            params["price"] = f"gte.{min_price}"
        
        if max_price:
            if "price" in params:
                params["price"] = f"gte.{min_price}.lte.{max_price}"
            else:
                params["price"] = f"lte.{max_price}"
        
        async with httpx.AsyncClient() as client:
            url = f"{self.client.url}/rest/v1/{self.table_name}"
            
            # Se houver query de busca, usar full text search
            if query:
                params["or"] = f"(name.ilike.%{query}%,description.ilike.%{query}%)"
            
            response = await client.get(
                url,
                headers=self.client.headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return [self._to_entity(item) for item in data]
            return []
    
    def _to_entity(self, data: Dict[str, Any]) -> Product:
        """Converter dados do banco para entidade Product"""
        from ...domain.value_objects.money import Money
        
        return Product(
            id=UUID(data["id"]),
            seller_id=UUID(data["seller_id"]),
            name=data["name"],
            description=data["description"],
            price=Money(Decimal(data["price"])),
            category=data["category"],
            quantity=data["quantity"],
            status=data["status"],
            images=data.get("images", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
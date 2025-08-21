"""
Implementação do repositório de produtos usando Supabase.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

# Repository base removido - implementação direta
from ...domain.entities.product import Product
from ..supabase.client import SimpleSupabaseClient
import httpx


class SupabaseProductRepository:
    """
    Implementação do ProductRepository usando Supabase.
    """
    
    def __init__(self):
        self.client = SimpleSupabaseClient()
        self.table_name = "products"
    
    async def create(self, product: Product, user_token: Optional[str] = None) -> Product:
        """Criar novo produto"""
        # Usar token do usuário se fornecido, senão usar service key
        headers = {
            "apikey": self.client.anon_key,
            "Authorization": f"Bearer {user_token}" if user_token else f"Bearer {self.client.service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=headers,
                json={
                    "id": str(product.id),
                    "seller_id": str(product.seller_id),
                    "name": product.name,
                    "description": product.description,
                    "price": str(product.price.amount),
                    "category": product.category,
                    "quantity": product.quantity,
                    "status": product.status,
                    "images": product.images if product.images else [],
                    "image_url": product.images[0] if product.images and len(product.images) > 0 else None
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                if data and len(data) > 0:
                    return self._to_entity(data[0])
                return product
            raise Exception(f"Erro ao criar produto: {response.status_code} - {response.text}")
    
    async def get_by_id(self, product_id: UUID, user_token: Optional[str] = None) -> Optional[Product]:
        """Buscar produto por ID"""
        headers = {
            "apikey": self.client.anon_key,
            "Authorization": f"Bearer {user_token}" if user_token else f"Bearer {self.client.service_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=headers,
                params={"id": f"eq.{product_id}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return self._to_entity(data[0])
            return None
    
    async def get_by_seller(self, seller_id: UUID, user_token: Optional[str] = None) -> List[Product]:
        """Buscar produtos de um vendedor"""
        headers = {
            "apikey": self.client.anon_key,
            "Authorization": f"Bearer {user_token}" if user_token else f"Bearer {self.client.service_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=headers,
                params={"seller_id": f"eq.{seller_id}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return [self._to_entity(item) for item in data]
            return []
    
    async def update(self, product: Product, user_token: Optional[str] = None) -> Product:
        """Atualizar produto"""
        headers = {
            "apikey": self.client.anon_key,
            "Authorization": f"Bearer {user_token}" if user_token else f"Bearer {self.client.service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=headers,
                params={"id": f"eq.{product.id}"},
                json={
                    "name": product.name,
                    "description": product.description,
                    "price": str(product.price.amount),
                    "category": product.category,
                    "quantity": product.quantity,
                    "status": product.status,
                    "updated_at": datetime.utcnow().isoformat(),
                    "images": product.images if product.images else [],
                    "image_url": product.images[0] if product.images and len(product.images) > 0 else None
                }
            )
            
            if response.status_code == 200:
                return product
            raise Exception(f"Erro ao atualizar produto: {response.text}")
    
    async def delete(self, product_id: UUID, user_token: Optional[str] = None) -> bool:
        """Deletar produto (marca como inativo)"""
        # Usar sempre service_key para bypass RLS no delete
        # A verificação de ownership é feita no serviço
        headers = {
            "apikey": self.client.service_key,
            "Authorization": f"Bearer {self.client.service_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=headers,
                params={"id": f"eq.{product_id}"},
                json={
                    "status": "inactive",
                    "deleted_at": datetime.utcnow().isoformat()
                }
            )
            
            return response.status_code in (200, 204)
    
    async def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        skip: int = 0,
        limit: int = 20,
        user_token: Optional[str] = None
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
        
        headers = {
            "apikey": self.client.anon_key,
            "Authorization": f"Bearer {user_token}" if user_token else f"Bearer {self.client.service_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            url = f"{self.client.url}/rest/v1/{self.table_name}"
            
            # Se houver query de busca, usar full text search
            if query:
                params["or"] = f"(name.ilike.%{query}%,description.ilike.%{query}%)"
            
            response = await client.get(
                url,
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return [self._to_entity(item) for item in data]
            return []
    
    def _to_entity(self, data: Dict[str, Any]) -> Product:
        """Converter dados do banco para entidade Product"""
        from ...domain.value_objects.money import Money
        
        # Processar imagens - priorizar o campo 'images' (JSONB)
        images = []
        if data.get("images"):
            # Se 'images' existe e não é vazio, usar ele
            images = data["images"] if isinstance(data["images"], list) else []
        elif data.get("image_url"):
            # Fallback para o campo antigo 'image_url' se existir
            images = [data["image_url"]]
        
        return Product(
            id=UUID(data["id"]),
            seller_id=UUID(data["seller_id"]),
            name=data["name"],
            description=data["description"],
            price=Money(Decimal(data["price"])),
            category=data["category"],
            quantity=data["quantity"],
            status=data["status"],
            images=images,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
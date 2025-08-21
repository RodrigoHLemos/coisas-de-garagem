"""
Implementação do repositório de usuários usando Supabase.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from ...domain.repositories.user import UserRepository
from ...domain.entities.user import User
from ..supabase.client import SimpleSupabaseClient
import httpx


class SupabaseUserRepository(UserRepository):
    """
    Implementação do UserRepository usando Supabase.
    """
    
    def __init__(self):
        self.client = SimpleSupabaseClient()
        self.table_name = "profiles"
    
    async def create(self, user: User) -> User:
        """Criar novo usuário no Supabase"""
        # O usuário é criado via Auth, aqui só criamos o perfil
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers={
                    **self.client.headers,
                    "Prefer": "return=representation"
                },
                json={
                    "id": str(user.id),
                    "email": user.email.value,
                    "name": user.name,
                    "cpf": user.cpf.value,
                    "phone": user.phone.value,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified
                }
            )
            
            if response.status_code == 201:
                return user
            raise Exception(f"Erro ao criar perfil: {response.text}")
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Buscar usuário por ID"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=self.client.headers,
                params={"id": f"eq.{user_id}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return self._to_entity(data[0])
            return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=self.client.headers,
                params={"email": f"eq.{email}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return self._to_entity(data[0])
            return None
    
    async def get_by_cpf(self, cpf: str) -> Optional[User]:
        """Buscar usuário por CPF"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=self.client.headers,
                params={"cpf": f"eq.{cpf}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return self._to_entity(data[0])
            return None
    
    async def update(self, user: User) -> User:
        """Atualizar usuário"""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers={
                    **self.client.headers,
                    "Prefer": "return=representation"
                },
                params={"id": f"eq.{user.id}"},
                json={
                    "name": user.name,
                    "phone": user.phone.value,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            if response.status_code == 200:
                return user
            raise Exception(f"Erro ao atualizar usuário: {response.text}")
    
    async def delete(self, user_id: UUID) -> bool:
        """Deletar usuário (soft delete)"""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=self.client.headers,
                params={"id": f"eq.{user_id}"},
                json={
                    "is_active": False,
                    "deleted_at": datetime.utcnow().isoformat()
                }
            )
            
            return response.status_code == 200
    
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[User]:
        """Listar usuários com paginação"""
        params = {
            "limit": limit,
            "offset": skip,
            "is_active": "eq.true"
        }
        
        if filters:
            params.update(filters)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.client.url}/rest/v1/{self.table_name}",
                headers=self.client.headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return [self._to_entity(item) for item in data]
            return []
    
    def _to_entity(self, data: Dict[str, Any]) -> User:
        """Converter dados do banco para entidade User"""
        from ...domain.value_objects.email import Email
        from ...domain.value_objects.cpf import CPF
        from ...domain.value_objects.phone import Phone
        
        return User(
            id=UUID(data["id"]),
            email=Email(data["email"]),
            cpf=CPF(data["cpf"]),
            phone=Phone(data["phone"]),
            name=data["name"],
            role=data["role"],
            is_active=data.get("is_active", True),
            is_verified=data.get("is_verified", False),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
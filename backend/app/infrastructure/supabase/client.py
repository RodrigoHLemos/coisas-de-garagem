"""
Cliente Supabase simplificado para testes.
"""
import httpx
from typing import Optional, Dict, Any
import json
from ...core.config import get_settings

settings = get_settings()


class SimpleSupabaseClient:
    """Cliente simplificado do Supabase usando httpx diretamente."""
    
    def __init__(self):
        self.url = settings.supabase.url
        self.anon_key = settings.supabase.anon_key
        self.service_key = settings.supabase.service_key
        self.headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json"
        }
    
    async def sign_up(
        self,
        email: str,
        password: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Registrar novo usuário."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/auth/v1/signup",
                headers=self.headers,
                json={
                    "email": email,
                    "password": password,
                    "data": metadata or {}
                }
            )
            
            if response.status_code not in (200, 201):
                raise Exception(f"Erro ao registrar: {response.text}")
            
            return response.json()
    
    async def sign_in(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """Login do usuário."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/auth/v1/token?grant_type=password",
                headers=self.headers,
                json={
                    "email": email,
                    "password": password
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Erro ao fazer login: {response.text}")
            
            return response.json()
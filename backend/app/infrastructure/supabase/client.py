"""
Cliente Supabase completo para autenticação e operações.
"""
import httpx
from typing import Optional, Dict, Any
import json
import logging
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SimpleSupabaseClient:
    """Cliente do Supabase usando httpx diretamente."""
    
    def __init__(self):
        self.url = settings.supabase.url
        self.anon_key = settings.supabase.anon_key
        self.service_key = settings.supabase.service_key
        self.headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json"
        }
        self.service_headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json"
        }
    
    async def sign_up(
        self,
        email: str,
        password: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Registrar novo usuário."""
        try:
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
                
                data = response.json()
                
                if response.status_code == 400:
                    if "already registered" in data.get("msg", "").lower():
                        raise Exception("Email já registrado")
                    raise Exception(data.get("msg", "Erro ao registrar"))
                
                if response.status_code not in (200, 201):
                    raise Exception(f"Erro ao registrar: {data}")
                
                logger.info(f"Usuário registrado com sucesso: {email}")
                return data
                
        except httpx.RequestError as e:
            logger.error(f"Erro de conexão ao registrar: {e}")
            raise Exception("Erro de conexão com Supabase")
    
    async def sign_in(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """Login do usuário."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.url}/auth/v1/token?grant_type=password",
                    headers=self.headers,
                    json={
                        "email": email,
                        "password": password
                    }
                )
                
                data = response.json()
                
                if response.status_code == 400:
                    error_code = data.get("error_code", "")
                    error_msg = data.get("msg", data.get("error_description", ""))
                    
                    if error_code == "email_not_confirmed":
                        raise Exception("Email não confirmado. Verifique seu email para confirmar o cadastro.")
                    elif "invalid" in error_msg.lower():
                        raise Exception("Email ou senha inválidos")
                    else:
                        raise Exception(f"Erro ao fazer login: {error_msg}")
                
                if response.status_code != 200:
                    raise Exception(f"Erro ao fazer login: {data}")
                
                logger.info(f"Login bem-sucedido: {email}")
                return data
                
        except httpx.RequestError as e:
            logger.error(f"Erro de conexão ao fazer login: {e}")
            raise Exception("Erro de conexão com Supabase")
    
    async def sign_out(self, access_token: str) -> bool:
        """Logout do usuário."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    **self.headers,
                    "Authorization": f"Bearer {access_token}"
                }
                response = await client.post(
                    f"{self.url}/auth/v1/logout",
                    headers=headers
                )
                
                return response.status_code == 204
                
        except httpx.RequestError as e:
            logger.error(f"Erro ao fazer logout: {e}")
            return False
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Renovar access token."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.url}/auth/v1/token?grant_type=refresh_token",
                    headers=self.headers,
                    json={
                        "refresh_token": refresh_token
                    }
                )
                
                if response.status_code != 200:
                    raise Exception("Token de refresh inválido ou expirado")
                
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Erro ao renovar token: {e}")
            raise Exception("Erro de conexão com Supabase")
    
    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """Obter dados do usuário autenticado."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    **self.headers,
                    "Authorization": f"Bearer {access_token}"
                }
                response = await client.get(
                    f"{self.url}/auth/v1/user",
                    headers=headers
                )
                
                if response.status_code != 200:
                    raise Exception("Token inválido")
                
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Erro ao obter usuário: {e}")
            raise Exception("Erro de conexão com Supabase")
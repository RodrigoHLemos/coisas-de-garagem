"""
Dependências compartilhadas da aplicação.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from datetime import datetime
import os
import base64
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importação removida - não temos database.py ainda
from ..infrastructure.supabase.client import SimpleSupabaseClient

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Supabase client
supabase_client = SimpleSupabaseClient()

async def get_db():
    """Obter sessão do banco de dados - placeholder."""
    # TODO: Implementar quando tivermos SQLAlchemy configurado
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Obter usuário atual a partir do token JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Obter e decodificar a chave JWT
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if not jwt_secret:
            raise credentials_exception
        
        # A chave JWT do Supabase já está em formato correto, não precisa decodificar base64
        # Decodificar token JWT do Supabase
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None:
            raise credentials_exception
        
        # Buscar perfil do usuário direto via Supabase
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{supabase_client.url}/rest/v1/profiles",
                headers={
                    **supabase_client.headers,
                    "Authorization": f"Bearer {token}"
                },
                params={"id": f"eq.{user_id}", "select": "*"}
            )
            
            if response.status_code != 200:
                raise credentials_exception
            
            profiles = response.json()
            if not profiles or len(profiles) == 0:
                # Se não encontrou perfil, pode ser um novo usuário - criar perfil básico
                print(f"Perfil não encontrado para user_id: {user_id}")
                raise credentials_exception
            
            profile_data = profiles[0]
            
            # Retornar como objeto simples com atributos
            class UserProfile:
                def __init__(self, data):
                    self.id = data["id"]
                    self.email = data["email"]
                    self.name = data["name"]
                    self.cpf = data["cpf"]
                    self.phone = data["phone"]
                    self.role = data["role"]
                    self.is_active = data.get("is_active", True)
                    self.is_verified = data.get("is_verified", False)
                    self.store_name = data.get("store_name")
                    self.store_description = data.get("store_description")
                    self.avatar_url = data.get("avatar_url")
                    self.created_at = data["created_at"]
                    self.updated_at = data["updated_at"]
            
            return UserProfile(profile_data)
        
    except JWTError as e:
        print(f"Erro JWT: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"Erro ao obter usuário: {e}")
        import traceback
        traceback.print_exc()
        raise credentials_exception

async def get_current_seller(
    current_user = Depends(get_current_user)
):
    """
    Verificar se o usuário atual é um vendedor.
    """
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas vendedores podem acessar este recurso"
        )
    return current_user

async def get_current_buyer(
    current_user = Depends(get_current_user)
):
    """
    Verificar se o usuário atual é um comprador.
    """
    if current_user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas compradores podem acessar este recurso"
        )
    return current_user
"""
Dependências compartilhadas da API.
Inclui autenticação, autorização e outras dependências comuns.
"""
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import httpx
import logging

from ..core.config import get_settings
from ..infrastructure.supabase.client import SimpleSupabaseClient

logger = logging.getLogger(__name__)
settings = get_settings()

# Schema OAuth2 para documentação
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False  # Não força autenticação em todas as rotas
)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[Dict[str, Any]]:
    """
    Obtém o usuário atual baseado no token JWT.
    Retorna None se não houver token ou token inválido.
    """
    if not token:
        return None
    
    try:
        client = SimpleSupabaseClient()
        user = await client.get_user(token)
        return user
    except Exception as e:
        logger.debug(f"Token inválido ou expirado: {e}")
        return None


async def require_user(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Requer que o usuário esteja autenticado.
    Lança exceção se não houver usuário.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def require_seller(
    current_user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    Requer que o usuário seja um vendedor.
    """
    user_metadata = current_user.get("user_metadata", {})
    role = user_metadata.get("role", "buyer")
    
    if role not in ["seller", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para vendedores"
        )
    return current_user


async def require_admin(
    current_user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    Requer que o usuário seja um administrador.
    """
    user_metadata = current_user.get("user_metadata", {})
    role = user_metadata.get("role", "buyer")
    
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para administradores"
        )
    return current_user


async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    Obtém o perfil completo do usuário da tabela profiles.
    """
    try:
        # Buscar perfil no banco
        client = SimpleSupabaseClient()
        user_id = current_user.get("id")
        
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"{client.url}/rest/v1/profiles",
                headers=client.service_headers,
                params={"id": f"eq.{user_id}", "select": "*"}
            )
            
            if response.status_code == 200:
                profiles = response.json()
                if profiles:
                    return profiles[0]
            
            # Se não encontrou perfil, criar um básico
            user_metadata = current_user.get("user_metadata", {})
            return {
                "id": user_id,
                "email": current_user.get("email"),
                "name": user_metadata.get("name", ""),
                "cpf": user_metadata.get("cpf", ""),
                "phone": user_metadata.get("phone", ""),
                "role": user_metadata.get("role", "buyer"),
                "is_active": True,
                "is_verified": current_user.get("email_confirmed_at") is not None
            }
            
    except Exception as e:
        logger.error(f"Erro ao obter perfil: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter perfil do usuário"
        )
"""
User management endpoints.
Handles user profiles, updates, and queries.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from ....api.deps import require_user, get_current_user_profile
from ....api.v1.schemas.user import UserProfileResponse, UserUpdateRequest

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    profile: Dict[str, Any] = Depends(get_current_user_profile)
):
    """
    Obtém o perfil do usuário autenticado.
    
    Requer autenticação.
    """
    return UserProfileResponse(
        id=profile.get("id"),
        email=profile.get("email"),
        name=profile.get("name"),
        cpf=profile.get("cpf"),
        phone=profile.get("phone"),
        role=profile.get("role"),
        is_active=profile.get("is_active", True),
        is_verified=profile.get("is_verified", False),
        store_name=profile.get("store_name"),
        store_description=profile.get("store_description"),
        avatar_url=profile.get("avatar_url"),
        total_sales=profile.get("total_sales", 0),
        total_purchases=profile.get("total_purchases", 0),
        rating=profile.get("rating"),
        created_at=profile.get("created_at"),
        updated_at=profile.get("updated_at"),
        last_login=profile.get("last_login")
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    request: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_user),
    profile: Dict[str, Any] = Depends(get_current_user_profile)
):
    """
    Atualiza o perfil do usuário autenticado.
    
    Requer autenticação.
    """
    import httpx
    from ....infrastructure.supabase.client import SimpleSupabaseClient
    
    client = SimpleSupabaseClient()
    user_id = current_user.get("id")
    
    # Preparar dados para atualização
    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.phone is not None:
        update_data["phone"] = request.phone
    if request.store_name is not None:
        update_data["store_name"] = request.store_name
    if request.store_description is not None:
        update_data["store_description"] = request.store_description
    if request.avatar_url is not None:
        update_data["avatar_url"] = request.avatar_url
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo para atualizar"
        )
    
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.patch(
                f"{client.url}/rest/v1/profiles",
                headers=client.service_headers,
                params={"id": f"eq.{user_id}"},
                json=update_data
            )
            
            if response.status_code not in (200, 204):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao atualizar perfil"
                )
        
        # Retornar perfil atualizado
        updated_profile = {**profile, **update_data}
        return UserProfileResponse(
            id=updated_profile.get("id"),
            email=updated_profile.get("email"),
            name=updated_profile.get("name"),
            cpf=updated_profile.get("cpf"),
            phone=updated_profile.get("phone"),
            role=updated_profile.get("role"),
            is_active=updated_profile.get("is_active", True),
            is_verified=updated_profile.get("is_verified", False),
            store_name=updated_profile.get("store_name"),
            store_description=updated_profile.get("store_description"),
            avatar_url=updated_profile.get("avatar_url"),
            total_sales=updated_profile.get("total_sales", 0),
            total_purchases=updated_profile.get("total_purchases", 0),
            rating=updated_profile.get("rating"),
            created_at=updated_profile.get("created_at"),
            updated_at=updated_profile.get("updated_at"),
            last_login=updated_profile.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar perfil: {str(e)}"
        )
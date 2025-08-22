"""
Products endpoints.
Handles product CRUD operations.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.dependencies import get_current_user, get_db, oauth2_scheme
from ....services.product.service import ProductService
from ..schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListResponse,
    ProductCategory
)
# UserResponse removido - usando dict genérico

router = APIRouter()
service = ProductService()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: ProductCreateRequest,
    current_user = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    Criar novo produto.
    Apenas vendedores podem criar produtos.
    """
    # Verificar se é vendedor
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas vendedores podem criar produtos"
        )
    
    # Debug: verificar o que está chegando
    print(f"Criando produto: {request.name}")
    print(f"Imagens recebidas: {len(request.images) if request.images else 0}")
    if request.images and len(request.images) > 0:
        print(f"Primeira imagem (primeiros 50 chars): {request.images[0][:50]}")
    
    try:
        product = await service.create_product(
            seller_id=UUID(current_user.id),
            request=request,
            user_token=token
        )
        return product
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    query: Optional[str] = Query(None, description="Buscar por nome ou descrição"),
    category: Optional[ProductCategory] = Query(None, description="Filtrar por categoria"),
    min_price: Optional[float] = Query(None, gt=0, description="Preço mínimo"),
    max_price: Optional[float] = Query(None, gt=0, description="Preço máximo"),
    page: int = Query(1, ge=1, description="Página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página")
):
    """
    Listar produtos com filtros opcionais.
    Endpoint público - não requer autenticação.
    """
    try:
        products = await service.search_products(
            query=query,
            category=category.value if category else None,
            min_price=min_price,
            max_price=max_price,
            page=page,
            page_size=page_size
        )
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/my-products", response_model=List[ProductResponse])
async def get_my_products(
    current_user = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    Listar produtos do vendedor autenticado.
    """
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas vendedores podem acessar este endpoint"
        )
    
    try:
        products = await service.get_seller_products(
            seller_id=UUID(current_user.id),
            user_token=token
        )
        return products if products else []
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Erro ao buscar produtos do vendedor: {e}")
        # Retornar lista vazia em caso de erro para não quebrar o frontend
        return []


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID
):
    """
    Buscar produto por ID.
    Endpoint público - não requer autenticação.
    """
    product = await service.get_product(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    request: ProductUpdateRequest,
    current_user = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    Atualizar produto.
    Apenas o vendedor dono do produto pode atualizá-lo.
    """
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas vendedores podem atualizar produtos"
        )
    
    try:
        product = await service.update_product(
            product_id=product_id,
            seller_id=UUID(current_user.id),
            request=request,
            user_token=token
        )
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado ou você não tem permissão para atualizá-lo"
            )
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    current_user = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    Deletar produto.
    Apenas o vendedor dono do produto pode deletá-lo.
    """
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas vendedores podem deletar produtos"
        )
    
    deleted = await service.delete_product(
        product_id=product_id,
        seller_id=UUID(current_user.id),
        user_token=token
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado ou você não tem permissão para deletá-lo"
        )
    
    return None
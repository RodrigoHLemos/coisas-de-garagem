"""
Authentication endpoints.
Handles user registration, login, and token management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database.connection import get_session
from ....services.auth.service import AuthService
from ....api.v1.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse
)
from ....core.config import get_settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Register a new user.
    
    - **email**: User's email address
    - **cpf**: Brazilian CPF number
    - **name**: Full name
    - **phone**: Phone number
    - **password**: Password (min 8 characters)
    """
    auth_service = AuthService()
    result = await auth_service.register(
        email=request.email,
        password=request.password,
        name=request.name,
        cpf=request.cpf,
        phone=request.phone,
        role=request.role
    )
    user_data = result.get("user", {})
    user_metadata = user_data.get("user_metadata", {})
    
    return UserResponse(
        id=user_data.get("id", ""),
        email=user_data.get("email", request.email),
        name=user_metadata.get("name", request.name),
        cpf=user_metadata.get("cpf", request.cpf),
        phone=user_metadata.get("phone", request.phone),
        role=user_metadata.get("role", request.role),
        is_active=True,
        is_verified=user_data.get("email_confirmed_at") is not None
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """
    Login with email and password.
    Returns access and refresh tokens.
    """
    auth_service = AuthService()
    tokens = await auth_service.login(form_data.username, form_data.password)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Refresh access token using refresh token.
    """
    auth_service = AuthService(session)
    tokens = await auth_service.refresh_token(refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Get current user information.
    Requires authentication.
    """
    auth_service = AuthService(session)
    user = await auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
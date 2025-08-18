"""
Serviço de autenticação usando Supabase Auth
Segue o princípio de Single Responsibility
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.infrastructure.supabase.client import SimpleSupabaseClient
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.core.config import get_settings
from app.shared.exceptions.auth import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    TokenExpiredError
)


class AuthService:
    """
    Serviço de autenticação responsável por:
    - Registro de novos usuários
    - Login/logout
    - Verificação de tokens
    - Gerenciamento de sessões
    """
    
    def __init__(self):
        self.client = SimpleSupabaseClient()
        self.settings = get_settings()
    
    async def register(
        self,
        email: str,
        password: str,
        name: str,
        cpf: str,
        phone: str,
        role: str = "buyer"
    ) -> Dict[str, Any]:
        """
        Registra um novo usuário no sistema
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            name: Nome completo
            cpf: CPF do usuário
            phone: Telefone
            role: Papel do usuário (buyer/seller/admin)
            
        Returns:
            Dados do usuário criado
            
        Raises:
            UserAlreadyExistsError: Se o email já está cadastrado
        """
        try:
            # Registrar no Supabase Auth
            metadata = {
                "name": name,
                "cpf": cpf,
                "phone": phone,
                "role": role
            }
            
            result = await self.client.sign_up(
                email=email,
                password=password,
                metadata=metadata
            )
            
            return {
                "user": result.get("user"),
                "session": result.get("access_token")
            }
            
        except Exception as e:
            if "already registered" in str(e).lower():
                raise UserAlreadyExistsError(f"Email {email} já está registrado")
            raise
    
    async def login(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Autentica um usuário
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Dados da sessão incluindo tokens
            
        Raises:
            InvalidCredentialsError: Se as credenciais são inválidas
        """
        try:
            result = await self.client.sign_in(
                email=email,
                password=password
            )
            
            return {
                "user": result.user,
                "session": result.session,
                "access_token": result.session.access_token,
                "refresh_token": result.session.refresh_token
            }
            
        except Exception as e:
            if "invalid" in str(e).lower():
                raise InvalidCredentialsError("Email ou senha inválidos")
            raise
    
    async def logout(self, access_token: str) -> None:
        """
        Encerra a sessão do usuário
        
        Args:
            access_token: Token de acesso da sessão
        """
        await self.client.sign_out(access_token)
    
    async def get_current_user(
        self,
        access_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtém o usuário atual baseado no token
        
        Args:
            access_token: Token de acesso JWT
            
        Returns:
            Dados do usuário ou None se token inválido
        """
        try:
            user = await self.client.get_user(access_token)
            return user
        except Exception:
            return None
    
    async def refresh_token(
        self,
        refresh_token: str
    ) -> Dict[str, Any]:
        """
        Renova o token de acesso
        
        Args:
            refresh_token: Token de refresh
            
        Returns:
            Nova sessão com tokens renovados
            
        Raises:
            TokenExpiredError: Se o refresh token expirou
        """
        try:
            result = await self.client.refresh_session(refresh_token)
            return {
                "session": result.session,
                "access_token": result.session.access_token,
                "refresh_token": result.session.refresh_token
            }
        except Exception as e:
            if "expired" in str(e).lower():
                raise TokenExpiredError("Token de refresh expirou")
            raise
    
    async def verify_email(
        self,
        token: str
    ) -> bool:
        """
        Verifica o email do usuário
        
        Args:
            token: Token de verificação enviado por email
            
        Returns:
            True se verificado com sucesso
        """
        try:
            await self.client.verify_email(token)
            return True
        except Exception:
            return False
    
    async def request_password_reset(
        self,
        email: str
    ) -> bool:
        """
        Solicita redefinição de senha
        
        Args:
            email: Email do usuário
            
        Returns:
            True se email enviado com sucesso
        """
        try:
            await self.client.reset_password(email)
            return True
        except Exception:
            return False
    
    async def update_password(
        self,
        access_token: str,
        new_password: str
    ) -> bool:
        """
        Atualiza a senha do usuário
        
        Args:
            access_token: Token de acesso do usuário
            new_password: Nova senha
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            await self.client.update_user(
                access_token,
                password=new_password
            )
            return True
        except Exception:
            return False
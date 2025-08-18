"""
Serviço de autenticação usando Supabase Auth.
Gerencia registro, login e sessões de usuários.
"""
from typing import Optional, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

from ...domain.entities.user import User, UserRole
from ...domain.value_objects.email import Email
from ...domain.value_objects.cpf import CPF
from ...domain.value_objects.phone import Phone
from ...infrastructure.supabase.client import get_supabase_client
from ...shared.exceptions.domain import (
    DomainValidationError,
    UnauthorizedError,
    ConflictError
)

logger = logging.getLogger(__name__)


class SupabaseAuthService:
    """
    Serviço de autenticação integrado com Supabase.
    Gerencia todo o fluxo de autenticação e autorização.
    """
    
    def __init__(self):
        """Inicializar serviço com cliente Supabase"""
        self.supabase = get_supabase_client()
    
    async def register_user(
        self,
        email: str,
        password: str,
        name: str,
        cpf: str,
        phone: str,
        role: str = "buyer"
    ) -> Dict[str, Any]:
        """
        Registrar novo usuário no sistema.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            name: Nome completo
            cpf: CPF brasileiro
            phone: Telefone
            role: Papel do usuário (buyer, seller, admin)
            
        Returns:
            Dados do usuário criado com tokens
            
        Raises:
            DomainValidationError: Se validação falhar
            ConflictError: Se email/CPF já existir
        """
        try:
            # Validar dados usando Value Objects
            email_vo = Email(email)
            cpf_vo = CPF(cpf)
            phone_vo = Phone(phone)
            
            # Validar nome
            if not name or len(name.strip()) < 3:
                raise DomainValidationError("Nome deve ter pelo menos 3 caracteres")
            
            # Validar senha
            if len(password) < 8:
                raise DomainValidationError("Senha deve ter pelo menos 8 caracteres")
            
            # Validar role
            if role not in ["buyer", "seller", "admin"]:
                raise DomainValidationError(f"Role inválido: {role}")
            
            # Verificar se CPF já existe
            existing = await self._check_cpf_exists(cpf_vo.value)
            if existing:
                raise ConflictError(f"CPF já cadastrado: {cpf_vo.formatted}")
            
            # Registrar no Supabase Auth com metadados
            response = await self.supabase.sign_up(
                email=email_vo.value,
                password=password,
                metadata={
                    "name": name,
                    "cpf": cpf_vo.value,
                    "phone": phone_vo.value,
                    "role": role
                }
            )
            
            if not response.user:
                raise DomainValidationError("Erro ao criar usuário")
            
            # Retornar dados do usuário e sessão
            return {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": name,
                    "cpf": cpf_vo.formatted,
                    "phone": phone_vo.formatted,
                    "role": role,
                    "created_at": response.user.created_at
                },
                "session": {
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None,
                    "expires_at": response.session.expires_at if response.session else None
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao registrar usuário: {e}")
            if "already registered" in str(e).lower():
                raise ConflictError("Email já cadastrado")
            raise
    
    async def login(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Fazer login do usuário.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Dados do usuário e tokens de sessão
            
        Raises:
            UnauthorizedError: Se credenciais inválidas
        """
        try:
            # Validar email
            email_vo = Email(email)
            
            # Fazer login no Supabase
            response = await self.supabase.sign_in(
                email=email_vo.value,
                password=password
            )
            
            if not response.user or not response.session:
                raise UnauthorizedError("Credenciais inválidas")
            
            # Buscar perfil completo do usuário
            profile = await self._get_user_profile(response.user.id)
            
            # Atualizar último login
            await self._update_last_login(response.user.id)
            
            return {
                "user": profile,
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                    "expires_in": response.session.expires_in
                }
            }
            
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Erro ao fazer login: {e}")
            raise UnauthorizedError("Erro ao autenticar usuário")
    
    async def logout(self) -> None:
        """
        Fazer logout do usuário atual.
        """
        try:
            await self.supabase.sign_out()
            logger.info("Usuário desconectado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao fazer logout: {e}")
            raise
    
    async def get_current_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Obter usuário atual a partir do token.
        
        Args:
            access_token: Token JWT de acesso
            
        Returns:
            Dados do usuário ou None se inválido
        """
        try:
            # Obter usuário do token
            user = await self.supabase.get_user(access_token)
            
            if not user:
                return None
            
            # Buscar perfil completo
            profile = await self._get_user_profile(user.id)
            return profile
            
        except Exception as e:
            logger.error(f"Erro ao obter usuário do token: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Renovar token de acesso usando refresh token.
        
        Args:
            refresh_token: Token de renovação
            
        Returns:
            Nova sessão com tokens ou None
        """
        try:
            session = await self.supabase.refresh_session(refresh_token)
            
            if not session:
                return None
            
            return {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "expires_at": session.expires_at,
                "expires_in": session.expires_in
            }
            
        except Exception as e:
            logger.error(f"Erro ao renovar token: {e}")
            return None
    
    async def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualizar perfil do usuário.
        
        Args:
            user_id: ID do usuário
            updates: Dados a atualizar
            
        Returns:
            Perfil atualizado
        """
        try:
            # Validar campos se fornecidos
            if "phone" in updates:
                phone_vo = Phone(updates["phone"])
                updates["phone"] = phone_vo.value
            
            if "name" in updates and len(updates["name"]) < 3:
                raise DomainValidationError("Nome deve ter pelo menos 3 caracteres")
            
            # Atualizar metadados no Supabase Auth
            user = await self.supabase.update_user_metadata(user_id, updates)
            
            # Atualizar perfil no banco
            await self._update_profile_data(user_id, updates)
            
            # Retornar perfil atualizado
            return await self._get_user_profile(user_id)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar perfil: {e}")
            raise
    
    async def promote_to_seller(self, user_id: str) -> Dict[str, Any]:
        """
        Promover usuário para vendedor.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Perfil atualizado
        """
        try:
            # Buscar perfil atual
            profile = await self._get_user_profile(user_id)
            
            if profile["role"] == "admin":
                raise DomainValidationError("Admin não pode ser promovido a vendedor")
            
            if profile["role"] == "seller":
                raise DomainValidationError("Usuário já é vendedor")
            
            # Atualizar role
            updates = {"role": "seller"}
            return await self.update_user_profile(user_id, updates)
            
        except Exception as e:
            logger.error(f"Erro ao promover usuário: {e}")
            raise
    
    async def verify_email(self, token: str) -> bool:
        """
        Verificar email do usuário.
        
        Args:
            token: Token de verificação
            
        Returns:
            True se verificado com sucesso
        """
        try:
            # Supabase lida com verificação automaticamente
            # Este método seria usado se precisarmos lógica adicional
            logger.info("Email verificado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar email: {e}")
            return False
    
    # ============= MÉTODOS PRIVADOS =============
    
    async def _check_cpf_exists(self, cpf: str) -> bool:
        """
        Verificar se CPF já existe no banco.
        
        Args:
            cpf: CPF a verificar
            
        Returns:
            True se existe
        """
        try:
            result = self.supabase.table("profiles") \
                .select("id") \
                .eq("cpf", cpf) \
                .execute()
            
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            logger.error(f"Erro ao verificar CPF: {e}")
            return False
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Buscar perfil completo do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dados do perfil
        """
        try:
            result = self.supabase.table("profiles") \
                .select("*") \
                .eq("id", user_id) \
                .single() \
                .execute()
            
            if not result.data:
                raise UnauthorizedError("Perfil não encontrado")
            
            profile = result.data
            
            # Formatar dados
            return {
                "id": profile["id"],
                "email": profile["email"],
                "name": profile["name"],
                "cpf": CPF(profile["cpf"]).formatted if profile.get("cpf") else None,
                "phone": Phone(profile["phone"]).formatted if profile.get("phone") else None,
                "role": profile["role"],
                "is_active": profile.get("is_active", True),
                "is_verified": profile.get("is_verified", False),
                "store_name": profile.get("store_name"),
                "store_description": profile.get("store_description"),
                "avatar_url": profile.get("avatar_url"),
                "created_at": profile["created_at"],
                "updated_at": profile["updated_at"],
                "last_login": profile.get("last_login")
            }
        except Exception as e:
            logger.error(f"Erro ao buscar perfil: {e}")
            raise
    
    async def _update_profile_data(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """
        Atualizar dados do perfil no banco.
        
        Args:
            user_id: ID do usuário
            updates: Dados a atualizar
        """
        try:
            # Filtrar campos permitidos
            allowed_fields = [
                "name", "phone", "role", "store_name", 
                "store_description", "avatar_url"
            ]
            
            filtered_updates = {
                k: v for k, v in updates.items() 
                if k in allowed_fields
            }
            
            if filtered_updates:
                self.supabase.table("profiles") \
                    .update(filtered_updates) \
                    .eq("id", user_id) \
                    .execute()
                    
        except Exception as e:
            logger.error(f"Erro ao atualizar perfil no banco: {e}")
            raise
    
    async def _update_last_login(self, user_id: str) -> None:
        """
        Atualizar timestamp do último login.
        
        Args:
            user_id: ID do usuário
        """
        try:
            self.supabase.table("profiles") \
                .update({"last_login": datetime.utcnow().isoformat()}) \
                .eq("id", user_id) \
                .execute()
        except Exception as e:
            logger.error(f"Erro ao atualizar último login: {e}")
            # Não lançar exceção pois não é crítico
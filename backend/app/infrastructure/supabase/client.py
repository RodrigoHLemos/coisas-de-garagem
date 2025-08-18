"""
Cliente Supabase para integra\u00e7\u00e3o com todos os servi\u00e7os.
Centraliza acesso ao banco, autentica\u00e7\u00e3o, storage e realtime.
"""
from typing import Optional, Dict, Any
from supabase import create_client, Client
from gotrue import AuthResponse, Session, User
from storage3 import SyncStorageClient
import logging

from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SupabaseClient:
    """
    Cliente centralizado do Supabase.
    Gerencia todas as intera\u00e7\u00f5es com os servi\u00e7os Supabase.
    """
    
    def __init__(self):
        """Inicializar cliente Supabase"""
        self.url = settings.supabase.url
        self.anon_key = settings.supabase.anon_key
        self.service_key = settings.supabase.service_key
        
        # Cliente an\u00f4nimo (para opera\u00e7\u00f5es p\u00fablicas)
        self.client: Client = create_client(self.url, self.anon_key)
        
        # Cliente de servi\u00e7o (para opera\u00e7\u00f5es administrativas)
        self.admin_client: Client = create_client(self.url, self.service_key)
        
        logger.info("Cliente Supabase inicializado com sucesso")
    
    # ============= AUTENTICA\u00c7\u00c3O =============
    
    async def sign_up(
        self,
        email: str,
        password: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuthResponse:
        """
        Registrar novo usu\u00e1rio no Supabase Auth.
        
        Args:
            email: Email do usu\u00e1rio
            password: Senha do usu\u00e1rio
            metadata: Dados adicionais (nome, CPF, telefone)
        
        Returns:
            AuthResponse com usu\u00e1rio e sess\u00e3o
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            
            if response.user:
                logger.info(f"Usu\u00e1rio registrado: {email}")
            
            return response
        except Exception as e:
            logger.error(f"Erro ao registrar usu\u00e1rio: {e}")
            raise
    
    async def sign_in(self, email: str, password: str) -> AuthResponse:
        """
        Fazer login com email e senha.
        
        Returns:
            AuthResponse com usu\u00e1rio e sess\u00e3o
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.session:
                logger.info(f"Usu\u00e1rio autenticado: {email}")
            
            return response
        except Exception as e:
            logger.error(f"Erro ao autenticar usu\u00e1rio: {e}")
            raise
    
    async def sign_out(self) -> None:
        """Fazer logout do usu\u00e1rio atual"""
        try:
            self.client.auth.sign_out()
            logger.info("Usu\u00e1rio desconectado")
        except Exception as e:
            logger.error(f"Erro ao desconectar usu\u00e1rio: {e}")
            raise
    
    async def get_user(self, jwt: str) -> Optional[User]:
        """
        Obter usu\u00e1rio a partir do JWT token.
        
        Args:
            jwt: Token JWT do usu\u00e1rio
            
        Returns:
            User ou None se inv\u00e1lido
        """
        try:
            response = self.client.auth.get_user(jwt)
            return response.user if response else None
        except Exception as e:
            logger.error(f"Erro ao obter usu\u00e1rio do token: {e}")
            return None
    
    async def refresh_session(self, refresh_token: str) -> Optional[Session]:
        """
        Renovar sess\u00e3o usando refresh token.
        
        Returns:
            Nova sess\u00e3o ou None
        """
        try:
            response = self.client.auth.refresh_session(refresh_token)
            return response.session if response else None
        except Exception as e:
            logger.error(f"Erro ao renovar sess\u00e3o: {e}")
            return None
    
    async def update_user_metadata(
        self,
        user_id: str,
        metadata: Dict[str, Any]
    ) -> Optional[User]:
        """
        Atualizar metadados do usu\u00e1rio.
        
        Args:
            user_id: ID do usu\u00e1rio
            metadata: Novos metadados
            
        Returns:
            Usu\u00e1rio atualizado
        """
        try:
            # Usar admin client para atualizar outros usu\u00e1rios
            response = self.admin_client.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": metadata}
            )
            return response.user if response else None
        except Exception as e:
            logger.error(f"Erro ao atualizar metadados: {e}")
            raise
    
    # ============= STORAGE =============
    
    async def upload_file(
        self,
        bucket: str,
        path: str,
        file_content: bytes,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Fazer upload de arquivo para Supabase Storage.
        
        Args:
            bucket: Nome do bucket
            path: Caminho do arquivo no bucket
            file_content: Conte\u00fado do arquivo
            content_type: Tipo MIME do arquivo
            
        Returns:
            URL p\u00fablica do arquivo
        """
        try:
            # Upload do arquivo
            response = self.client.storage.from_(bucket).upload(
                path,
                file_content,
                {"content-type": content_type}
            )
            
            # Obter URL p\u00fablica
            public_url = self.client.storage.from_(bucket).get_public_url(path)
            
            logger.info(f"Arquivo enviado: {bucket}/{path}")
            return public_url
        except Exception as e:
            logger.error(f"Erro ao fazer upload: {e}")
            raise
    
    async def delete_file(self, bucket: str, path: str) -> bool:
        """
        Deletar arquivo do Storage.
        
        Returns:
            True se deletado com sucesso
        """
        try:
            response = self.client.storage.from_(bucket).remove([path])
            logger.info(f"Arquivo deletado: {bucket}/{path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo: {e}")
            return False
    
    async def create_bucket(self, name: str, public: bool = False) -> bool:
        """
        Criar novo bucket no Storage.
        
        Args:
            name: Nome do bucket
            public: Se o bucket \u00e9 p\u00fablico
            
        Returns:
            True se criado com sucesso
        """
        try:
            response = self.admin_client.storage.create_bucket(
                name,
                {"public": public}
            )
            logger.info(f"Bucket criado: {name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar bucket: {e}")
            return False
    
    # ============= BANCO DE DADOS =============
    
    def table(self, table_name: str):
        """
        Acessar tabela do banco.
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            QueryBuilder para a tabela
        """
        return self.client.table(table_name)
    
    async def execute_rpc(self, function_name: str, params: Dict[str, Any] = None):
        """
        Executar fun\u00e7\u00e3o RPC no banco.
        
        Args:
            function_name: Nome da fun\u00e7\u00e3o
            params: Par\u00e2metros da fun\u00e7\u00e3o
            
        Returns:
            Resultado da fun\u00e7\u00e3o
        """
        try:
            response = self.client.rpc(function_name, params or {}).execute()
            return response.data
        except Exception as e:
            logger.error(f"Erro ao executar RPC {function_name}: {e}")
            raise
    
    # ============= REALTIME =============
    
    def subscribe_to_changes(
        self,
        table: str,
        callback,
        event: str = "*",
        schema: str = "public"
    ):
        """
        Inscrever-se para mudan\u00e7as em tempo real.
        
        Args:
            table: Nome da tabela
            callback: Fun\u00e7\u00e3o callback
            event: Tipo de evento (INSERT, UPDATE, DELETE, *)
            schema: Schema do banco
            
        Returns:
            Subscription channel
        """
        channel = self.client.channel(f"{schema}:{table}")
        
        if event == "*":
            channel.on_postgres_changes(
                event="*",
                schema=schema,
                table=table,
                callback=callback
            )
        else:
            channel.on_postgres_changes(
                event=event,
                schema=schema,
                table=table,
                callback=callback
            )
        
        channel.subscribe()
        logger.info(f"Inscrito em mudan\u00e7as: {table} ({event})")
        return channel


# Singleton do cliente Supabase
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """
    Obter inst\u00e2ncia singleton do cliente Supabase.
    
    Returns:
        Cliente Supabase configurado
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    
    return _supabase_client
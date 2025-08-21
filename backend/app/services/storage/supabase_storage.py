"""
Serviço de armazenamento usando Supabase Storage.
Gerencia upload, download e deleção de arquivos.
"""
from typing import Optional, List, Dict, Any, BinaryIO
from uuid import UUID, uuid4
import logging
from datetime import datetime
import mimetypes
from pathlib import Path

from ...infrastructure.supabase.client import get_supabase_client
from ...shared.exceptions.domain import (
    DomainValidationError,
    UnauthorizedError
)

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """
    Serviço de armazenamento integrado com Supabase Storage.
    Gerencia arquivos de produtos, QR codes e avatares.
    """
    
    # Configurações de tamanho máximo por tipo
    MAX_SIZES = {
        "products": 5 * 1024 * 1024,  # 5MB
        "qr-codes": 1 * 1024 * 1024,  # 1MB
        "avatars": 2 * 1024 * 1024,   # 2MB
    }
    
    # Tipos MIME permitidos por bucket
    ALLOWED_TYPES = {
        "products": ["image/jpeg", "image/png", "image/webp"],
        "qr-codes": ["image/png", "image/svg+xml"],
        "avatars": ["image/jpeg", "image/png", "image/webp"],
    }
    
    def __init__(self):
        """Inicializar serviço com cliente Supabase"""
        self.supabase = get_supabase_client()
    
    async def upload_product_image(
        self,
        seller_id: UUID,
        product_id: UUID,
        file_content: bytes,
        file_name: str,
        is_main: bool = True
    ) -> str:
        """
        Fazer upload de imagem de produto.
        
        Args:
            seller_id: ID do vendedor
            product_id: ID do produto
            file_content: Conteúdo do arquivo
            file_name: Nome original do arquivo
            is_main: Se é a imagem principal
            
        Returns:
            URL pública da imagem
            
        Raises:
            DomainValidationError: Se validação falhar
        """
        try:
            # Validar arquivo
            self._validate_file(
                file_content,
                file_name,
                "products"
            )
            
            # Gerar caminho no storage
            if is_main:
                path = f"{seller_id}/{product_id}/main{self._get_extension(file_name)}"
            else:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                path = f"{seller_id}/{product_id}/gallery/{timestamp}_{file_name}"
            
            # Fazer upload
            url = await self.supabase.upload_file(
                bucket="products",
                path=path,
                file_content=file_content,
                content_type=self._get_mime_type(file_name)
            )
            
            logger.info(f"Imagem de produto enviada: {path}")
            return url
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload de imagem: {e}")
            raise
    
    async def upload_qr_code(
        self,
        product_id: UUID,
        qr_content: bytes,
        format: str = "png"
    ) -> str:
        """
        Fazer upload de QR code gerado.
        
        Args:
            product_id: ID do produto
            qr_content: Conteúdo do QR code
            format: Formato do arquivo (png ou svg)
            
        Returns:
            URL pública do QR code
        """
        try:
            # Validar formato
            if format not in ["png", "svg"]:
                raise DomainValidationError(f"Formato inválido: {format}")
            
            # Gerar caminho
            path = f"{product_id}/qr.{format}"
            
            # Determinar content type
            content_type = "image/png" if format == "png" else "image/svg+xml"
            
            # Fazer upload
            url = await self.supabase.upload_file(
                bucket="qr-codes",
                path=path,
                file_content=qr_content,
                content_type=content_type
            )
            
            logger.info(f"QR code enviado: {path}")
            return url
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload de QR code: {e}")
            raise
    
    async def upload_avatar(
        self,
        user_id: UUID,
        file_content: bytes,
        file_name: str
    ) -> str:
        """
        Fazer upload de avatar do usuário.
        
        Args:
            user_id: ID do usuário
            file_content: Conteúdo do arquivo
            file_name: Nome original do arquivo
            
        Returns:
            URL pública do avatar
        """
        try:
            # Validar arquivo
            self._validate_file(
                file_content,
                file_name,
                "avatars"
            )
            
            # Gerar caminho (sobrescreve anterior)
            path = f"{user_id}/avatar{self._get_extension(file_name)}"
            
            # Fazer upload
            url = await self.supabase.upload_file(
                bucket="avatars",
                path=path,
                file_content=file_content,
                content_type=self._get_mime_type(file_name)
            )
            
            logger.info(f"Avatar enviado: {path}")
            return url
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload de avatar: {e}")
            raise
    
    async def delete_product_images(
        self,
        seller_id: UUID,
        product_id: UUID
    ) -> bool:
        """
        Deletar todas as imagens de um produto.
        
        Args:
            seller_id: ID do vendedor
            product_id: ID do produto
            
        Returns:
            True se deletado com sucesso
        """
        try:
            # Deletar pasta inteira do produto
            path = f"{seller_id}/{product_id}"
            
            # Listar todos os arquivos na pasta
            files = await self._list_files("products", path)
            
            # Deletar cada arquivo
            for file in files:
                await self.supabase.delete_file("products", file)
            
            logger.info(f"Imagens do produto deletadas: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar imagens: {e}")
            return False
    
    async def delete_file(
        self,
        bucket: str,
        file_path: str
    ) -> bool:
        """
        Deletar arquivo específico.
        
        Args:
            bucket: Nome do bucket
            file_path: Caminho do arquivo
            
        Returns:
            True se deletado com sucesso
        """
        try:
            result = await self.supabase.delete_file(bucket, file_path)
            logger.info(f"Arquivo deletado: {bucket}/{file_path}")
            return result
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo: {e}")
            return False
    
    async def get_file_url(
        self,
        bucket: str,
        file_path: str,
        expires_in: Optional[int] = None
    ) -> str:
        """
        Obter URL de acesso ao arquivo.
        
        Args:
            bucket: Nome do bucket
            file_path: Caminho do arquivo
            expires_in: Tempo de expiração em segundos (para URLs privadas)
            
        Returns:
            URL de acesso ao arquivo
        """
        try:
            if expires_in:
                # URL assinada com expiração
                response = self.supabase.client.storage \
                    .from_(bucket) \
                    .create_signed_url(file_path, expires_in)
                return response["signedURL"]
            else:
                # URL pública
                return self.supabase.client.storage \
                    .from_(bucket) \
                    .get_public_url(file_path)
        except Exception as e:
            logger.error(f"Erro ao obter URL do arquivo: {e}")
            raise
    
    async def list_product_images(
        self,
        seller_id: UUID,
        product_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Listar todas as imagens de um produto.
        
        Args:
            seller_id: ID do vendedor
            product_id: ID do produto
            
        Returns:
            Lista de imagens com URLs
        """
        try:
            path = f"{seller_id}/{product_id}"
            files = await self._list_files("products", path)
            
            images = []
            for file in files:
                url = await self.get_file_url("products", file)
                is_main = "main" in file
                
                images.append({
                    "path": file,
                    "url": url,
                    "is_main": is_main,
                    "name": Path(file).name
                })
            
            # Ordenar: principal primeiro, depois por nome
            images.sort(key=lambda x: (not x["is_main"], x["name"]))
            
            return images
            
        except Exception as e:
            logger.error(f"Erro ao listar imagens: {e}")
            return []
    
    async def create_buckets_if_not_exists(self) -> None:
        """
        Criar buckets se não existirem.
        Deve ser executado na inicialização do sistema.
        """
        buckets = ["products", "qr-codes", "avatars"]
        
        for bucket_name in buckets:
            try:
                # Tentar criar bucket (falha se já existe)
                await self.supabase.create_bucket(
                    name=bucket_name,
                    public=True  # Todos os buckets são públicos para leitura
                )
                logger.info(f"Bucket criado: {bucket_name}")
            except Exception as e:
                # Bucket já existe ou erro
                if "already exists" not in str(e).lower():
                    logger.error(f"Erro ao criar bucket {bucket_name}: {e}")
    
    # ============= MÉTODOS PRIVADOS =============
    
    def _validate_file(
        self,
        file_content: bytes,
        file_name: str,
        bucket: str
    ) -> None:
        """
        Validar arquivo antes do upload.
        
        Args:
            file_content: Conteúdo do arquivo
            file_name: Nome do arquivo
            bucket: Bucket destino
            
        Raises:
            DomainValidationError: Se validação falhar
        """
        # Validar tamanho
        max_size = self.MAX_SIZES.get(bucket, 5 * 1024 * 1024)
        if len(file_content) > max_size:
            max_mb = max_size / (1024 * 1024)
            raise DomainValidationError(
                f"Arquivo muito grande. Máximo: {max_mb}MB"
            )
        
        # Validar tipo MIME
        mime_type = self._get_mime_type(file_name)
        allowed_types = self.ALLOWED_TYPES.get(bucket, [])
        
        if mime_type not in allowed_types:
            raise DomainValidationError(
                f"Tipo de arquivo não permitido: {mime_type}. "
                f"Permitidos: {', '.join(allowed_types)}"
            )
    
    def _get_mime_type(self, file_name: str) -> str:
        """
        Obter tipo MIME do arquivo.
        
        Args:
            file_name: Nome do arquivo
            
        Returns:
            Tipo MIME
        """
        mime_type, _ = mimetypes.guess_type(file_name)
        return mime_type or "application/octet-stream"
    
    def _get_extension(self, file_name: str) -> str:
        """
        Obter extensão do arquivo.
        
        Args:
            file_name: Nome do arquivo
            
        Returns:
            Extensão com ponto (.jpg, .png, etc)
        """
        return Path(file_name).suffix.lower()
    
    async def _list_files(
        self,
        bucket: str,
        prefix: str
    ) -> List[str]:
        """
        Listar arquivos em um bucket com prefixo.
        
        Args:
            bucket: Nome do bucket
            prefix: Prefixo do caminho
            
        Returns:
            Lista de caminhos de arquivos
        """
        try:
            response = self.supabase.client.storage \
                .from_(bucket) \
                .list(prefix)
            
            files = []
            for item in response:
                if item.get("name"):
                    # Se é um arquivo
                    files.append(f"{prefix}/{item['name']}")
                elif item.get("id"):
                    # Se é uma pasta, listar recursivamente
                    subfolder = f"{prefix}/{item['name']}"
                    subfiles = await self._list_files(bucket, subfolder)
                    files.extend(subfiles)
            
            return files
            
        except Exception as e:
            logger.error(f"Erro ao listar arquivos: {e}")
            return []
    
    async def generate_thumbnail(
        self,
        image_content: bytes,
        max_width: int = 200,
        max_height: int = 200
    ) -> bytes:
        """
        Gerar thumbnail de imagem.
        
        Args:
            image_content: Conteúdo da imagem original
            max_width: Largura máxima
            max_height: Altura máxima
            
        Returns:
            Conteúdo da thumbnail
        """
        try:
            from PIL import Image
            import io
            
            # Abrir imagem
            img = Image.open(io.BytesIO(image_content))
            
            # Calcular novo tamanho mantendo proporção
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Salvar em bytes
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=85, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Erro ao gerar thumbnail: {e}")
            # Retornar imagem original se falhar
            return image_content
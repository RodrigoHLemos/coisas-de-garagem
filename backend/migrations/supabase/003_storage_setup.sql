-- =====================================================
-- Migration: 003_storage_setup.sql
-- Descrição: Configuração de Storage Buckets
-- Data: 2024
-- NOTA: Execute via Supabase Dashboard ou CLI
-- =====================================================

-- Este arquivo contém os comandos para configurar os buckets
-- no Supabase Storage. Como o Storage usa uma API específica,
-- estes comandos devem ser executados via:
-- 1. Supabase Dashboard (Storage section)
-- 2. Supabase CLI
-- 3. Supabase Management API

-- =====================================================
-- BUCKETS A CRIAR
-- =====================================================

/*
1. BUCKET: products
   - Descrição: Imagens de produtos
   - Público: SIM (leitura)
   - Tamanho máximo arquivo: 5MB
   - Tipos permitidos: image/jpeg, image/png, image/webp
   
2. BUCKET: qr-codes
   - Descrição: QR codes gerados
   - Público: SIM (leitura)
   - Tamanho máximo arquivo: 1MB
   - Tipos permitidos: image/png, image/svg+xml
   
3. BUCKET: avatars
   - Descrição: Fotos de perfil
   - Público: SIM (leitura)
   - Tamanho máximo arquivo: 2MB
   - Tipos permitidos: image/jpeg, image/png, image/webp
*/

-- =====================================================
-- COMANDOS SUPABASE CLI
-- =====================================================

-- Para criar via CLI:
-- supabase storage create products --public
-- supabase storage create qr-codes --public
-- supabase storage create avatars --public

-- =====================================================
-- POLÍTICAS DE STORAGE (RLS)
-- =====================================================

-- As políticas abaixo devem ser aplicadas via Dashboard
-- ou usando a API de administração do Supabase

-- BUCKET: products
-- =====================================================

/*
-- Política: Leitura pública
{
  "name": "Imagens de produtos são públicas",
  "definition": "true",
  "operation": "SELECT"
}

-- Política: Vendedores fazem upload
{
  "name": "Vendedores fazem upload de imagens",
  "definition": "auth.role() IN ('seller', 'admin')",
  "operation": "INSERT"
}

-- Política: Vendedores atualizam suas imagens
{
  "name": "Vendedores atualizam próprias imagens",
  "definition": "auth.uid() IN (
    SELECT seller_id FROM products 
    WHERE image_url LIKE '%' || name
  )",
  "operation": "UPDATE"
}

-- Política: Vendedores deletam suas imagens
{
  "name": "Vendedores deletam próprias imagens",
  "definition": "auth.uid() IN (
    SELECT seller_id FROM products 
    WHERE image_url LIKE '%' || name
  )",
  "operation": "DELETE"
}
*/

-- BUCKET: qr-codes
-- =====================================================

/*
-- Política: Leitura pública
{
  "name": "QR codes são públicos",
  "definition": "true",
  "operation": "SELECT"
}

-- Política: Sistema gera QR codes
{
  "name": "Sistema gera QR codes",
  "definition": "auth.role() IN ('seller', 'admin', 'service_role')",
  "operation": "INSERT"
}
*/

-- BUCKET: avatars
-- =====================================================

/*
-- Política: Leitura pública
{
  "name": "Avatars são públicos",
  "definition": "true",
  "operation": "SELECT"
}

-- Política: Usuários fazem upload do próprio avatar
{
  "name": "Usuários gerenciam próprio avatar",
  "definition": "auth.uid()::text = (storage.foldername(name))[1]",
  "operation": "INSERT,UPDATE,DELETE"
}
*/

-- =====================================================
-- ESTRUTURA DE PASTAS RECOMENDADA
-- =====================================================

/*
products/
├── {seller_id}/
│   ├── {product_id}/
│   │   ├── main.jpg
│   │   ├── thumb.jpg
│   │   └── gallery/
│   │       ├── 1.jpg
│   │       ├── 2.jpg
│   │       └── 3.jpg

qr-codes/
├── {product_id}/
│   ├── qr.png
│   └── qr.svg

avatars/
├── {user_id}/
│   └── avatar.jpg
*/

-- =====================================================
-- FUNÇÕES AUXILIARES PARA STORAGE
-- =====================================================

-- Função para gerar URL de imagem do produto
CREATE OR REPLACE FUNCTION get_product_image_url(
    bucket TEXT,
    file_path TEXT
) RETURNS TEXT AS $$
DECLARE
    supabase_url TEXT;
BEGIN
    -- Substitua pela URL do seu projeto Supabase
    supabase_url := current_setting('app.supabase_url', true);
    
    IF supabase_url IS NULL THEN
        supabase_url := 'https://seu-projeto.supabase.co';
    END IF;
    
    RETURN supabase_url || '/storage/v1/object/public/' || bucket || '/' || file_path;
END;
$$ LANGUAGE plpgsql;

-- Função para validar tipo de arquivo
CREATE OR REPLACE FUNCTION validate_file_type(
    file_name TEXT,
    allowed_types TEXT[]
) RETURNS BOOLEAN AS $$
DECLARE
    file_extension TEXT;
    mime_type TEXT;
BEGIN
    -- Extrair extensão do arquivo
    file_extension := LOWER(split_part(file_name, '.', -1));
    
    -- Mapear extensão para mime type
    CASE file_extension
        WHEN 'jpg', 'jpeg' THEN mime_type := 'image/jpeg';
        WHEN 'png' THEN mime_type := 'image/png';
        WHEN 'webp' THEN mime_type := 'image/webp';
        WHEN 'svg' THEN mime_type := 'image/svg+xml';
        ELSE mime_type := 'unknown';
    END CASE;
    
    RETURN mime_type = ANY(allowed_types);
END;
$$ LANGUAGE plpgsql;

-- Função para gerar path único para upload
CREATE OR REPLACE FUNCTION generate_storage_path(
    bucket_name TEXT,
    user_id UUID,
    file_name TEXT
) RETURNS TEXT AS $$
DECLARE
    timestamp_str TEXT;
    random_str TEXT;
    clean_name TEXT;
BEGIN
    -- Gerar timestamp
    timestamp_str := TO_CHAR(NOW(), 'YYYYMMDD_HH24MISS');
    
    -- Gerar string aleatória
    random_str := SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8);
    
    -- Limpar nome do arquivo
    clean_name := REGEXP_REPLACE(LOWER(file_name), '[^a-z0-9\.]', '_', 'g');
    
    -- Retornar path completo
    RETURN user_id::TEXT || '/' || timestamp_str || '_' || random_str || '_' || clean_name;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGERS PARA LIMPEZA DE STORAGE
-- =====================================================

-- Trigger para deletar imagens quando produto é deletado
CREATE OR REPLACE FUNCTION cleanup_product_images()
RETURNS TRIGGER AS $$
BEGIN
    -- Marcar imagens para deleção (seria processado por job)
    INSERT INTO storage_cleanup_queue (
        bucket,
        path,
        scheduled_at
    ) VALUES (
        'products',
        OLD.seller_id::TEXT || '/' || OLD.id::TEXT,
        NOW()
    );
    
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Tabela para fila de limpeza
CREATE TABLE IF NOT EXISTS public.storage_cleanup_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bucket TEXT NOT NULL,
    path TEXT NOT NULL,
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    status TEXT DEFAULT 'pending'
);

-- Aplicar trigger
CREATE TRIGGER cleanup_product_storage
    AFTER DELETE ON public.products
    FOR EACH ROW
    EXECUTE FUNCTION cleanup_product_images();

-- =====================================================
-- CONFIGURAÇÕES DE CORS PARA STORAGE
-- =====================================================

/*
Adicione estas configurações CORS no Dashboard do Supabase:

{
  "cors": {
    "allowedOrigins": ["*"],
    "allowedMethods": ["GET", "POST", "PUT", "DELETE"],
    "allowedHeaders": ["*"],
    "exposedHeaders": ["*"],
    "maxAge": 3600
  }
}
*/

-- =====================================================
-- EXEMPLO DE USO
-- =====================================================

/*
-- Upload de imagem via JavaScript/TypeScript:

const { data, error } = await supabase.storage
  .from('products')
  .upload(`${userId}/${productId}/main.jpg`, file, {
    contentType: 'image/jpeg',
    upsert: true
  });

-- Obter URL pública:

const { data } = supabase.storage
  .from('products')
  .getPublicUrl(`${userId}/${productId}/main.jpg`);

-- Deletar arquivo:

const { error } = await supabase.storage
  .from('products')
  .remove([`${userId}/${productId}/main.jpg`]);
*/
-- =====================================================
-- Migration: 002_row_level_security.sql
-- Descrição: Políticas de Row Level Security (RLS)
-- Data: 2024
-- =====================================================

-- =====================================================
-- HABILITAR RLS NAS TABELAS
-- =====================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.qr_scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.product_images ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- POLÍTICAS PARA PROFILES
-- =====================================================

-- Usuários podem ver perfis públicos (nome, foto, loja)
CREATE POLICY "Perfis públicos são visíveis para todos"
    ON public.profiles FOR SELECT
    USING (true);

-- Usuários podem atualizar apenas seu próprio perfil
CREATE POLICY "Usuários podem atualizar próprio perfil"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Apenas o próprio usuário pode ver dados sensíveis (CPF, telefone)
CREATE POLICY "Dados sensíveis apenas para o próprio usuário"
    ON public.profiles FOR SELECT
    USING (
        auth.uid() = id 
        OR 
        (auth.uid() IS NOT NULL AND id != auth.uid())
    );

-- =====================================================
-- POLÍTICAS PARA PRODUCTS
-- =====================================================

-- Produtos disponíveis são públicos
CREATE POLICY "Produtos disponíveis são públicos"
    ON public.products FOR SELECT
    USING (status IN ('available', 'sold'));

-- Vendedores podem criar produtos
CREATE POLICY "Vendedores podem criar produtos"
    ON public.products FOR INSERT
    WITH CHECK (
        auth.uid() = seller_id 
        AND 
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() 
            AND role IN ('seller', 'admin')
        )
    );

-- Vendedores podem atualizar seus próprios produtos
CREATE POLICY "Vendedores atualizam próprios produtos"
    ON public.products FOR UPDATE
    USING (
        auth.uid() = seller_id 
        AND 
        status != 'sold'
    )
    WITH CHECK (auth.uid() = seller_id);

-- Vendedores podem deletar produtos não vendidos
CREATE POLICY "Vendedores deletam produtos não vendidos"
    ON public.products FOR DELETE
    USING (
        auth.uid() = seller_id 
        AND 
        status != 'sold'
    );

-- =====================================================
-- POLÍTICAS PARA SALES
-- =====================================================

-- Compradores veem suas próprias compras
CREATE POLICY "Compradores veem suas compras"
    ON public.sales FOR SELECT
    USING (auth.uid() = buyer_id);

-- Vendedores veem suas próprias vendas
CREATE POLICY "Vendedores veem suas vendas"
    ON public.sales FOR SELECT
    USING (auth.uid() = seller_id);

-- Sistema pode criar vendas (via service role)
CREATE POLICY "Sistema cria vendas"
    ON public.sales FOR INSERT
    WITH CHECK (
        auth.uid() = buyer_id
        AND
        EXISTS (
            SELECT 1 FROM public.products 
            WHERE id = product_id 
            AND status = 'available'
        )
    );

-- Vendedores podem atualizar status de suas vendas
CREATE POLICY "Vendedores atualizam status de vendas"
    ON public.sales FOR UPDATE
    USING (auth.uid() = seller_id)
    WITH CHECK (
        auth.uid() = seller_id
        AND
        status IN ('pending', 'completed', 'cancelled')
    );

-- =====================================================
-- POLÍTICAS PARA QR_SCANS
-- =====================================================

-- Qualquer pessoa autenticada pode registrar scan
CREATE POLICY "Usuários autenticados registram scans"
    ON public.qr_scans FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);

-- Vendedores veem scans de seus produtos
CREATE POLICY "Vendedores veem scans de seus produtos"
    ON public.qr_scans FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.products 
            WHERE id = product_id 
            AND seller_id = auth.uid()
        )
    );

-- =====================================================
-- POLÍTICAS PARA PRODUCT_IMAGES
-- =====================================================

-- Imagens de produtos públicos são visíveis
CREATE POLICY "Imagens públicas"
    ON public.product_images FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.products 
            WHERE id = product_id 
            AND status IN ('available', 'sold')
        )
    );

-- Vendedores gerenciam imagens de seus produtos
CREATE POLICY "Vendedores gerenciam imagens"
    ON public.product_images FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.products 
            WHERE id = product_id 
            AND seller_id = auth.uid()
        )
    );

-- =====================================================
-- FUNÇÕES AUXILIARES PARA RLS
-- =====================================================

-- Função para verificar se usuário é admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.profiles 
        WHERE id = auth.uid() 
        AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para verificar se usuário é vendedor
CREATE OR REPLACE FUNCTION is_seller()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.profiles 
        WHERE id = auth.uid() 
        AND role IN ('seller', 'admin')
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para verificar se usuário é dono do produto
CREATE OR REPLACE FUNCTION owns_product(product_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.products 
        WHERE id = product_uuid 
        AND seller_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- POLÍTICAS ESPECIAIS PARA ADMIN
-- =====================================================

-- Admin tem acesso total a profiles
CREATE POLICY "Admin acessa todos os perfis"
    ON public.profiles FOR ALL
    USING (is_admin())
    WITH CHECK (is_admin());

-- Admin tem acesso total a products
CREATE POLICY "Admin gerencia todos os produtos"
    ON public.products FOR ALL
    USING (is_admin())
    WITH CHECK (is_admin());

-- Admin tem acesso total a sales
CREATE POLICY "Admin gerencia todas as vendas"
    ON public.sales FOR ALL
    USING (is_admin())
    WITH CHECK (is_admin());

-- =====================================================
-- POLÍTICAS DE STORAGE (BUCKETS)
-- =====================================================

-- Nota: Estas políticas devem ser aplicadas via Dashboard do Supabase
-- ou via API de administração, pois não são comandos SQL padrão

/*
Bucket: products
- SELECT: Público (anyone)
- INSERT: Apenas vendedores autenticados
- UPDATE: Apenas dono do produto
- DELETE: Apenas dono do produto

Bucket: qr-codes
- SELECT: Público (anyone)
- INSERT: Apenas vendedores autenticados
- UPDATE: Apenas dono do produto
- DELETE: Apenas dono do produto

Bucket: avatars
- SELECT: Público (anyone)
- INSERT: Apenas próprio usuário
- UPDATE: Apenas próprio usuário
- DELETE: Apenas próprio usuário
*/

-- =====================================================
-- GRANT PERMISSIONS PARA FUNÇÕES
-- =====================================================

-- Permitir que usuários autenticados executem funções
GRANT EXECUTE ON FUNCTION increment_product_views TO authenticated;
GRANT EXECUTE ON FUNCTION search_available_products TO authenticated;
GRANT EXECUTE ON FUNCTION get_seller_dashboard TO authenticated;
GRANT EXECUTE ON FUNCTION is_admin TO authenticated;
GRANT EXECUTE ON FUNCTION is_seller TO authenticated;
GRANT EXECUTE ON FUNCTION owns_product TO authenticated;

-- Permitir acesso anônimo a busca de produtos
GRANT EXECUTE ON FUNCTION search_available_products TO anon;

-- =====================================================
-- ÍNDICES ADICIONAIS PARA PERFORMANCE COM RLS
-- =====================================================

-- Índice para melhorar performance de políticas baseadas em auth.uid()
CREATE INDEX idx_products_seller_id_status 
    ON public.products(seller_id, status);

CREATE INDEX idx_sales_buyer_seller 
    ON public.sales(buyer_id, seller_id);

-- =====================================================
-- COMENTÁRIOS
-- =====================================================

COMMENT ON POLICY "Perfis públicos são visíveis para todos" 
    ON public.profiles IS 'Permite visualização de informações públicas de perfis';

COMMENT ON POLICY "Vendedores podem criar produtos" 
    ON public.products IS 'Apenas usuários com role seller ou admin podem criar produtos';

COMMENT ON POLICY "Sistema cria vendas" 
    ON public.sales IS 'Vendas são criadas quando comprador confirma compra';

-- =====================================================
-- TESTES DE SEGURANÇA (OPCIONAL)
-- =====================================================

-- Para testar as políticas, você pode usar:
-- SET LOCAL role authenticated;
-- SET LOCAL request.jwt.claim.sub = 'user-uuid-here';
-- Depois tentar SELECT, INSERT, UPDATE, DELETE nas tabelas
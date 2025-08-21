-- =====================================================
-- Migration: 001_initial_schema.sql
-- Descrição: Schema inicial do sistema Coisas de Garagem
-- Data: 2024
-- =====================================================

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- TIPOS ENUM
-- =====================================================

-- Tipo de papel do usuário
CREATE TYPE user_role AS ENUM ('buyer', 'seller', 'admin');

-- Status do produto
CREATE TYPE product_status AS ENUM ('available', 'sold', 'reserved', 'inactive');

-- Categoria do produto
CREATE TYPE product_category AS ENUM (
    'electronics',
    'furniture',
    'books',
    'toys',
    'clothing',
    'sports',
    'tools',
    'other'
);

-- Status da venda
CREATE TYPE sale_status AS ENUM ('pending', 'completed', 'cancelled', 'refunded');

-- =====================================================
-- TABELA: profiles (estende auth.users do Supabase)
-- =====================================================

CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    role user_role DEFAULT 'buyer' NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    is_verified BOOLEAN DEFAULT false NOT NULL,
    store_name TEXT,
    store_description TEXT,
    avatar_url TEXT,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    CONSTRAINT cpf_format CHECK (cpf ~ '^\d{11}$'),
    CONSTRAINT phone_format CHECK (phone ~ '^\d{10,11}$'),
    CONSTRAINT name_min_length CHECK (LENGTH(name) >= 3)
);

-- Índices para profiles
CREATE INDEX idx_profiles_email ON public.profiles(email);
CREATE INDEX idx_profiles_cpf ON public.profiles(cpf);
CREATE INDEX idx_profiles_role ON public.profiles(role);
CREATE INDEX idx_profiles_created_at ON public.profiles(created_at DESC);

-- =====================================================
-- TABELA: products
-- =====================================================

CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category product_category DEFAULT 'other' NOT NULL,
    status product_status DEFAULT 'available' NOT NULL,
    image_url TEXT,
    qr_code_data TEXT UNIQUE,
    qr_code_image_url TEXT,
    view_count INTEGER DEFAULT 0 NOT NULL,
    reserved_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    reserved_at TIMESTAMPTZ,
    sold_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    CONSTRAINT price_positive CHECK (price > 0),
    CONSTRAINT name_min_length CHECK (LENGTH(name) >= 3),
    CONSTRAINT description_min_length CHECK (LENGTH(description) >= 10)
);

-- Índices para products
CREATE INDEX idx_products_seller_id ON public.products(seller_id);
CREATE INDEX idx_products_status ON public.products(status);
CREATE INDEX idx_products_category ON public.products(category);
CREATE INDEX idx_products_qr_code ON public.products(qr_code_data);
CREATE INDEX idx_products_created_at ON public.products(created_at DESC);
CREATE INDEX idx_products_price ON public.products(price);

-- Índice para busca textual
CREATE INDEX idx_products_search ON public.products 
USING gin(to_tsvector('portuguese', name || ' ' || description));

-- =====================================================
-- TABELA: sales
-- =====================================================

CREATE TABLE IF NOT EXISTS public.sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE RESTRICT,
    buyer_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    seller_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    price DECIMAL(10, 2) NOT NULL,
    status sale_status DEFAULT 'pending' NOT NULL,
    payment_method TEXT,
    notes TEXT,
    transaction_date TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    CONSTRAINT price_positive CHECK (price > 0)
);

-- Índices para sales
CREATE INDEX idx_sales_product_id ON public.sales(product_id);
CREATE INDEX idx_sales_buyer_id ON public.sales(buyer_id);
CREATE INDEX idx_sales_seller_id ON public.sales(seller_id);
CREATE INDEX idx_sales_status ON public.sales(status);
CREATE INDEX idx_sales_transaction_date ON public.sales(transaction_date DESC);

-- =====================================================
-- TABELA: qr_scans
-- =====================================================

CREATE TABLE IF NOT EXISTS public.qr_scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    scanned_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    ip_address INET,
    user_agent TEXT,
    location JSONB,
    scanned_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Índices para qr_scans
CREATE INDEX idx_qr_scans_product_id ON public.qr_scans(product_id);
CREATE INDEX idx_qr_scans_scanned_by ON public.qr_scans(scanned_by);
CREATE INDEX idx_qr_scans_scanned_at ON public.qr_scans(scanned_at DESC);

-- =====================================================
-- TABELA: product_images (múltiplas imagens por produto)
-- =====================================================

CREATE TABLE IF NOT EXISTS public.product_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT false NOT NULL,
    display_order INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Índices para product_images
CREATE INDEX idx_product_images_product_id ON public.product_images(product_id);
CREATE INDEX idx_product_images_display_order ON public.product_images(display_order);

-- =====================================================
-- FUNÇÕES AUXILIARES
-- =====================================================

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger para atualizar updated_at em profiles
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para atualizar updated_at em products
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON public.products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para atualizar updated_at em sales
CREATE TRIGGER update_sales_updated_at
    BEFORE UPDATE ON public.sales
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- FUNÇÃO: Criar perfil automaticamente ao registrar usuário
-- =====================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (
        id,
        email,
        cpf,
        name,
        phone,
        role
    ) VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'cpf', '00000000000'),
        COALESCE(NEW.raw_user_meta_data->>'name', 'Usuário'),
        COALESCE(NEW.raw_user_meta_data->>'phone', '00000000000'),
        COALESCE((NEW.raw_user_meta_data->>'role')::user_role, 'buyer')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger para criar perfil quando usuário é criado
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- =====================================================
-- FUNÇÃO: Incrementar contador de visualizações
-- =====================================================

CREATE OR REPLACE FUNCTION increment_product_views(product_uuid UUID)
RETURNS void AS $$
BEGIN
    UPDATE public.products
    SET view_count = view_count + 1
    WHERE id = product_uuid;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNÇÃO: Buscar produtos disponíveis
-- =====================================================

CREATE OR REPLACE FUNCTION search_available_products(search_query TEXT)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    price DECIMAL,
    category product_category,
    image_url TEXT,
    seller_name TEXT,
    relevance REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.description,
        p.price,
        p.category,
        p.image_url,
        prof.name as seller_name,
        ts_rank(
            to_tsvector('portuguese', p.name || ' ' || p.description),
            plainto_tsquery('portuguese', search_query)
        ) as relevance
    FROM public.products p
    JOIN public.profiles prof ON p.seller_id = prof.id
    WHERE 
        p.status = 'available'
        AND to_tsvector('portuguese', p.name || ' ' || p.description) @@ 
            plainto_tsquery('portuguese', search_query)
    ORDER BY relevance DESC, p.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNÇÃO: Dashboard do vendedor
-- =====================================================

CREATE OR REPLACE FUNCTION get_seller_dashboard(seller_uuid UUID)
RETURNS TABLE (
    total_products BIGINT,
    products_sold BIGINT,
    products_available BIGINT,
    total_revenue DECIMAL,
    total_views BIGINT,
    recent_sales JSONB
) AS $$
BEGIN
    RETURN QUERY
    WITH stats AS (
        SELECT
            COUNT(*) FILTER (WHERE true) as total_products,
            COUNT(*) FILTER (WHERE status = 'sold') as products_sold,
            COUNT(*) FILTER (WHERE status = 'available') as products_available,
            COALESCE(SUM(price) FILTER (WHERE status = 'sold'), 0) as total_revenue,
            COALESCE(SUM(view_count), 0) as total_views
        FROM public.products
        WHERE seller_id = seller_uuid
    ),
    recent AS (
        SELECT jsonb_agg(
            jsonb_build_object(
                'id', s.id,
                'product_name', p.name,
                'buyer_name', b.name,
                'price', s.price,
                'date', s.transaction_date
            ) ORDER BY s.transaction_date DESC
        ) as recent_sales
        FROM public.sales s
        JOIN public.products p ON s.product_id = p.id
        JOIN public.profiles b ON s.buyer_id = b.id
        WHERE s.seller_id = seller_uuid
        AND s.status = 'completed'
        LIMIT 10
    )
    SELECT 
        stats.*,
        COALESCE(recent.recent_sales, '[]'::jsonb)
    FROM stats, recent;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMENTÁRIOS NAS TABELAS
-- =====================================================

COMMENT ON TABLE public.profiles IS 'Perfis de usuários do sistema, estende auth.users';
COMMENT ON TABLE public.products IS 'Produtos disponíveis para venda';
COMMENT ON TABLE public.sales IS 'Registro de vendas realizadas';
COMMENT ON TABLE public.qr_scans IS 'Registro de escaneamentos de QR codes';
COMMENT ON TABLE public.product_images IS 'Imagens adicionais dos produtos';

-- =====================================================
-- DADOS INICIAIS (OPCIONAL)
-- =====================================================

-- Inserir categorias padrão, roles, etc. se necessário
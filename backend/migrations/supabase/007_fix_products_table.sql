-- =====================================================
-- Migration: 007_fix_products_table.sql
-- Descrição: Adicionar colunas faltantes na tabela products
-- Data: 2024
-- =====================================================

-- Adicionar coluna quantity
ALTER TABLE public.products 
ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1 NOT NULL CHECK (quantity > 0);

-- Adicionar coluna images como JSONB para suportar múltiplas imagens
ALTER TABLE public.products 
ADD COLUMN IF NOT EXISTS images JSONB DEFAULT '[]'::jsonb;

-- Adicionar coluna deleted_at para soft delete
ALTER TABLE public.products 
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- Criar índice para queries de produtos não deletados
CREATE INDEX IF NOT EXISTS idx_products_deleted_at ON public.products(deleted_at) WHERE deleted_at IS NULL;

-- Comentários nas novas colunas
COMMENT ON COLUMN public.products.quantity IS 'Quantidade disponível do produto';
COMMENT ON COLUMN public.products.images IS 'Array de URLs das imagens do produto';
COMMENT ON COLUMN public.products.deleted_at IS 'Data de soft delete do produto';
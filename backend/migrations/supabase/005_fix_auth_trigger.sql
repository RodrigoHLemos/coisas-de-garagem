-- =====================================================
-- Migration: 005_fix_auth_trigger.sql
-- Descrição: Corrige trigger para criar perfil automaticamente
-- Data: 2025
-- =====================================================

-- Remover trigger e função antigas se existirem
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users CASCADE;
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;

-- Criar função melhorada para criar perfil
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    user_metadata jsonb;
BEGIN
    -- Obter metadata do usuário
    user_metadata := NEW.raw_user_meta_data;
    
    -- Criar perfil na tabela public.profiles
    INSERT INTO public.profiles (
        id,
        email,
        name,
        cpf,
        phone,
        role,
        is_active,
        is_verified,
        created_at,
        updated_at
    ) VALUES (
        NEW.id,
        NEW.email,
        COALESCE(user_metadata->>'name', ''),
        COALESCE(user_metadata->>'cpf', ''),
        COALESCE(user_metadata->>'phone', ''),
        COALESCE(user_metadata->>'role', 'buyer'),
        true,
        false,
        NOW(),
        NOW()
    ) ON CONFLICT (id) DO NOTHING; -- Evita erro se perfil já existe
    
    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        -- Log do erro mas não falha o registro
        RAISE WARNING 'Erro ao criar perfil para usuário %: %', NEW.id, SQLERRM;
        RETURN NEW;
END;
$$;

-- Criar trigger no schema auth
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Grant necessário para a função acessar a tabela profiles
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON public.profiles TO postgres, service_role;
GRANT SELECT, INSERT, UPDATE ON public.profiles TO anon, authenticated;

-- Criar perfis para usuários existentes que não tenham perfil
INSERT INTO public.profiles (id, email, name, cpf, phone, role, is_active, is_verified)
SELECT 
    au.id,
    au.email,
    COALESCE(au.raw_user_meta_data->>'name', ''),
    COALESCE(au.raw_user_meta_data->>'cpf', ''),
    COALESCE(au.raw_user_meta_data->>'phone', ''),
    COALESCE(au.raw_user_meta_data->>'role', 'buyer'),
    true,
    false
FROM auth.users au
LEFT JOIN public.profiles p ON p.id = au.id
WHERE p.id IS NULL;

-- Verificar se a trigger foi criada
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_trigger 
        WHERE tgname = 'on_auth_user_created'
    ) THEN
        RAISE NOTICE 'Trigger on_auth_user_created criada com sucesso!';
    ELSE
        RAISE WARNING 'Trigger on_auth_user_created NÃO foi criada!';
    END IF;
END $$;
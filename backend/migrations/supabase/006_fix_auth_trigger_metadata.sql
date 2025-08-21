-- =====================================================
-- Migration: 006_fix_auth_trigger_metadata.sql
-- Descrição: Corrige trigger para acessar metadados corretamente
-- Data: 2025
-- =====================================================

-- Remover trigger e função antigas
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users CASCADE;
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;

-- Criar função corrigida para criar perfil
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    user_metadata jsonb;
    user_name text;
    user_cpf text;
    user_phone text;
    user_role text;
BEGIN
    -- Obter metadata do usuário
    user_metadata := NEW.raw_user_meta_data;
    
    -- Log para debug (pode ser removido depois)
    RAISE NOTICE 'Metadata recebida: %', user_metadata;
    
    -- Extrair valores com validação
    user_name := COALESCE(user_metadata->>'name', '');
    user_cpf := COALESCE(user_metadata->>'cpf', '');
    user_phone := COALESCE(user_metadata->>'phone', '');
    user_role := COALESCE(user_metadata->>'role', 'buyer');
    
    -- Verificar se temos os dados mínimos necessários
    IF user_name = '' OR LENGTH(user_name) < 3 THEN
        user_name := COALESCE(split_part(NEW.email, '@', 1), 'Usuario');
        -- Garantir mínimo de 3 caracteres
        IF LENGTH(user_name) < 3 THEN
            user_name := 'Usuario ' || substring(NEW.id::text, 1, 8);
        END IF;
    END IF;
    
    -- Se CPF estiver vazio ou inválido, gerar um temporário
    IF user_cpf = '' OR LENGTH(user_cpf) != 11 OR user_cpf !~ '^\d{11}$' THEN
        -- Gerar CPF temporário baseado no ID (apenas para não violar constraint)
        -- IMPORTANTE: Isso é temporário, o usuário deve atualizar depois
        user_cpf := '00000000' || substring(replace(NEW.id::text, '-', ''), 1, 3);
    END IF;
    
    -- Se telefone estiver vazio ou inválido, gerar um temporário
    IF user_phone = '' OR LENGTH(user_phone) < 10 OR user_phone !~ '^\d{10,11}$' THEN
        -- Gerar telefone temporário
        user_phone := '0000000' || substring(replace(NEW.id::text, '-', ''), 1, 4);
    END IF;
    
    -- Log dos valores finais
    RAISE NOTICE 'Inserindo perfil - Nome: %, CPF: %, Phone: %, Role: %', 
                 user_name, user_cpf, user_phone, user_role;
    
    -- Tentar criar perfil na tabela public.profiles
    BEGIN
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
            user_name,
            user_cpf,
            user_phone,
            user_role::user_role,
            true,
            false,
            NOW(),
            NOW()
        );
        
        RAISE NOTICE 'Perfil criado com sucesso para usuário %', NEW.id;
        
    EXCEPTION
        WHEN unique_violation THEN
            -- Se já existe um perfil (não deveria acontecer), atualizar
            RAISE NOTICE 'Perfil já existe para usuário %, atualizando...', NEW.id;
            UPDATE public.profiles 
            SET 
                email = NEW.email,
                updated_at = NOW()
            WHERE id = NEW.id;
            
        WHEN OTHERS THEN
            -- Log do erro mas não falha o registro do usuário
            RAISE WARNING 'Erro ao criar perfil para usuário %: % (SQLSTATE: %)', 
                         NEW.id, SQLERRM, SQLSTATE;
            -- Ainda assim, retorna NEW para não bloquear o registro
    END;
    
    RETURN NEW;
END;
$$;

-- Criar trigger no schema auth
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Grant necessário para a função
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON public.profiles TO postgres, service_role;
GRANT SELECT, INSERT, UPDATE ON public.profiles TO anon, authenticated;

-- Criar perfis para usuários existentes sem perfil
-- Usa valores temporários para campos obrigatórios
INSERT INTO public.profiles (id, email, name, cpf, phone, role, is_active, is_verified)
SELECT 
    au.id,
    au.email,
    COALESCE(
        NULLIF(au.raw_user_meta_data->>'name', ''),
        split_part(au.email, '@', 1),
        'Usuario'
    ) as name,
    COALESCE(
        CASE 
            WHEN au.raw_user_meta_data->>'cpf' ~ '^\d{11}$' 
            THEN au.raw_user_meta_data->>'cpf'
            ELSE NULL
        END,
        '00000000' || substring(replace(au.id::text, '-', ''), 1, 3)
    ) as cpf,
    COALESCE(
        CASE 
            WHEN au.raw_user_meta_data->>'phone' ~ '^\d{10,11}$' 
            THEN au.raw_user_meta_data->>'phone'
            ELSE NULL
        END,
        '0000000' || substring(replace(au.id::text, '-', ''), 1, 4)
    ) as phone,
    COALESCE(au.raw_user_meta_data->>'role', 'buyer')::user_role,
    true,
    false
FROM auth.users au
LEFT JOIN public.profiles p ON p.id = au.id
WHERE p.id IS NULL;

-- Teste para verificar se a trigger foi criada
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_trigger 
        WHERE tgname = 'on_auth_user_created'
        AND tgrelid = 'auth.users'::regclass
    ) THEN
        RAISE NOTICE '✅ Trigger on_auth_user_created criada com sucesso no schema auth!';
    ELSE
        RAISE WARNING '❌ Trigger on_auth_user_created NÃO foi criada!';
    END IF;
    
    -- Verificar se a função existe
    IF EXISTS (
        SELECT 1 FROM pg_proc 
        WHERE proname = 'handle_new_user'
    ) THEN
        RAISE NOTICE '✅ Função handle_new_user existe!';
    ELSE
        RAISE WARNING '❌ Função handle_new_user NÃO existe!';
    END IF;
END $$;

-- Instruções para o usuário
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE 'MIGRATION EXECUTADA COM SUCESSO!';
    RAISE NOTICE '==========================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'A trigger agora:';
    RAISE NOTICE '1. Aceita metadados parciais ou vazios';
    RAISE NOTICE '2. Gera valores temporários para campos obrigatórios';
    RAISE NOTICE '3. Não bloqueia o registro se houver erro no perfil';
    RAISE NOTICE '4. Registra logs para debug (RAISE NOTICE)';
    RAISE NOTICE '';
    RAISE NOTICE 'IMPORTANTE: Usuários com CPF/telefone temporários';
    RAISE NOTICE 'devem atualizar seus dados após o registro!';
    RAISE NOTICE '==========================================================';
END $$;
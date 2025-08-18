-- =====================================================
-- Migration: 004_auth_trigger.sql
-- Descrição: Trigger para criar perfil automaticamente após registro
-- Data: 2024
-- =====================================================

-- Função para criar perfil automaticamente
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (
    id,
    email,
    name,
    cpf,
    phone,
    role,
    is_active,
    is_verified
  )
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', ''),
    COALESCE(NEW.raw_user_meta_data->>'cpf', ''),
    COALESCE(NEW.raw_user_meta_data->>'phone', ''),
    COALESCE(NEW.raw_user_meta_data->>'role', 'buyer'),
    true,
    false
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Remover trigger se existir
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Criar trigger
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
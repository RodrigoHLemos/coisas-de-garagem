#!/usr/bin/env python3
"""
Script para testar diretamente a API do Supabase.
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("=" * 60)
print("🔍 DIAGNÓSTICO SUPABASE")
print("=" * 60)
print(f"URL: {SUPABASE_URL}")
print(f"Anon Key: {SUPABASE_ANON_KEY[:20]}...")
print(f"Service Key: {SUPABASE_SERVICE_KEY[:20]}...")
print()

async def test_tables():
    """Verifica se a tabela profiles existe."""
    print("📊 VERIFICANDO TABELAS...")
    print("-" * 40)
    
    async with httpx.AsyncClient() as client:
        # Verificar tabela profiles
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/profiles",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"
            },
            params={"limit": 1}
        )
        
        if response.status_code == 200:
            print("✅ Tabela 'profiles' existe")
            profiles = response.json()
            print(f"   Registros encontrados: {len(profiles)}")
        else:
            print("❌ Erro ao acessar tabela 'profiles'")
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
    
    print()

async def test_direct_signup():
    """Testa signup direto no Supabase."""
    print("🔐 TESTANDO SIGNUP DIRETO...")
    print("-" * 40)
    
    import random
    import string
    
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_email = f"direct_test_{random_suffix}@exemplo.com"
    
    print(f"Email: {test_email}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={
                "email": test_email,
                "password": "TestPassword123!",
                "data": {
                    "name": "Direct Test User",
                    "cpf": "12345678901",
                    "phone": "11999999999",
                    "role": "buyer"
                }
            }
        )
        
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print(f"Resposta: {json.dumps(data, indent=2)}")
        
        if response.status_code in (200, 201):
            print("✅ Signup funcionou!")
            
            # Verificar se o perfil foi criado
            user_id = data.get("user", {}).get("id")
            if user_id:
                await asyncio.sleep(2)  # Aguardar trigger
                
                print("\n🔍 Verificando perfil criado...")
                profile_response = await client.get(
                    f"{SUPABASE_URL}/rest/v1/profiles",
                    headers={
                        "apikey": SUPABASE_SERVICE_KEY,
                        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"
                    },
                    params={"id": f"eq.{user_id}"}
                )
                
                if profile_response.status_code == 200:
                    profiles = profile_response.json()
                    if profiles:
                        print("✅ Perfil criado automaticamente!")
                        print(f"   Perfil: {json.dumps(profiles[0], indent=2)}")
                    else:
                        print("❌ Perfil NÃO foi criado automaticamente")
                        print("   A trigger pode não estar funcionando")
        else:
            print("❌ Erro no signup")
    
    print()

async def check_trigger():
    """Verifica se a trigger existe no banco."""
    print("🔧 VERIFICANDO TRIGGER...")
    print("-" * 40)
    
    async with httpx.AsyncClient() as client:
        # Query para verificar triggers
        sql_query = """
        SELECT 
            trigger_name,
            event_manipulation,
            event_object_table,
            action_statement
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
        AND trigger_name = 'on_auth_user_created';
        """
        
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/sql",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            },
            json={"query": sql_query}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result:
                print("✅ Trigger 'on_auth_user_created' encontrada!")
            else:
                print("❌ Trigger NÃO encontrada")
                print("   Execute a migration 004_auth_trigger.sql")
        else:
            # Tentar método alternativo
            print("⚠️ Não foi possível verificar trigger diretamente")
            print("   Verifique manualmente no Supabase Dashboard")
    
    print()

async def main():
    """Executa todos os testes."""
    try:
        await test_tables()
        await check_trigger()
        await test_direct_signup()
        
        print("=" * 60)
        print("📋 RESUMO")
        print("=" * 60)
        print()
        print("Se o perfil NÃO foi criado automaticamente:")
        print("1. Verifique se a migration foi executada corretamente")
        print("2. No SQL Editor do Supabase, execute:")
        print("   SELECT * FROM information_schema.triggers")
        print("   WHERE trigger_schema = 'public';")
        print()
        print("3. Verifique se existe a trigger 'on_auth_user_created'")
        print()
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    asyncio.run(main())
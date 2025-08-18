#!/usr/bin/env python3
"""
Script para testar autenticação com Supabase.
Execute: python tests/test_auth.py
"""
import asyncio
import httpx
import json
import sys
from datetime import datetime
import random
import string

# URL base da API
BASE_URL = "http://localhost:8000/api/v1"

# Gerar dados aleatórios para teste
def generate_test_data():
    """Gera dados de teste únicos."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    return {
        "email": f"teste_{random_suffix}@exemplo.com",
        "password": "SenhaForte123!",
        "name": f"Teste User {random_suffix}",
        "cpf": "".join(random.choices(string.digits, k=11)),
        "phone": "11" + "".join(random.choices(string.digits, k=9)),
        "role": "seller"
    }

async def test_register():
    """Testa registro de novo usuário."""
    print("\n🔵 TESTANDO REGISTRO...")
    print("-" * 50)
    
    test_data = generate_test_data()
    
    print(f"📧 Email: {test_data['email']}")
    print(f"👤 Nome: {test_data['name']}")
    print(f"📱 CPF: {test_data['cpf']}")
    print(f"📞 Telefone: {test_data['phone']}")
    print(f"🎭 Role: {test_data['role']}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/auth/register",
                json=test_data,
                timeout=10.0
            )
            
            print(f"\n📊 Status Code: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print("✅ REGISTRO BEM-SUCEDIDO!")
                print(f"   ID: {data.get('id')}")
                print(f"   Email: {data.get('email')}")
                print(f"   Verificado: {data.get('is_verified')}")
                return test_data  # Retorna para usar no login
            else:
                print(f"❌ ERRO NO REGISTRO:")
                print(f"   {response.text}")
                return None
                
        except httpx.RequestError as e:
            print(f"❌ ERRO DE CONEXÃO: {e}")
            return None
        except Exception as e:
            print(f"❌ ERRO: {e}")
            return None

async def test_login(email: str, password: str):
    """Testa login de usuário."""
    print("\n🔵 TESTANDO LOGIN...")
    print("-" * 50)
    print(f"📧 Email: {email}")
    
    async with httpx.AsyncClient() as client:
        try:
            # O endpoint espera form-data para OAuth2
            response = await client.post(
                f"{BASE_URL}/auth/login",
                data={
                    "username": email,
                    "password": password
                },
                timeout=10.0
            )
            
            print(f"\n📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ LOGIN BEM-SUCEDIDO!")
                print(f"   Token Type: {data.get('token_type')}")
                print(f"   Expires In: {data.get('expires_in')} segundos")
                print(f"   Access Token: {data.get('access_token')[:50]}...")
                return data.get('access_token')
            else:
                print(f"❌ ERRO NO LOGIN:")
                print(f"   {response.text}")
                return None
                
        except httpx.RequestError as e:
            print(f"❌ ERRO DE CONEXÃO: {e}")
            return None
        except Exception as e:
            print(f"❌ ERRO: {e}")
            return None

async def test_protected_route(token: str):
    """Testa acesso a rota protegida."""
    print("\n🔵 TESTANDO ROTA PROTEGIDA...")
    print("-" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/users/profile",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ ACESSO AUTORIZADO!")
                print(f"   ID: {data.get('id')}")
                print(f"   Email: {data.get('email')}")
                print(f"   Nome: {data.get('name')}")
            else:
                print(f"❌ ACESSO NEGADO:")
                print(f"   {response.text}")
                
        except httpx.RequestError as e:
            print(f"❌ ERRO DE CONEXÃO: {e}")
        except Exception as e:
            print(f"❌ ERRO: {e}")

async def test_duplicate_registration():
    """Testa registro duplicado."""
    print("\n🔵 TESTANDO REGISTRO DUPLICADO...")
    print("-" * 50)
    
    # Usar email fixo para testar duplicação
    test_data = {
        "email": "duplicado@teste.com",
        "password": "SenhaForte123!",
        "name": "Usuario Duplicado",
        "cpf": "12345678901",
        "phone": "11999999999",
        "role": "buyer"
    }
    
    async with httpx.AsyncClient() as client:
        # Primeiro registro
        print("1️⃣ Primeiro registro...")
        response1 = await client.post(
            f"{BASE_URL}/auth/register",
            json=test_data,
            timeout=10.0
        )
        
        # Segundo registro (deve falhar)
        print("2️⃣ Tentando registrar novamente...")
        response2 = await client.post(
            f"{BASE_URL}/auth/register",
            json=test_data,
            timeout=10.0
        )
        
        if response2.status_code == 400:
            print("✅ DUPLICAÇÃO BLOQUEADA CORRETAMENTE!")
            print(f"   Mensagem: {response2.text}")
        else:
            print("❌ ERRO: Permitiu registro duplicado!")

async def test_invalid_login():
    """Testa login com credenciais inválidas."""
    print("\n🔵 TESTANDO LOGIN INVÁLIDO...")
    print("-" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": "naoexiste@teste.com",
                "password": "senhaerrada"
            },
            timeout=10.0
        )
        
        if response.status_code == 401:
            print("✅ LOGIN INVÁLIDO BLOQUEADO CORRETAMENTE!")
            print(f"   Status: {response.status_code}")
            print(f"   Mensagem: {response.text}")
        else:
            print("❌ ERRO: Login inválido não foi bloqueado!")

async def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("🧪 TESTE DE AUTENTICAÇÃO - COISAS DE GARAGEM")
    print("=" * 60)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL Base: {BASE_URL}")
    
    # Verificar se o servidor está rodando
    print("\n🔍 Verificando servidor...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/docs", timeout=5.0)
            if response.status_code == 200:
                print("✅ Servidor está rodando!")
            else:
                print("⚠️ Servidor respondeu com status:", response.status_code)
    except:
        print("❌ ERRO: Servidor não está respondendo!")
        print("   Execute: uvicorn app.main:app --reload")
        return
    
    # Executar testes
    print("\n" + "=" * 60)
    print("INICIANDO TESTES")
    print("=" * 60)
    
    # Teste 1: Registro
    user_data = await test_register()
    
    # Teste 2: Login (se registro funcionou)
    token = None
    if user_data:
        await asyncio.sleep(1)  # Aguardar um pouco
        token = await test_login(user_data["email"], user_data["password"])
    
    # Teste 3: Rota protegida (se login funcionou)
    if token:
        await asyncio.sleep(1)
        await test_protected_route(token)
    
    # Teste 4: Registro duplicado
    await test_duplicate_registration()
    
    # Teste 5: Login inválido
    await test_invalid_login()
    
    print("\n" + "=" * 60)
    print("🏁 TESTES CONCLUÍDOS!")
    print("=" * 60)

if __name__ == "__main__":
    # Executar testes
    asyncio.run(main())
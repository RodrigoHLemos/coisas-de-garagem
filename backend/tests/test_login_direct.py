#!/usr/bin/env python3
"""
Teste direto de login no Supabase
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv
import json

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

async def test_login():
    """Testa login direto no Supabase."""
    
    # Primeiro criar um usuário
    email = "test_login@exemplo.com"
    password = "TestPassword123!"
    
    print("1️⃣ Criando usuário de teste...")
    async with httpx.AsyncClient() as client:
        # Signup
        signup_response = await client.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={
                "email": email,
                "password": password,
                "data": {
                    "name": "Test Login User",
                    "cpf": "12345678901",
                    "phone": "11999999999",
                    "role": "buyer"
                }
            }
        )
        
        print(f"Signup status: {signup_response.status_code}")
        
        # Aguardar um pouco
        await asyncio.sleep(2)
        
        print("\n2️⃣ Testando login...")
        
        # Teste 1: Login com grant_type=password
        login_response = await client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={
                "email": email,
                "password": password
            }
        )
        
        print(f"Login status: {login_response.status_code}")
        print(f"Login response: {json.dumps(login_response.json(), indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_login())
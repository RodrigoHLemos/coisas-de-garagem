#!/usr/bin/env python3
"""
Script para testar se o ambiente está configurado corretamente.
Execute: python test_setup.py
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Testar se todos os módulos podem ser importados"""
    print("🔍 Testando importações...")
    
    modules_to_test = [
        ("FastAPI", "fastapi"),
        ("Pydantic", "pydantic"),
        ("Supabase", "supabase"),
        ("SQLAlchemy", "sqlalchemy"),
        ("Uvicorn", "uvicorn"),
        ("QRCode", "qrcode"),
        ("PIL", "PIL"),
        ("Redis", "redis"),
    ]
    
    failed = []
    for name, module in modules_to_test:
        try:
            __import__(module)
            print(f"  ✅ {name} ({module})")
        except ImportError as e:
            print(f"  ❌ {name} ({module}): {e}")
            failed.append(name)
    
    return len(failed) == 0

def test_env_file():
    """Verificar se arquivo .env existe"""
    print("\n📁 Verificando arquivo .env...")
    
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if env_file.exists():
        print(f"  ✅ Arquivo .env encontrado")
        
        # Verificar variáveis importantes
        with open(env_file) as f:
            content = f.read()
            
        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_KEY",
            "DATABASE_URL",
            "SECRET_KEY"
        ]
        
        print("\n  Verificando variáveis obrigatórias:")
        missing = []
        for var in required_vars:
            if f"{var}=" in content:
                # Verificar se não está com valor padrão
                line_with_var = [line for line in content.split('\n') if f"{var}=" in line]
                if line_with_var:
                    value = line_with_var[0].split('=', 1)[1]
                    if "seu-projeto" in value or "sua-" in value or "your-" in value or "[YOUR-" in value or "[SUA-" in value:
                        print(f"    ⚠️  {var} - encontrada mas com valor padrão")
                        missing.append(var)
                else:
                    print(f"    ✅ {var}")
            else:
                print(f"    ❌ {var} - não encontrada")
                missing.append(var)
        
        if missing:
            print(f"\n  ⚠️  Configure as variáveis: {', '.join(missing)}")
            return False
        return True
    else:
        print(f"  ❌ Arquivo .env não encontrado")
        if env_example.exists():
            print(f"  💡 Execute: cp .env.example .env")
        return False

def test_app_import():
    """Testar se a aplicação pode ser importada"""
    print("\n🚀 Testando aplicação FastAPI...")
    
    try:
        from app.main import app
        print(f"  ✅ Aplicação importada com sucesso")
        print(f"     Título: {app.title}")
        print(f"     Versão: {app.version}")
        return True
    except ImportError as e:
        print(f"  ❌ Erro ao importar aplicação: {e}")
        return False
    except Exception as e:
        print(f"  ⚠️  Aplicação importada mas com erro: {e}")
        print(f"     Provavelmente faltam configurações no .env")
        return False

def test_supabase_config():
    """Testar configuração do Supabase"""
    print("\n🔌 Testando configuração Supabase...")
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        if hasattr(settings, 'supabase'):
            print(f"  ✅ Configurações Supabase encontradas")
            
            # Verificar se não são valores padrão
            if "seu-projeto" in settings.supabase.url:
                print(f"  ⚠️  URL do Supabase ainda com valor padrão")
                return False
            else:
                print(f"  ✅ URL configurada")
            return True
        else:
            print(f"  ❌ Configurações Supabase não encontradas")
            return False
    except Exception as e:
        print(f"  ❌ Erro ao carregar configurações: {e}")
        return False

def main():
    """Executar todos os testes"""
    print("=" * 50)
    print("🧪 TESTE DE CONFIGURAÇÃO DO AMBIENTE")
    print("=" * 50)
    
    results = []
    
    # Testar importações
    results.append(("Importações", test_imports()))
    
    # Testar arquivo .env
    results.append(("Arquivo .env", test_env_file()))
    
    # Testar importação da app
    results.append(("Aplicação FastAPI", test_app_import()))
    
    # Testar Supabase se .env existir
    if Path(__file__).parent.joinpath(".env").exists():
        results.append(("Configuração Supabase", test_supabase_config()))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 AMBIENTE CONFIGURADO COM SUCESSO!")
        print("\nPróximos passos:")
        print("1. Configure as credenciais do Supabase no .env")
        print("2. Execute as migrations no Supabase Dashboard")
        print("3. Inicie o servidor: uvicorn app.main:app --reload")
    else:
        print("⚠️  CONFIGURAÇÃO INCOMPLETA")
        print("\nVerifique os erros acima e:")
        print("1. Instale dependências faltantes: pip install -r requirements.txt")
        print("2. Configure o arquivo .env com suas credenciais")
        print("3. Crie um projeto no Supabase se ainda não tiver")
    
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
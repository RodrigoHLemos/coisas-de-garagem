#!/bin/bash

echo "==========================================="
echo "🚀 SETUP DE AUTENTICAÇÃO - COISAS DE GARAGEM"
echo "==========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 INSTRUÇÕES PARA CONFIGURAR AUTENTICAÇÃO${NC}"
echo ""
echo "1. EXECUTAR MIGRATION NO SUPABASE:"
echo "   --------------------------------"
echo "   a) Acesse o Supabase Dashboard: https://supabase.com/dashboard"
echo "   b) Selecione seu projeto"
echo "   c) Vá para SQL Editor (ícone de banco de dados)"
echo "   d) Cole o conteúdo do arquivo: migrations/supabase/004_auth_trigger.sql"
echo "   e) Clique em 'Run' para executar"
echo ""
echo -e "${GREEN}✅ A migration criará:${NC}"
echo "   - Função handle_new_user() para criar perfil automaticamente"
echo "   - Trigger que executa após novo usuário registrar"
echo ""

read -p "Você já executou a migration? (s/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]
then
    echo -e "${RED}❌ Execute a migration primeiro antes de continuar!${NC}"
    echo "   Arquivo: backend/migrations/supabase/004_auth_trigger.sql"
    exit 1
fi

echo ""
echo -e "${YELLOW}🔧 VERIFICANDO AMBIENTE...${NC}"
echo ""

# Verificar se está no diretório backend
if [ ! -f "app/main.py" ]; then
    echo -e "${RED}❌ Execute este script do diretório backend/${NC}"
    exit 1
fi

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Ambiente configurado${NC}"
echo ""

# Verificar se servidor está rodando
echo -e "${YELLOW}🔍 Verificando servidor...${NC}"
curl -s http://localhost:8000/docs > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Servidor não está rodando!${NC}"
    echo ""
    echo "Iniciando servidor em segundo plano..."
    nohup uvicorn app.main:app --reload > server.log 2>&1 &
    SERVER_PID=$!
    echo "PID do servidor: $SERVER_PID"
    echo "Aguardando servidor iniciar..."
    sleep 5
    
    # Verificar novamente
    curl -s http://localhost:8000/docs > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Falha ao iniciar servidor!${NC}"
        echo "Verifique server.log para erros"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Servidor está rodando${NC}"
fi

echo ""
echo "==========================================="
echo -e "${YELLOW}🧪 EXECUTANDO TESTES DE AUTENTICAÇÃO${NC}"
echo "==========================================="
echo ""

# Executar testes
python tests/test_auth.py

echo ""
echo "==========================================="
echo -e "${GREEN}📊 RESUMO${NC}"
echo "==========================================="
echo ""
echo "✅ Migration: Executada no Supabase"
echo "✅ Servidor: Rodando em http://localhost:8000"
echo "✅ Documentação: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}🎯 PRÓXIMOS PASSOS:${NC}"
echo ""
echo "1. Se os testes passaram:"
echo "   - Sistema de autenticação está funcionando!"
echo "   - Você pode testar manualmente em http://localhost:8000/docs"
echo ""
echo "2. Se houve erros:"
echo "   - Verifique se a migration foi executada corretamente"
echo "   - Confirme as credenciais no arquivo .env"
echo "   - Verifique server.log para erros do servidor"
echo ""
echo "==========================================="
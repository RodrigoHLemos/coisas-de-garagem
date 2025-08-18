# 🚀 Guia Rápido - Coisas de Garagem Backend

## 1. Instalação Rápida

### Pré-requisitos
- Python 3.11+ instalado
- Conta no Supabase (grátis em https://supabase.com)

### Passos

```bash
# 1. Entrar no diretório backend
cd backend

# 2. Criar ambiente virtual
python3 -m venv venv

# 3. Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Criar arquivo de configuração
cp .env.example .env
```

## 2. Configurar Supabase

### Criar Projeto
1. Acesse https://supabase.com
2. Clique em "New Project"
3. Configure:
   - **Nome**: coisas-de-garagem
   - **Senha do banco**: (salve esta senha!)
   - **Região**: São Paulo

### Obter Credenciais
No dashboard do Supabase, vá em **Settings > API** e copie:
- Project URL
- Anon Key
- Service Role Key

### Configurar .env
Edite o arquivo `.env` com suas credenciais:

```env
# OBRIGATÓRIO - Substitua com suas credenciais
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=eyJ...sua-anon-key...
SUPABASE_SERVICE_KEY=eyJ...sua-service-key...

# Banco de dados - pegue em Settings > Database
DATABASE_URL=postgresql+asyncpg://postgres:[SUA-SENHA]@db.[SEU-PROJETO].supabase.co:5432/postgres

# Segurança - gere uma chave forte
SECRET_KEY=gere-uma-chave-secreta-forte-aqui

# JWT Secret - pegue em Settings > API > JWT Settings
SUPABASE_JWT_SECRET=seu-jwt-secret
```

### Executar Migrations
1. No Supabase Dashboard, vá para **SQL Editor**
2. Execute cada arquivo em ordem:
   - `migrations/supabase/001_initial_schema.sql`
   - `migrations/supabase/002_row_level_security.sql`
   - `migrations/supabase/003_storage_setup.sql`

### Criar Storage Buckets
No Dashboard > Storage, crie 3 buckets públicos:
- `products`
- `qr-codes`
- `avatars`

## 3. Testar Instalação

```bash
# Testar configuração
python test_setup.py

# Se tudo OK, iniciar servidor
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs

## 4. Comandos Úteis

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Iniciar servidor desenvolvimento
uvicorn app.main:app --reload

# Iniciar com logs detalhados
uvicorn app.main:app --reload --log-level debug

# Rodar testes
pytest tests/

# Formatar código
black app/

# Verificar tipos
mypy app/
```

## 5. Testar API

### Registrar Usuário
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "password": "Senha123!",
    "name": "João Silva",
    "cpf": "11144477735",
    "phone": "11999999999",
    "role": "buyer"
  }'
```

### Fazer Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teste@exemplo.com",
    "password": "Senha123!"
  }'
```

## 6. Estrutura do Projeto

```
backend/
├── app/
│   ├── api/           # Endpoints REST
│   ├── core/          # Configurações
│   ├── domain/        # Lógica de negócio
│   ├── infrastructure/# Banco e storage
│   ├── services/      # Serviços
│   └── shared/        # Utilitários
├── migrations/        # Scripts SQL
├── tests/            # Testes
├── .env              # Configurações (não commitpar)
└── requirements.txt  # Dependências
```

## 7. Troubleshooting

### Erro: ModuleNotFoundError
```bash
# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: Supabase connection failed
- Verifique credenciais no .env
- Confirme que projeto existe no Supabase

### Erro: Table não existe
- Execute migrations no SQL Editor
- Verifique ordem: 001 → 002 → 003

### Erro: Permission denied
- Verifique políticas RLS
- Use Service Role Key para admin

## 8. Próximos Passos

1. ✅ Backend configurado
2. 📝 Implementar endpoints faltantes
3. 🎨 Conectar frontend
4. 🚀 Deploy

## Links Úteis

- [Documentação Completa](docs/ARQUITETURA.md)
- [Supabase Dashboard](https://app.supabase.com)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Supabase Docs](https://supabase.com/docs)

---

**Dúvidas?** Veja a documentação completa em `/docs`
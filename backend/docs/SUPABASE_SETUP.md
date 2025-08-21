# Guia de Configuração do Supabase

## 📋 Índice
1. [Criar Projeto no Supabase](#1-criar-projeto-no-supabase)
2. [Configurar Banco de Dados](#2-configurar-banco-de-dados)
3. [Configurar Autenticação](#3-configurar-autenticação)
4. [Configurar Storage](#4-configurar-storage)
5. [Configurar Variáveis de Ambiente](#5-configurar-variáveis-de-ambiente)
6. [Testar Integração](#6-testar-integração)

## 1. Criar Projeto no Supabase

### Passo 1: Criar Conta
1. Acesse [https://supabase.com](https://supabase.com)
2. Clique em "Start your project"
3. Faça login com GitHub ou crie uma conta

### Passo 2: Criar Novo Projeto
1. Clique em "New Project"
2. Preencha os dados:
   - **Name**: `coisas-de-garagem`
   - **Database Password**: Gere uma senha forte (SALVE ESTA SENHA!)
   - **Region**: São Paulo (`sa-east-1`) para melhor latência no Brasil
   - **Pricing Plan**: Free tier para começar

3. Clique em "Create new project" e aguarde ~2 minutos

### Passo 3: Obter Credenciais
No dashboard do projeto, vá em **Settings > API** e copie:
- **Project URL**: `https://seu-projeto.supabase.co`
- **Anon/Public Key**: Chave pública para o frontend
- **Service Role Key**: Chave privada para o backend (MANTENHA SEGURA!)

## 2. Configurar Banco de Dados

### Executar Migrations

1. No Supabase Dashboard, vá para **SQL Editor**
2. Crie uma nova query
3. Cole e execute cada arquivo de migration em ordem:

#### Migration 1: Schema Inicial
```sql
-- Cole o conteúdo de: backend/migrations/supabase/001_initial_schema.sql
```

#### Migration 2: Row Level Security
```sql
-- Cole o conteúdo de: backend/migrations/supabase/002_row_level_security.sql
```

#### Migration 3: Storage Setup
```sql
-- Cole as partes SQL de: backend/migrations/supabase/003_storage_setup.sql
```

### Verificar Tabelas
Após executar, verifique em **Table Editor** se foram criadas:
- `profiles`
- `products`
- `sales`
- `qr_scans`
- `product_images`

## 3. Configurar Autenticação

### Configurar Providers
1. Vá para **Authentication > Providers**
2. Configure **Email**:
   - ✅ Enable Email provider
   - ✅ Confirm email (pode desativar para testes)
   - Customize email templates se desejar

### Configurar Email Templates (Opcional)
1. Vá para **Authentication > Email Templates**
2. Personalize os templates:
   - **Confirm signup**: Email de confirmação
   - **Reset password**: Recuperação de senha

### Configurar URL de Redirecionamento
1. Em **Authentication > URL Configuration**
2. Adicione as URLs do seu frontend:
   ```
   Site URL: http://localhost:3000
   Redirect URLs: 
   - http://localhost:3000/auth/callback
   - http://localhost:8000/auth/callback
   - https://seu-dominio.com/auth/callback
   ```

## 4. Configurar Storage

### Criar Buckets
1. Vá para **Storage**
2. Clique em "New bucket" e crie 3 buckets:

#### Bucket 1: products
- **Name**: `products`
- **Public**: ✅ (marcar como público)
- **File size limit**: 5MB
- **Allowed MIME types**: `image/jpeg, image/png, image/webp`

#### Bucket 2: qr-codes
- **Name**: `qr-codes`
- **Public**: ✅ (marcar como público)
- **File size limit**: 1MB
- **Allowed MIME types**: `image/png, image/svg+xml`

#### Bucket 3: avatars
- **Name**: `avatars`
- **Public**: ✅ (marcar como público)
- **File size limit**: 2MB
- **Allowed MIME types**: `image/jpeg, image/png, image/webp`

### Configurar Políticas de Storage
Para cada bucket, vá em **Policies** e adicione:

#### Products Bucket:
```sql
-- SELECT (Leitura pública)
CREATE POLICY "Imagens públicas" ON storage.objects
FOR SELECT USING (bucket_id = 'products');

-- INSERT (Vendedores fazem upload)
CREATE POLICY "Vendedores upload" ON storage.objects
FOR INSERT WITH CHECK (
  bucket_id = 'products' AND
  auth.role() = 'authenticated'
);

-- UPDATE/DELETE (Donos editam)
CREATE POLICY "Donos editam" ON storage.objects
FOR ALL USING (
  bucket_id = 'products' AND
  auth.uid()::text = (storage.foldername(name))[1]
);
```

## 5. Configurar Variáveis de Ambiente

### Criar arquivo .env
No diretório `backend/`, crie um arquivo `.env`:

```bash
# Supabase Configuration
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=eyJ...sua-anon-key-aqui...
SUPABASE_SERVICE_KEY=eyJ...sua-service-key-aqui...

# Database Configuration (Supabase PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:[SUA-SENHA]@db.[SEU-PROJETO].supabase.co:5432/postgres

# Security
SECRET_KEY=gere-uma-chave-secreta-forte-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Supabase Auth Settings
SUPABASE_JWT_SECRET=seu-jwt-secret-do-supabase

# Storage Configuration
STORAGE_TYPE=supabase
SUPABASE_STORAGE_BUCKET=products
SUPABASE_QR_BUCKET=qr-codes

# QR Code Settings
QR_CODE_BASE_URL=https://seu-projeto.supabase.co/products/qr

# Redis (opcional para cache)
REDIS_URL=redis://localhost:6379/0

# Application
APP_NAME=Coisas de Garagem API
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development
API_V1_PREFIX=/api/v1

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=True

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### Obter JWT Secret
1. No Supabase Dashboard, vá em **Settings > API**
2. Procure por **JWT Settings**
3. Copie o **JWT Secret** (NÃO a anon key!)

## 6. Testar Integração

### Instalar Dependências
```bash
cd backend
pip install -r requirements.txt
```

### Testar Conexão
Crie um arquivo `test_supabase.py`:

```python
import asyncio
from app.infrastructure.supabase.client import get_supabase_client

async def test_connection():
    client = get_supabase_client()
    
    # Testar query no banco
    result = client.table("profiles").select("*").limit(1).execute()
    print("Conexão com banco: OK")
    
    # Testar buckets
    buckets = ["products", "qr-codes", "avatars"]
    for bucket in buckets:
        print(f"Bucket '{bucket}': Configurado")
    
    print("\n✅ Supabase configurado com sucesso!")

if __name__ == "__main__":
    asyncio.run(test_connection())
```

### Executar Teste
```bash
python test_supabase.py
```

## 🚀 Iniciar Aplicação

### Backend
```bash
cd backend
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs

### Testar Endpoints

#### 1. Registrar Usuário
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

#### 2. Fazer Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teste@exemplo.com",
    "password": "Senha123!"
  }'
```

## 📊 Monitoramento

### Dashboard do Supabase
- **Database**: Monitor de queries e performance
- **Authentication**: Usuários registrados e logins
- **Storage**: Uso de armazenamento
- **Realtime**: Conexões ativas
- **Logs**: Logs de erro e debug

### Métricas Importantes
- Usuários ativos: `select count(*) from auth.users`
- Produtos cadastrados: `select count(*) from products`
- Vendas realizadas: `select count(*) from sales where status = 'completed'`
- Uso de storage: Dashboard > Storage > Usage

## 🔒 Segurança

### Checklist de Segurança
- [ ] Service Role Key NUNCA no frontend
- [ ] Usar apenas Anon Key no frontend
- [ ] RLS habilitado em todas as tabelas
- [ ] Políticas de storage configuradas
- [ ] Backup automático ativado
- [ ] SSL/TLS sempre ativo
- [ ] Variáveis de ambiente seguras
- [ ] Não commitar `.env` no git

### Backup
O Supabase faz backup automático diário no plano free. Para backup manual:
1. Vá em **Settings > Backups**
2. Clique em "Start backup"

## 🆘 Troubleshooting

### Erro: "relation does not exist"
- Execute as migrations na ordem correta
- Verifique se está no schema correto (`public`)

### Erro: "permission denied"
- Verifique as políticas RLS
- Confirme que está usando o token correto

### Erro: "JWT expired"
- Implemente refresh token
- Aumente tempo de expiração em AUTH settings

### Storage não funciona
- Verifique se buckets foram criados
- Confirme políticas de acesso
- Teste com Dashboard primeiro

## 📚 Recursos Adicionais

- [Documentação Supabase](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [SQL Editor Guide](https://supabase.com/docs/guides/database)
- [RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Storage Guide](https://supabase.com/docs/guides/storage)
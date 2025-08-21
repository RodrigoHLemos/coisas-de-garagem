# 🔐 Sistema de Autenticação - Coisas de Garagem

## 📋 Status Atual

O sistema de autenticação está **IMPLEMENTADO** e integrado com Supabase Auth, mas precisa de uma configuração final no banco de dados.

## ⚠️ AÇÃO NECESSÁRIA

### Executar Migration no Supabase

1. **Acesse o Supabase Dashboard**
   - URL: https://supabase.com/dashboard
   - Faça login com sua conta

2. **Selecione seu projeto**
   - Projeto: `CoisasDeGaragem` ou similar

3. **Vá para o SQL Editor**
   - Clique no ícone de banco de dados na barra lateral
   - Ou acesse diretamente: SQL Editor

4. **Execute a Migration**
   - Cole o conteúdo do arquivo: `backend/migrations/supabase/004_auth_trigger.sql`
   - Clique em "Run" para executar
   - Você deve ver uma mensagem de sucesso

## 🧪 Testar Autenticação

Após executar a migration, teste o sistema:

```bash
cd backend
bash scripts/setup_auth.sh
```

Ou manualmente:

```bash
cd backend
python tests/test_auth.py
```

## 🔧 Funcionalidades Implementadas

### Endpoints de Autenticação

| Endpoint | Método | Descrição | Status |
|----------|--------|-----------|--------|
| `/api/v1/auth/register` | POST | Registrar novo usuário | ✅ Implementado |
| `/api/v1/auth/login` | POST | Login com email/senha | ✅ Implementado |
| `/api/v1/users/profile` | GET | Obter perfil do usuário | ✅ Implementado |
| `/api/v1/users/profile` | PUT | Atualizar perfil | ✅ Implementado |

### Recursos de Segurança

- ✅ **JWT Authentication**: Tokens seguros via Supabase
- ✅ **Password Hashing**: Senhas criptografadas automaticamente
- ✅ **Role-Based Access**: Suporte para buyer/seller/admin
- ✅ **Token Refresh**: Renovação automática de tokens
- ✅ **Email Verification**: Preparado para verificação de email
- ✅ **Row Level Security**: Preparado para RLS no Supabase

### Middleware de Autenticação

```python
# Dependências disponíveis em app/api/deps.py

# Usuário opcional (não força autenticação)
async def get_current_user() -> Optional[Dict]

# Requer autenticação
async def require_user() -> Dict

# Requer vendedor
async def require_seller() -> Dict

# Requer admin
async def require_admin() -> Dict

# Obtém perfil completo
async def get_current_user_profile() -> Dict
```

## 📝 Exemplo de Uso

### Registro de Usuário

```python
POST /api/v1/auth/register
{
    "email": "usuario@exemplo.com",
    "password": "SenhaForte123!",
    "name": "João Silva",
    "cpf": "12345678901",
    "phone": "11999999999",
    "role": "seller"  // ou "buyer"
}
```

### Login

```python
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=usuario@exemplo.com&password=SenhaForte123!
```

Resposta:
```json
{
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 3600,
    "refresh_token": "..."
}
```

### Acessar Rota Protegida

```python
GET /api/v1/users/profile
Authorization: Bearer {access_token}
```

## 🐛 Troubleshooting

### Erro: "Database error saving new user"

**Solução**: Execute a migration `004_auth_trigger.sql` no Supabase Dashboard

### Erro: "Not authenticated"

**Solução**: Inclua o header `Authorization: Bearer {token}` na requisição

### Erro: "User already exists"

**Solução**: O email já está cadastrado. Use outro email ou faça login.

## 🚀 Próximos Passos

Após confirmar que a autenticação está funcionando:

1. **Implementar endpoints de produtos**
   - CRUD completo para produtos
   - Upload de imagens

2. **Implementar sistema de vendas**
   - Carrinho de compras
   - Processamento de vendas
   - Histórico

3. **Implementar QR Codes**
   - Geração de QR codes
   - Leitura e validação

4. **Configurar notificações**
   - Email via Supabase
   - Notificações in-app

## 📚 Documentação Relacionada

- [API.md](API.md) - Documentação completa da API
- [ARQUITETURA.md](ARQUITETURA.md) - Arquitetura do sistema
- [migrations/](migrations/) - Todas as migrations SQL
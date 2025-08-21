# 📚 Documentação da API - Coisas de Garagem

## Base URL
```
http://localhost:8000/api/v1
```

## Autenticação

A API usa JWT (JSON Web Tokens) via Supabase Auth. Inclua o token no header:

```
Authorization: Bearer <seu_token_aqui>
```

## Status de Implementação

| Endpoint | Método | Status | Descrição |
|----------|--------|--------|------------|
| `/auth/register` | POST | ✅ Implementado | Registro de usuário |
| `/auth/login` | POST | ✅ Implementado | Login com email/senha |
| `/auth/refresh` | POST | ⏳ Pendente | Renovar token |
| `/auth/logout` | POST | ⏳ Pendente | Logout |
| `/users/profile` | GET | ✅ Implementado | Obter perfil |
| `/users/profile` | PUT | ✅ Implementado | Atualizar perfil |
| `/products` | GET | ⏳ Pendente | Listar produtos |
| `/products` | POST | ⏳ Pendente | Criar produto |
| `/sales` | GET | ⏳ Pendente | Listar vendas |
| `/qr-codes` | GET | ⏳ Pendente | Gerar QR Code |

## Endpoints

### 🔐 Autenticação

#### POST `/auth/register`
Registra um novo usuário.

**Request Body:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "SenhaForte123!",
  "name": "João Silva",
  "cpf": "123.456.789-00",
  "phone": "(11) 98765-4321",
  "role": "buyer"  // "buyer", "seller", ou "admin"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "usuario@exemplo.com",
  "name": "João Silva",
  "cpf": "12345678900",
  "phone": "11987654321",
  "role": "buyer",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST `/auth/login`
Autentica um usuário.

**Request Body (form-data):**
```
Content-Type: application/x-www-form-urlencoded

username=usuario@exemplo.com&password=SenhaForte123!
```

**Ou via JSON (para testes):**
```json
{
  "username": "usuario@exemplo.com",
  "password": "SenhaForte123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST `/auth/refresh`
Renova o token de acesso.

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 📦 Produtos

#### GET `/products`
Lista produtos disponíveis.

**Query Parameters:**
- `page` (int): Página atual (default: 1)
- `page_size` (int): Itens por página (default: 20)
- `category` (string): Filtrar por categoria
- `min_price` (float): Preço mínimo
- `max_price` (float): Preço máximo
- `search` (string): Buscar por nome ou descrição

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "seller_id": "uuid",
      "name": "Notebook Dell",
      "description": "Notebook em bom estado",
      "price": 1500.00,
      "category": "electronics",
      "quantity": 1,
      "status": "available",
      "images": ["url1", "url2"],
      "qr_code_url": "url",
      "views": 42,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

#### GET `/products/{id}`
Obtém detalhes de um produto.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "seller_id": "uuid",
  "name": "Notebook Dell",
  "description": "Notebook em bom estado, 8GB RAM",
  "price": 1500.00,
  "category": "electronics",
  "quantity": 1,
  "status": "available",
  "images": ["url1", "url2"],
  "qr_code_url": "url",
  "views": 42,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST `/products`
Cria um novo produto (requer autenticação de vendedor).

**Request Body:**
```json
{
  "name": "Notebook Dell",
  "description": "Notebook em bom estado, 8GB RAM",
  "price": 1500.00,
  "category": "electronics",
  "quantity": 1,
  "images": ["base64_image1", "base64_image2"]
}
```

**Response:** `201 Created`

#### PUT `/products/{id}`
Atualiza um produto (apenas o vendedor dono).

**Request Body:**
```json
{
  "name": "Notebook Dell Atualizado",
  "price": 1400.00,
  "status": "reserved"
}
```

**Response:** `200 OK`

#### DELETE `/products/{id}`
Remove um produto (apenas o vendedor dono).

**Response:** `204 No Content`

### 🛒 Vendas

#### GET `/sales`
Lista vendas do usuário.

**Query Parameters:**
- `role` (string): "buyer" ou "seller"
- `status` (string): "pending", "completed", "cancelled", "refunded"
- `page` (int): Página atual
- `page_size` (int): Itens por página

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "seller_id": "uuid",
      "buyer_id": "uuid",
      "items": [
        {
          "id": "uuid",
          "product_id": "uuid",
          "product_name": "Notebook Dell",
          "quantity": 1,
          "unit_price": 1500.00,
          "subtotal": 1500.00
        }
      ],
      "total_amount": 1500.00,
      "status": "completed",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### POST `/sales`
Cria uma nova venda.

**Request Body:**
```json
{
  "items": [
    {
      "product_id": "uuid",
      "quantity": 2,
      "unit_price": 50.00
    }
  ],
  "buyer_notes": "Entregar após 18h"
}
```

**Response:** `201 Created`

#### PUT `/sales/{id}/status`
Atualiza status de uma venda.

**Request Body:**
```json
{
  "status": "completed",
  "seller_notes": "Entregue com sucesso"
}
```

**Response:** `200 OK`

### 📱 QR Codes

#### POST `/qr-codes/generate`
Gera QR Code para um produto.

**Request Body:**
```json
{
  "product_id": "uuid",
  "size": 10,
  "border": 5
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "product_id": "uuid",
  "qr_code_url": "https://storage.supabase.co/...",
  "scan_url": "http://localhost:8000/scan/uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "scans_count": 0
}
```

#### GET `/qr-codes/scan/{code}`
Registra scan de QR Code e retorna informações do produto.

**Response:** `200 OK`
```json
{
  "product_id": "uuid",
  "product_name": "Notebook Dell",
  "product_price": 1500.00,
  "seller_name": "João Silva",
  "seller_phone": "11987654321",
  "scan_count": 15,
  "scanned_at": "2024-01-01T00:00:00Z"
}
```

### 👤 Usuários

#### GET `/users/profile`
Obtém perfil do usuário autenticado.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "usuario@exemplo.com",
  "name": "João Silva",
  "cpf": "12345678900",
  "phone": "11987654321",
  "role": "seller",
  "store_name": "Loja do João",
  "store_description": "Vendemos de tudo",
  "avatar_url": "https://storage.supabase.co/...",
  "total_sales": 42,
  "total_purchases": 5,
  "rating": 4.8,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PUT `/users/profile`
Atualiza perfil do usuário.

**Request Body:**
```json
{
  "name": "João Silva Santos",
  "phone": "11999999999",
  "store_name": "Mega Loja do João",
  "store_description": "Os melhores produtos",
  "avatar_url": "base64_image"
}
```

**Response:** `200 OK`

#### GET `/users/{id}/public`
Obtém perfil público de um vendedor.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "João Silva",
  "store_name": "Loja do João",
  "store_description": "Vendemos de tudo",
  "avatar_url": "https://storage.supabase.co/...",
  "total_products": 25,
  "total_sales": 42,
  "rating": 4.8,
  "member_since": "2024-01-01T00:00:00Z"
}
```

## Status Codes

| Código | Descrição |
|--------|-----------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado |
| 204 | No Content - Requisição bem-sucedida sem conteúdo |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Não autenticado |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Validação falhou |
| 500 | Internal Server Error - Erro no servidor |

## Rate Limiting

A API implementa rate limiting:
- **Não autenticado**: 100 requisições/hora
- **Autenticado**: 1000 requisições/hora
- **Admin**: Sem limite

## Paginação

Endpoints que retornam listas suportam paginação:

```
GET /products?page=2&page_size=50
```

Resposta inclui metadados:
```json
{
  "items": [...],
  "total": 500,
  "page": 2,
  "page_size": 50,
  "total_pages": 10
}
```

## Filtros

Endpoints de listagem suportam filtros via query parameters:

```
GET /products?category=electronics&min_price=100&max_price=1000
```

## Busca

Use o parâmetro `search` para busca textual:

```
GET /products?search=notebook
```

## Ordenação

Use `sort_by` e `order`:

```
GET /products?sort_by=price&order=asc
GET /products?sort_by=created_at&order=desc
```

## Versionamento

A API é versionada via URL:
- v1: `/api/v1/...`
- v2 (futuro): `/api/v2/...`

## SDKs

SDKs oficiais disponíveis para:
- JavaScript/TypeScript (em desenvolvimento)
- Python (em desenvolvimento)
- Flutter/Dart (em desenvolvimento)
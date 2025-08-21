# Fluxo de Dados - Sistema Coisas de Garagem

## Índice
1. [Visão Geral do Fluxo](#visão-geral-do-fluxo)
2. [Fluxos Principais](#fluxos-principais)
3. [Ciclo de Vida dos Dados](#ciclo-de-vida-dos-dados)
4. [Camadas e Responsabilidades](#camadas-e-responsabilidades)
5. [Diagramas de Sequência](#diagramas-de-sequência)

## Visão Geral do Fluxo

O sistema segue uma arquitetura em camadas onde os dados fluem de forma unidirecional, garantindo separação de responsabilidades e facilitando manutenção.

```
┌─────────────┐
│   Cliente   │ (Frontend/Mobile)
└──────┬──────┘
       │ HTTP/HTTPS
       ▼
┌─────────────┐
│  API Layer  │ (FastAPI)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Service   │ (Lógica de Aplicação)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Domain    │ (Regras de Negócio)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Repository  │ (Abstração de Dados)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │ (PostgreSQL)
└─────────────┘
```

## Fluxos Principais

### 1. Fluxo de Registro de Usuário

```
ENTRADA: Dados do usuário (email, CPF, nome, telefone, senha)
```

**Passo a Passo**:

1. **Cliente → API** (`POST /api/v1/auth/register`)
   - Envia JSON com dados do usuário

2. **API → Schema Validation** (`UserRegisterRequest`)
   - Valida formato do email
   - Valida CPF (11 dígitos + algoritmo)
   - Valida telefone brasileiro
   - Valida senha (min 8 chars, maiúscula, minúscula, número)

3. **API → AuthService**
   ```python
   auth_service = AuthService(session)
   user = await auth_service.register_user(request)
   ```

4. **AuthService → Domain**
   - Cria Value Objects: `Email`, `CPF`, `Phone`
   - Cria entidade `User` com validação de domínio
   - Hash da senha com bcrypt

5. **AuthService → UserRepository**
   - Verifica se email/CPF já existem
   - Persiste usuário no banco

6. **Domain → Events**
   - Emite evento: `UserRegistered`

7. **API → Cliente**
   - Retorna `UserResponse` com dados do usuário criado

```
SAÍDA: Usuário criado com ID, sem senha
```

### 2. Fluxo de Login

```
ENTRADA: Email e senha
```

**Passo a Passo**:

1. **Cliente → API** (`POST /api/v1/auth/login`)
   - Envia credenciais (OAuth2PasswordRequestForm)

2. **API → AuthService**
   - Busca usuário por email
   - Verifica senha com hash armazenado

3. **AuthService → JWT Generation**
   - Gera access_token (30 min)
   - Gera refresh_token (7 dias)
   - Atualiza last_login do usuário

4. **API → Cliente**
   - Retorna tokens JWT

```
SAÍDA: Access token + Refresh token
```

### 3. Fluxo de Cadastro de Produto

```
ENTRADA: Dados do produto (nome, preço, descrição, categoria, imagem)
```

**Passo a Passo**:

1. **Cliente → API** (`POST /api/v1/products`)
   - Envia dados do produto + arquivo de imagem
   - Header: Authorization Bearer {token}

2. **API → Authentication Middleware**
   - Valida JWT token
   - Extrai user_id do token
   - Verifica se usuário é vendedor

3. **API → ProductService**
   ```python
   product_service = ProductService(session)
   product = await product_service.create_product(data, seller_id)
   ```

4. **ProductService → Storage**
   - Upload da imagem para S3/MinIO
   - Retorna URL da imagem

5. **ProductService → Domain**
   - Cria Value Object `Money` para preço
   - Cria entidade `Product` com validações

6. **ProductService → QR Code Generation**
   - Gera identificador único
   - Cria QR code com URL do produto
   - Salva imagem do QR code

7. **ProductService → ProductRepository**
   - Persiste produto no banco

8. **Domain → Events**
   - Emite evento: `ProductCreated`

9. **API → Cliente**
   - Retorna produto com QR code

```
SAÍDA: Produto criado com QR code
```

### 4. Fluxo de Compra (Via QR Code)

```
ENTRADA: QR code escaneado
```

**Passo a Passo**:

1. **Cliente → API** (`GET /api/v1/products/qr/{qr_code}`)
   - Escaneia QR code
   - Envia código para API

2. **API → ProductService**
   - Busca produto pelo QR code
   - Incrementa contador de visualizações

3. **Cliente → API** (`POST /api/v1/sales/purchase`)
   - Confirma intenção de compra
   - Envia product_id + buyer_id

4. **API → SaleService**
   ```python
   sale_service = SaleService(session)
   sale = await sale_service.create_purchase(product_id, buyer_id)
   ```

5. **SaleService → Domain Validation**
   - Verifica se produto está disponível
   - Verifica se comprador está ativo
   - Cria entidade `Sale`

6. **SaleService → Transaction**
   - Inicia transação do banco
   - Marca produto como vendido
   - Cria registro de venda
   - Commit da transação

7. **Domain → Events**
   - Emite evento: `ProductSold`
   - Emite evento: `SaleCompleted`

8. **SaleService → Notification** (futuro)
   - Notifica vendedor por email/SMS
   - Notifica comprador com confirmação

9. **API → Cliente**
   - Retorna confirmação da compra

```
SAÍDA: Confirmação de compra com detalhes
```

## Ciclo de Vida dos Dados

### Estados do Produto

```
[CRIADO] → [DISPONÍVEL] → [RESERVADO] → [VENDIDO]
             ↓      ↑         ↓
         [INATIVO]       [CANCELADO]
```

### Estados do Usuário

```
[REGISTRADO] → [VERIFICADO] → [ATIVO]
                               ↓    ↑
                           [INATIVO]
```

### Estados da Venda

```
[INICIADA] → [CONFIRMADA] → [CONCLUÍDA]
                ↓
           [CANCELADA]
```

## Camadas e Responsabilidades

### 1. **Camada de Apresentação (API)**
**Localização**: `app/api/v1/`

**Responsabilidades**:
- Receber requisições HTTP
- Validar dados de entrada
- Autenticar/autorizar usuários
- Serializar respostas
- Documentação automática (OpenAPI)

**Fluxo de Dados**:
```python
# Entrada
Request → Pydantic Schema → Validated Data

# Processamento
Validated Data → Service Layer → Domain Logic

# Saída
Domain Object → Response Schema → JSON Response
```

### 2. **Camada de Serviço (Application)**
**Localização**: `app/services/`

**Responsabilidades**:
- Coordenar casos de uso
- Orquestrar transações
- Chamar serviços externos
- Aplicar lógica de aplicação

**Fluxo de Dados**:
```python
# Coordenação
Input DTO → Domain Entity → Repository → External Services → Response DTO
```

### 3. **Camada de Domínio (Business)**
**Localização**: `app/domain/`

**Responsabilidades**:
- Aplicar regras de negócio
- Validar invariantes
- Emitir eventos de domínio
- Manter integridade dos dados

**Fluxo de Dados**:
```python
# Validação e Regras
Raw Data → Value Objects → Entity Validation → Business Rules → Domain Events
```

### 4. **Camada de Infraestrutura**
**Localização**: `app/infrastructure/`

**Responsabilidades**:
- Persistência de dados
- Comunicação externa
- Armazenamento de arquivos
- Cache e fila de mensagens

**Fluxo de Dados**:
```python
# Persistência
Domain Entity → SQL Model → Database → SQL Model → Domain Entity
```

## Diagramas de Sequência

### Sequência de Autenticação JWT

```
Cliente         API           AuthService      UserRepo        JWT
   │              │                │              │             │
   ├─login────────►                │              │             │
   │              ├─validate────────►              │             │
   │              │                ├─find_user────►             │
   │              │                │◄──user────────             │
   │              │                ├─verify_pass──►             │
   │              │                ├─generate─────────────────►│
   │              │                │◄──tokens──────────────────│
   │◄──tokens──────                │              │             │
   │              │                │              │             │
```

### Sequência de Criação de Produto com QR Code

```
Cliente         API          ProductService    QRService     Storage      DB
   │              │                │              │            │          │
   ├─create───────►                │              │            │          │
   │              ├─auth───────────►              │            │          │
   │              ├─validate──────►              │            │          │
   │              │                ├─upload_img───────────────►          │
   │              │                │◄──img_url────────────────           │
   │              │                ├─generate_qr──►            │          │
   │              │                │◄──qr_data────             │          │
   │              │                ├─save_qr──────────────────►          │
   │              │                ├─save_product─────────────────────────►
   │              │                │◄──product_id─────────────────────────
   │◄──product─────                │              │            │          │
```

### Sequência de Compra via QR Code

```
Cliente      Mobile        API         SaleService    ProductRepo    SaleRepo
   │           │            │               │             │             │
   │           ├─scan_qr────►               │             │             │
   │           │            ├─get_product───►             │             │
   │           │            │               ├─find────────►             │
   │           │            │◄──product─────              │             │
   │◄──show────┤            │               │             │             │
   ├─confirm───►            │               │             │             │
   │           │            ├─purchase──────►             │             │
   │           │            │               ├─check_avail─►             │
   │           │            │               ├─mark_sold───►             │
   │           │            │               ├─create_sale─────────────►│
   │           │            │               │◄──sale_id───────────────┤│
   │◄──receipt──            │               │             │             │
```

## Fluxo de Cache (Redis)

### Estratégia de Cache

```
Request → Check Cache → Found? → Return Cached
            ↓            No ↓
         Database ← Fetch Data
            ↓
         Update Cache
            ↓
         Return Data
```

**Dados Cacheados**:
- Lista de produtos disponíveis (TTL: 5 min)
- Detalhes do produto (TTL: 10 min)
- Informações do usuário (TTL: 30 min)
- Dashboard do vendedor (TTL: 1 min)

### Invalidação de Cache

```python
# Quando produto é atualizado
async def update_product(product_id):
    # 1. Atualiza banco
    await repository.update(product)
    
    # 2. Invalida cache
    await redis.delete(f"product:{product_id}")
    await redis.delete("products:available")
    
    # 3. Emite evento
    emit_event("ProductUpdated", product_id)
```

## Tratamento de Erros

### Fluxo de Exceções

```
Domain Exception → Service Layer → API Layer → Error Response
         ↓              ↓              ↓
    Log & Metrics   Rollback      HTTP Status
```

**Tipos de Erro**:
- `400 Bad Request`: Validação falhou
- `401 Unauthorized`: Não autenticado
- `403 Forbidden`: Sem permissão
- `404 Not Found`: Recurso não existe
- `409 Conflict`: Conflito de dados
- `500 Internal Server`: Erro não tratado

### Exemplo de Tratamento

```python
try:
    # Tenta criar produto
    product = await service.create_product(data)
except DomainValidationError as e:
    # Erro de validação → 400
    return JSONResponse(status_code=400, content={"error": str(e)})
except UnauthorizedError as e:
    # Sem permissão → 403
    return JSONResponse(status_code=403, content={"error": str(e)})
except Exception as e:
    # Erro genérico → 500
    logger.error(f"Unexpected error: {e}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})
```
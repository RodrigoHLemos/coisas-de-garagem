# Diagramas do Sistema - Coisas de Garagem

## Arquitetura Geral

```mermaid
graph TB
    subgraph "Frontend"
        WEB[Aplicação Web]
        MOBILE[Mobile/Scanner]
    end
    
    subgraph "Backend - FastAPI"
        API[API Layer]
        AUTH[Auth Service]
        PROD[Product Service]
        SALE[Sales Service]
        QR[QR Service]
    end
    
    subgraph "Infraestrutura"
        DB[(PostgreSQL)]
        REDIS[(Redis Cache)]
        S3[S3/MinIO Storage]
    end
    
    WEB --> API
    MOBILE --> API
    API --> AUTH
    API --> PROD
    API --> SALE
    API --> QR
    
    AUTH --> DB
    PROD --> DB
    SALE --> DB
    
    PROD --> S3
    QR --> S3
    
    API --> REDIS
```

## Fluxo de Autenticação

```mermaid
sequenceDiagram
    participant C as Cliente
    participant API as API
    participant AS as AuthService
    participant DB as Database
    participant JWT as JWT Service
    
    C->>API: POST /auth/register
    API->>API: Validar dados (Pydantic)
    API->>AS: register_user()
    AS->>DB: Verificar email/CPF
    AS->>AS: Hash senha
    AS->>DB: Salvar usuário
    AS->>JWT: Gerar tokens
    JWT-->>AS: access + refresh tokens
    AS-->>API: UserResponse + tokens
    API-->>C: 201 Created
```

## Fluxo de Criação de Produto

```mermaid
sequenceDiagram
    participant V as Vendedor
    participant API as API
    participant PS as ProductService
    participant QRS as QRService
    participant ST as Storage
    participant DB as Database
    
    V->>API: POST /products (com imagem)
    API->>API: Validar JWT
    API->>PS: create_product()
    PS->>ST: Upload imagem
    ST-->>PS: URL imagem
    PS->>QRS: generate_qr()
    QRS->>QRS: Criar QR code
    QRS->>ST: Salvar QR
    QRS-->>PS: QR data + URL
    PS->>DB: Salvar produto
    DB-->>PS: product_id
    PS-->>API: ProductResponse
    API-->>V: 201 Created
```

## Fluxo de Compra via QR Code

```mermaid
sequenceDiagram
    participant C as Comprador
    participant M as Mobile App
    participant API as API
    participant PS as ProductService
    participant SS as SaleService
    participant DB as Database
    
    C->>M: Escanear QR Code
    M->>API: GET /products/qr/{code}
    API->>PS: get_by_qr_code()
    PS->>DB: Buscar produto
    DB-->>PS: Produto
    PS-->>API: ProductDetails
    API-->>M: Mostrar produto
    M-->>C: Exibir detalhes
    
    C->>M: Confirmar compra
    M->>API: POST /sales/purchase
    API->>SS: create_purchase()
    SS->>DB: Verificar disponibilidade
    SS->>DB: BEGIN TRANSACTION
    SS->>DB: Marcar como vendido
    SS->>DB: Criar registro venda
    SS->>DB: COMMIT
    SS-->>API: SaleConfirmation
    API-->>M: 201 Created
    M-->>C: Compra confirmada
```

## Estrutura de Classes do Domínio

```mermaid
classDiagram
    class DomainEntity {
        <<abstract>>
        -UUID id
        -DateTime created_at
        -DateTime updated_at
        -List~Event~ events
        +validate()
        +add_domain_event()
    }
    
    class User {
        -Email email
        -String name
        -CPF cpf
        -Phone phone
        -UserRole role
        +update_profile()
        +change_password()
        +can_sell()
        +can_buy()
    }
    
    class Product {
        -String name
        -String description
        -Money price
        -UUID seller_id
        -ProductStatus status
        +mark_as_sold()
        +reserve()
        +apply_discount()
    }
    
    class Sale {
        -UUID product_id
        -UUID buyer_id
        -UUID seller_id
        -Money price
        -SaleStatus status
        +confirm()
        +cancel()
    }
    
    DomainEntity <|-- User
    DomainEntity <|-- Product
    DomainEntity <|-- Sale
```

## Value Objects

```mermaid
classDiagram
    class Email {
        <<value object>>
        -String value
        +validate()
        +domain()
        +local_part()
    }
    
    class CPF {
        <<value object>>
        -String value
        +validate()
        +formatted()
    }
    
    class Phone {
        <<value object>>
        -String value
        +validate()
        +formatted()
        +whatsapp_link()
    }
    
    class Money {
        <<value object>>
        -Decimal amount
        -String currency
        +add()
        +subtract()
        +apply_discount()
        +formatted()
    }
```

## Camadas da Arquitetura

```mermaid
graph LR
    subgraph "Presentation Layer"
        REST[REST API]
        WS[WebSocket]
    end
    
    subgraph "Application Layer"
        SVC[Services]
        DTO[DTOs/Schemas]
    end
    
    subgraph "Domain Layer"
        ENT[Entities]
        VO[Value Objects]
        REPO[Repository Interfaces]
        EVT[Domain Events]
    end
    
    subgraph "Infrastructure Layer"
        IMPL[Repository Impl]
        DB[Database]
        CACHE[Cache]
        QUEUE[Message Queue]
    end
    
    REST --> SVC
    WS --> SVC
    SVC --> ENT
    SVC --> VO
    SVC --> REPO
    REPO --> IMPL
    IMPL --> DB
    IMPL --> CACHE
    EVT --> QUEUE
```

## Estados do Sistema

### Estados do Produto

```mermaid
stateDiagram-v2
    [*] --> Criado
    Criado --> Disponível: Ativar
    Disponível --> Reservado: Reservar
    Reservado --> Disponível: Cancelar Reserva
    Reservado --> Vendido: Confirmar Venda
    Disponível --> Vendido: Venda Direta
    Disponível --> Inativo: Desativar
    Inativo --> Disponível: Reativar
    Vendido --> [*]
```

### Estados da Venda

```mermaid
stateDiagram-v2
    [*] --> Iniciada
    Iniciada --> Confirmada: Confirmar
    Confirmada --> Concluída: Processar
    Iniciada --> Cancelada: Cancelar
    Confirmada --> Cancelada: Cancelar
    Concluída --> [*]
    Cancelada --> [*]
```

### Estados do Usuário

```mermaid
stateDiagram-v2
    [*] --> Registrado
    Registrado --> Verificado: Verificar Email
    Verificado --> Ativo: Ativar
    Ativo --> Inativo: Desativar
    Inativo --> Ativo: Reativar
    Ativo --> Vendedor: Promover
```

## Fluxo de Cache

```mermaid
graph TD
    REQ[Requisição] --> CHECK{Cache existe?}
    CHECK -->|Sim| HIT[Cache Hit]
    CHECK -->|Não| MISS[Cache Miss]
    HIT --> RETURN[Retornar dados]
    MISS --> DB[Buscar no BD]
    DB --> STORE[Armazenar no cache]
    STORE --> RETURN
    
    UPDATE[Atualização] --> INVALID[Invalidar cache]
    INVALID --> DB2[Atualizar BD]
```

## Pipeline de Deploy

```mermaid
graph LR
    DEV[Development] --> TEST[Testing]
    TEST --> BUILD[Build Docker]
    BUILD --> PUSH[Push Registry]
    PUSH --> STAGING[Staging]
    STAGING --> PROD[Production]
    
    TEST --> UNIT[Unit Tests]
    TEST --> INT[Integration Tests]
    TEST --> E2E[E2E Tests]
```

## Componentes do Sistema

```mermaid
graph TB
    subgraph "Cliente"
        BROWSER[Navegador Web]
        SCANNER[App Scanner QR]
    end
    
    subgraph "Gateway"
        NGINX[Nginx]
        LB[Load Balancer]
    end
    
    subgraph "Aplicação"
        API1[FastAPI Instance 1]
        API2[FastAPI Instance 2]
        WORKER[Celery Workers]
    end
    
    subgraph "Dados"
        PG_MASTER[(PostgreSQL Master)]
        PG_SLAVE[(PostgreSQL Slave)]
        REDIS_CACHE[(Redis Cache)]
        REDIS_QUEUE[(Redis Queue)]
    end
    
    subgraph "Armazenamento"
        S3[S3/MinIO]
    end
    
    BROWSER --> NGINX
    SCANNER --> NGINX
    NGINX --> LB
    LB --> API1
    LB --> API2
    
    API1 --> PG_MASTER
    API2 --> PG_MASTER
    PG_MASTER --> PG_SLAVE
    
    API1 --> REDIS_CACHE
    API2 --> REDIS_CACHE
    
    API1 --> REDIS_QUEUE
    REDIS_QUEUE --> WORKER
    
    API1 --> S3
    API2 --> S3
    WORKER --> S3
```

## Modelo de Dados (ER)

```mermaid
erDiagram
    USERS ||--o{ PRODUCTS : "owns"
    USERS ||--o{ SALES : "buys"
    PRODUCTS ||--o| SALES : "sold_in"
    PRODUCTS ||--|| QR_CODES : "has"
    
    USERS {
        uuid id PK
        string email UK
        string cpf UK
        string name
        string phone
        string password_hash
        enum role
        boolean is_active
        datetime created_at
    }
    
    PRODUCTS {
        uuid id PK
        uuid seller_id FK
        string name
        text description
        decimal price
        enum category
        enum status
        string image_url
        string qr_code_data UK
        int view_count
        datetime created_at
    }
    
    SALES {
        uuid id PK
        uuid product_id FK
        uuid buyer_id FK
        uuid seller_id FK
        decimal price
        enum status
        datetime transaction_date
    }
    
    QR_CODES {
        uuid id PK
        uuid product_id FK
        string code UK
        string image_url
        int scan_count
        datetime created_at
    }
```
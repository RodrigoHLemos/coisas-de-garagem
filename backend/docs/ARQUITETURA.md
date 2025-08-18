# Arquitetura do Sistema - Coisas de Garagem

## Índice
1. [Visão Geral](#visão-geral)
2. [Princípios Arquiteturais](#princípios-arquiteturais)
3. [Estrutura de Diretórios](#estrutura-de-diretórios)
4. [Explicação Detalhada dos Arquivos](#explicação-detalhada-dos-arquivos)
5. [Padrões de Projeto Utilizados](#padrões-de-projeto-utilizados)

## Visão Geral

O backend do sistema "Coisas de Garagem" foi desenvolvido seguindo os princípios de **Domain-Driven Design (DDD)** e **Clean Architecture**, garantindo separação clara de responsabilidades, alta manutenibilidade e testabilidade.

## Princípios Arquiteturais

### SOLID
- **S**ingle Responsibility (Responsabilidade Única): Cada classe tem apenas uma razão para mudar
- **O**pen/Closed (Aberto/Fechado): Aberto para extensão, fechado para modificação
- **L**iskov Substitution (Substituição de Liskov): Classes derivadas devem ser substituíveis por suas classes base
- **I**nterface Segregation (Segregação de Interface): Muitas interfaces específicas são melhores que uma interface geral
- **D**ependency Inversion (Inversão de Dependência): Dependa de abstrações, não de implementações concretas

### DRY (Don't Repeat Yourself)
Evitamos duplicação de código através de abstrações e reutilização de componentes.

## Estrutura de Diretórios

```
backend/
├── app/
│   ├── api/                 # Camada de Apresentação
│   │   └── v1/
│   │       ├── endpoints/   # Endpoints da API REST
│   │       ├── schemas/     # Schemas Pydantic para validação
│   │       └── router.py    # Roteador principal da API
│   │
│   ├── core/               # Configurações Centrais
│   │   └── config.py       # Gerenciamento de configurações
│   │
│   ├── domain/             # Camada de Domínio (Núcleo do Negócio)
│   │   ├── entities/       # Entidades do domínio
│   │   ├── repositories/   # Interfaces de repositório
│   │   └── value_objects/  # Objetos de valor
│   │
│   ├── infrastructure/     # Camada de Infraestrutura
│   │   ├── database/       # Conexão e configuração do banco
│   │   ├── storage/        # Armazenamento de arquivos
│   │   └── external/       # Serviços externos
│   │
│   ├── services/           # Camada de Aplicação
│   │   ├── auth/           # Serviços de autenticação
│   │   ├── products/       # Serviços de produtos
│   │   ├── sales/          # Serviços de vendas
│   │   └── qr_codes/       # Serviços de QR Code
│   │
│   ├── shared/             # Componentes Compartilhados
│   │   ├── exceptions/     # Exceções customizadas
│   │   ├── utils/          # Utilitários
│   │   └── validators/     # Validadores reutilizáveis
│   │
│   └── main.py            # Ponto de entrada da aplicação
```

## Explicação Detalhada dos Arquivos

### 1. **app/main.py**
**Propósito**: Ponto de entrada principal da aplicação FastAPI.

**Responsabilidades**:
- Criar e configurar a instância do FastAPI
- Configurar middlewares (CORS, TrustedHost, etc.)
- Registrar manipuladores de exceções globais
- Incluir rotas da API
- Gerenciar ciclo de vida da aplicação (startup/shutdown)

**Conexões**:
- Importa configurações de `core/config.py`
- Importa rotas de `api/v1/router.py`
- Importa conexão do banco de `infrastructure/database/connection.py`

**Como funciona**:
```python
# Factory pattern para criar a aplicação
def create_application() -> FastAPI:
    # 1. Cria instância FastAPI
    # 2. Configura middlewares
    # 3. Configura exception handlers
    # 4. Inclui rotas
    # 5. Retorna aplicação configurada
```

### 2. **app/core/config.py**
**Propósito**: Gerenciamento centralizado de todas as configurações do sistema.

**Responsabilidades**:
- Carregar variáveis de ambiente
- Validar configurações
- Fornecer interface única para acessar configurações

**Classes de Configuração**:
- `AppSettings`: Configurações gerais da aplicação
- `ServerSettings`: Configurações do servidor
- `DatabaseSettings`: Configurações do banco de dados
- `SecuritySettings`: Configurações de segurança e JWT
- `CORSSettings`: Configurações de CORS
- `RedisSettings`: Configurações do Redis
- `StorageSettings`: Configurações de armazenamento
- `QRCodeSettings`: Configurações de geração de QR Code

**Padrão Singleton**:
```python
@lru_cache()
def get_settings() -> Settings:
    # Retorna sempre a mesma instância (Singleton)
```

### 3. **app/domain/entities/base.py**
**Propósito**: Classe base abstrata para todas as entidades do domínio.

**Responsabilidades**:
- Fornecer identificador único (UUID)
- Gerenciar timestamps (created_at, updated_at)
- Gerenciar eventos de domínio
- Definir contrato de validação

**Características**:
- Implementa padrão Entity do DDD
- Suporta event sourcing através de domain events
- Força validação através de método abstrato

### 4. **app/domain/entities/user.py**
**Propósito**: Entidade que representa um usuário do sistema.

**Responsabilidades**:
- Encapsular lógica de negócio do usuário
- Validar estado do usuário
- Gerenciar mudanças de estado (ativar, desativar, verificar email)
- Emitir eventos de domínio

**Métodos de Negócio**:
- `update_profile()`: Atualiza informações do perfil
- `change_password()`: Altera senha com evento
- `promote_to_seller()`: Promove usuário a vendedor
- `can_sell()`: Verifica permissão para vender
- `can_buy()`: Verifica permissão para comprar

### 5. **app/domain/entities/product.py**
**Propósito**: Entidade que representa um produto à venda.

**Responsabilidades**:
- Gerenciar ciclo de vida do produto
- Controlar status (disponível, vendido, reservado)
- Aplicar regras de negócio (descontos, reservas)
- Rastrear visualizações

**Métodos de Negócio**:
- `mark_as_sold()`: Marca produto como vendido
- `reserve()`: Reserva produto para comprador
- `apply_discount()`: Aplica desconto percentual
- `set_qr_code()`: Define QR code do produto

### 6. **app/domain/value_objects/**

#### **email.py**
**Propósito**: Objeto de valor imutável que representa um email válido.

**Validações**:
- Formato regex de email
- Tamanho máximo 255 caracteres
- Normalização (lowercase)

#### **cpf.py**
**Propósito**: Objeto de valor para CPF brasileiro com validação.

**Validações**:
- Algoritmo de dígitos verificadores
- Formatação automática
- Rejeita CPFs inválidos (todos dígitos iguais)

#### **phone.py**
**Propósito**: Objeto de valor para telefone brasileiro.

**Validações**:
- Códigos de área válidos
- Formato móvel/fixo
- Geração de link WhatsApp

#### **money.py**
**Propósito**: Objeto de valor para valores monetários com precisão.

**Funcionalidades**:
- Operações matemáticas (soma, subtração, multiplicação)
- Aplicação de descontos
- Formatação por moeda (BRL, USD, EUR)
- Precisão decimal (2 casas)

### 7. **app/domain/repositories/**

#### **base.py**
**Propósito**: Interface base para todos os repositórios (Repository Pattern).

**Métodos Abstratos**:
- `create()`: Criar entidade
- `get_by_id()`: Buscar por ID
- `update()`: Atualizar entidade
- `delete()`: Deletar entidade
- `list()`: Listar com paginação
- `count()`: Contar registros
- `exists()`: Verificar existência

#### **user.py** e **product.py**
Estendem a interface base com métodos específicos:
- `get_by_email()`: Buscar usuário por email
- `get_by_cpf()`: Buscar usuário por CPF
- `get_by_category()`: Buscar produtos por categoria
- `get_by_qr_code()`: Buscar produto por QR code

### 8. **app/infrastructure/database/connection.py**
**Propósito**: Gerenciar conexões com o banco de dados PostgreSQL.

**Responsabilidades**:
- Criar engine assíncrono SQLAlchemy
- Configurar pool de conexões
- Fornecer sessões do banco
- Gerenciar ciclo de vida das conexões

**Dependency Injection**:
```python
async def get_session() -> AsyncSession:
    # Fornece sessão para injeção de dependência
```

### 9. **app/api/v1/endpoints/**

#### **auth.py**
**Propósito**: Endpoints de autenticação e autorização.

**Endpoints**:
- `POST /register`: Registro de novo usuário
- `POST /login`: Login com email/senha
- `POST /refresh`: Renovar token de acesso
- `GET /me`: Obter usuário atual

**Fluxo de Autenticação**:
1. Usuário envia credenciais
2. Sistema valida e gera JWT
3. Cliente armazena token
4. Token enviado em requisições futuras

### 10. **app/api/v1/schemas/**
**Propósito**: Schemas Pydantic para validação de entrada/saída.

**Responsabilidades**:
- Validar dados de entrada
- Serializar dados de saída
- Documentação automática (OpenAPI)
- Type hints para IDE

### 11. **app/shared/exceptions/domain.py**
**Propósito**: Exceções customizadas do domínio.

**Hierarquia**:
```
DomainException (base)
├── DomainValidationError
├── EntityNotFoundError
├── BusinessRuleViolationError
├── UnauthorizedError
└── ConflictError
```

## Padrões de Projeto Utilizados

### 1. **Repository Pattern**
- Abstrai acesso a dados
- Permite trocar implementação (SQL, NoSQL, etc.)
- Localização: `domain/repositories/`

### 2. **Value Object Pattern**
- Objetos imutáveis sem identidade
- Encapsulam validação e comportamento
- Localização: `domain/value_objects/`

### 3. **Factory Pattern**
- Criação de objetos complexos
- Exemplo: `create_application()` em `main.py`

### 4. **Singleton Pattern**
- Uma única instância de configuração
- Implementado com `@lru_cache` em `config.py`

### 5. **Dependency Injection**
- Desacoplamento através de injeção
- FastAPI `Depends()` para injetar sessões

### 6. **Domain Events**
- Comunicação entre agregados
- Rastreabilidade de mudanças
- Implementado em `entities/base.py`

## Fluxo de Requisição

```
Cliente → API Endpoint → Schema Validation → Service Layer → Domain Layer → Repository → Database
         ←              ← Response Schema  ←              ←              ←            ←
```

1. **Cliente** faz requisição HTTP
2. **FastAPI** roteia para endpoint correto
3. **Pydantic** valida dados de entrada
4. **Service** coordena lógica de negócio
5. **Domain** aplica regras de negócio
6. **Repository** persiste/busca dados
7. **Response** é serializada e retornada
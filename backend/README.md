# Coisas de Garagem - API Backend

## Arquitetura

Este backend segue os **princípios SOLID** e **Domain-Driven Design (DDD)**:

- **Single Responsibility**: Cada classe/módulo tem apenas uma razão para mudar
- **Open/Closed**: Aberto para extensão, fechado para modificação
- **Liskov Substitution**: Classes derivadas devem ser substituíveis por suas classes base
- **Interface Segregation**: Muitas interfaces específicas são melhores que uma interface geral
- **Dependency Inversion**: Dependa de abstrações, não de implementações concretas

### Estrutura do Projeto

```
backend/
├── app/
│   ├── api/              # Endpoints da API (Camada de Apresentação)
│   ├── core/             # Configurações centrais
│   ├── domain/           # Entidades, objetos de valor, repositórios
│   ├── infrastructure/   # Serviços externos (BD, Storage, etc.)
│   ├── services/         # Lógica de negócio e casos de uso
│   └── shared/           # Utilitários e exceções compartilhadas
```

## Stack Tecnológica

- **FastAPI**: Framework web assíncrono moderno
- **PostgreSQL**: Banco de dados relacional
- **SQLAlchemy**: ORM com suporte assíncrono
- **Redis**: Cache e gerenciamento de sessões
- **JWT**: Autenticação
- **Docker**: Containerização

## Configuração

### Pré-requisitos

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Instalação

1. Clone e mude para a branch:
```bash
git checkout prototipo-fullstack
```

2. Crie o arquivo `.env`:
```bash
cd backend
cp .env.example .env
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Executando com Docker

```bash
# Do diretório raiz
docker-compose up -d
```

A API estará disponível em `http://localhost:8000`

### Executando localmente

1. Inicie PostgreSQL e Redis
2. Atualize `.env` com suas credenciais
3. Execute as migrações:
```bash
alembic upgrade head
```
4. Inicie o servidor:
```bash
uvicorn app.main:app --reload
```

## Documentação da API

Em modo desenvolvimento, acesse:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Documentação Detalhada

📚 **Documentação completa disponível em `/docs`:**

- [**ARQUITETURA.md**](docs/ARQUITETURA.md) - Explicação detalhada arquivo por arquivo
- [**FLUXO_DE_DADOS.md**](docs/FLUXO_DE_DADOS.md) - Fluxo completo de dados no sistema
- [**FUNCIONALIDADES.md**](docs/FUNCIONALIDADES.md) - Funcionalidades implementadas e pendentes

## Padrões de Projeto Utilizados

1. **Repository Pattern**: Abstrai lógica de acesso a dados
2. **Value Objects**: Conceitos de domínio imutáveis (Email, CPF, Money)
3. **Domain Entities**: Objetos de negócio com comportamento
4. **Service Layer**: Coordenação de lógica de negócio
5. **Dependency Injection**: Baixo acoplamento entre componentes
6. **Factory Pattern**: Criação de aplicação e objetos
7. **Singleton Pattern**: Gerenciamento de configuração

## Funcionalidades Principais

- **Geração de QR Code**: QR codes automáticos para produtos
- **Autenticação JWT**: Autenticação segura baseada em token
- **Controle de Acesso**: Papéis de Comprador, Vendedor, Admin
- **Operações Assíncronas**: Alta performance com async/await
- **Validação de Entrada**: Schemas Pydantic para validação
- **Tratamento de Erros**: Manipulação centralizada de exceções
- **Suporte CORS**: Compartilhamento de recursos entre origens
- **Migrações de BD**: Controle de versão do schema

## Testes

```bash
pytest tests/ -v --cov=app
```

## Contribuindo

1. Siga os princípios SOLID e DRY
2. Escreva testes para novas funcionalidades
3. Atualize a documentação
4. Use type hints
5. Siga o guia de estilo PEP 8
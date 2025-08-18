# 🏪 Coisas de Garagem - API Backend

Sistema de gerenciamento de vendas de garagem (garage sale) desenvolvido em Python com FastAPI e Supabase, seguindo princípios SOLID e Domain-Driven Design (DDD).

## 🚀 Stack Tecnológica

- **FastAPI**: Framework web assíncrono moderno
- **Supabase**: Backend as a Service completo
  - PostgreSQL (banco de dados)
  - Auth (autenticação)
  - Storage (armazenamento de arquivos)
  - Realtime (websockets)
- **SQLAlchemy**: ORM com suporte assíncrono
- **Redis**: Cache e gerenciamento de sessões
- **Docker**: Containerização
- **QR Code**: Geração automática para produtos

## 📋 Arquitetura

Este backend segue os **princípios SOLID** e **Domain-Driven Design (DDD)**:

- **Single Responsibility**: Cada classe/módulo tem apenas uma razão para mudar
- **Open/Closed**: Aberto para extensão, fechado para modificação
- **Liskov Substitution**: Classes derivadas devem ser substituíveis por suas classes base
- **Interface Segregation**: Muitas interfaces específicas são melhores que uma interface geral
- **Dependency Inversion**: Dependa de abstrações, não de implementações concretas

### 📁 Estrutura do Projeto

```
backend/
├── app/
│   ├── api/v1/           # API REST v1
│   │   ├── endpoints/    # Controllers (auth, products, sales, etc)
│   │   ├── schemas/      # Schemas Pydantic para validação
│   │   └── router.py     # Roteador principal da API
│   ├── core/             # Configurações centrais
│   │   └── config.py     # Gerenciamento de configurações
│   ├── domain/           # Camada de domínio (DDD)
│   │   ├── entities/     # Entidades de negócio
│   │   ├── repositories/ # Interfaces de repositórios
│   │   └── value_objects/# Objetos de valor (CPF, Email, Money, Phone)
│   ├── infrastructure/   # Implementações de infraestrutura
│   │   ├── database/     # Conexão com banco de dados
│   │   ├── repositories/ # Implementações dos repositórios
│   │   └── supabase/     # Cliente Supabase
│   ├── services/         # Lógica de negócio
│   │   ├── auth/         # Serviço de autenticação
│   │   ├── product/      # Serviço de produtos
│   │   ├── sale/         # Serviço de vendas
│   │   └── qr_code/      # Serviço de QR codes
│   └── shared/           # Código compartilhado
│       └── exceptions/   # Exceções customizadas
├── migrations/           # Migrations SQL do Supabase
│   └── supabase/        # Scripts SQL para criação de tabelas
├── tests/               # Testes automatizados
├── docs/                # Documentação detalhada
└── requirements.txt     # Dependências Python
```

## 🔧 Configuração

### Pré-requisitos

- Python 3.11+
- Conta no [Supabase](https://supabase.com) (grátis)
- Redis 7+ (opcional, para cache)
- Docker & Docker Compose (opcional)

### Instalação Rápida

1. **Clone o repositório e entre no backend:**
```bash
git clone https://github.com/1harz/CoisasDeGaragem.git
cd CoisasDeGaragem/backend
```

2. **Crie e ative o ambiente virtual:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure o Supabase:**
   - Crie um projeto no [Supabase Dashboard](https://supabase.com)
   - Copie as credenciais (URL, anon key, service key)

5. **Configure o arquivo `.env`:**
```bash
cp .env.example .env
# Edite .env com suas credenciais do Supabase
```

6. **Execute as migrations no Supabase:**
   - Acesse o SQL Editor no Dashboard
   - Execute os arquivos em ordem:
     - `migrations/supabase/001_initial_schema.sql`
     - `migrations/supabase/002_row_level_security.sql`
     - `migrations/supabase/003_storage_setup.sql`

7. **Crie os Storage Buckets:**
   - No Dashboard > Storage
   - Crie 3 buckets públicos: `products`, `qr-codes`, `avatars`

8. **Inicie o servidor:**
```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

## 📚 Documentação

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Documentação Detalhada

📁 **Documentação completa em `/docs`:**

- [**ARQUITETURA.md**](docs/ARQUITETURA.md) - Explicação detalhada arquivo por arquivo
- [**FLUXO_DE_DADOS.md**](docs/FLUXO_DE_DADOS.md) - Fluxo completo de dados no sistema
- [**FUNCIONALIDADES.md**](docs/FUNCIONALIDADES.md) - Funcionalidades implementadas e roadmap
- [**INTEGRACAO_SUPABASE.md**](docs/INTEGRACAO_SUPABASE.md) - Guia de integração com Supabase
- [**SUPABASE_SETUP.md**](docs/SUPABASE_SETUP.md) - Setup completo do Supabase
- [**DIAGRAMAS.md**](docs/DIAGRAMAS.md) - Diagramas de arquitetura e fluxo

## 🎯 Funcionalidades Principais

### ✅ Implementadas
- **Autenticação com Supabase Auth**: Registro, login, tokens JWT
- **Gestão de Produtos**: CRUD completo com categorias
- **Geração de QR Codes**: QR codes únicos para cada produto
- **Sistema de Vendas**: Carrinho, checkout, histórico
- **Upload de Imagens**: Via Supabase Storage
- **Busca e Filtros**: Por categoria, preço, texto
- **Validação de Dados**: CPF, email, telefone
- **Row Level Security**: Segurança a nível de banco

### 🚧 Em Desenvolvimento
- Dashboard de vendedor
- Sistema de avaliações
- Notificações em tempo real
- Relatórios de vendas
- Sistema de mensagens

## 🧪 Testes

```bash
# Executar testes
pytest tests/ -v

# Com coverage
pytest tests/ -v --cov=app

# Testar configuração
python tests/test_setup.py
```

## 🐳 Docker

```bash
# Construir e iniciar
docker-compose up -d

# Parar serviços
docker-compose down

# Ver logs
docker-compose logs -f backend
```

## 🔒 Segurança

- Autenticação JWT via Supabase
- Row Level Security (RLS) no banco
- Validação de entrada com Pydantic
- Sanitização de dados
- CORS configurado
- Rate limiting (em desenvolvimento)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma feature branch (`git checkout -b feature/AmazingFeature`)
3. Siga os princípios SOLID e DDD
4. Escreva testes para novas funcionalidades
5. Atualize a documentação
6. Use type hints e docstrings
7. Siga PEP 8
8. Commit suas mudanças (`git commit -m 'Add: nova funcionalidade'`)
9. Push para a branch (`git push origin feature/AmazingFeature`)
10. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](../LICENSE) para mais detalhes.

## 👥 Autores

- **Rodrigo** - [GitHub](https://github.com/1harz)

## 🙏 Agradecimentos

- FastAPI por um framework incrível
- Supabase pela infraestrutura simplificada
- Comunidade Python pelos pacotes excelentes
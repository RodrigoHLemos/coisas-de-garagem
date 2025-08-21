# Guia de Deployment - Coisas de Garagem

## Arquitetura de Deployment

- **Frontend**: Vercel (HTML/CSS/JS estático)
- **Backend**: Render (FastAPI)
- **Banco de Dados**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage

## Pré-requisitos

1. Conta no [Vercel](https://vercel.com)
2. Conta no [Render](https://render.com)
3. Projeto configurado no [Supabase](https://supabase.com)
4. Repositório no GitHub

## 1. Deploy do Backend no Render

### Configuração Manual (Dashboard)

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em "New" > "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: coisas-de-garagem-api
   - **Branch**: prototipo-fullstack
   - **Root Directory**: backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Variáveis de Ambiente

No dashboard do Render, adicione:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-anon-key
SUPABASE_SERVICE_KEY=sua-service-key
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=gerar-com-openssl-rand-hex-32
ENVIRONMENT=production
CORS_ORIGINS=https://coisas-de-garagem.vercel.app,https://*.vercel.app
```

### Deploy Automático

O arquivo `render.yaml` já está configurado. O Render fará deploy automático a cada push.

## 2. Deploy do Frontend no Vercel

### Via Dashboard

1. Acesse [Vercel Dashboard](https://vercel.com/dashboard)
2. Clique em "Add New" > "Project"
3. Importe o repositório GitHub
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: frontend
   - **Build Command**: (deixar vazio)
   - **Output Directory**: (deixar vazio)

### Via CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Na pasta frontend
cd frontend
vercel

# Seguir prompts
```

### Após o Deploy

1. Copie a URL do backend no Render (ex: https://coisas-de-garagem-api.onrender.com)
2. Atualize `frontend/js/config.js`:
   ```javascript
   return 'https://coisas-de-garagem-api.onrender.com/api/v1';
   ```
3. Faça commit e push - Vercel fará redeploy automático

## 3. Configuração do Supabase

### Migrations

Execute as migrations na ordem:
1. `001_initial_schema.sql`
2. `002_row_level_security.sql`
3. `003_storage_setup.sql`
4. `004_auth_trigger.sql`
5. `005_fix_auth_trigger.sql`
6. `006_fix_auth_trigger_metadata.sql`
7. `007_fix_products_table.sql`

### Storage Buckets

Crie os buckets no Dashboard:
- `products` - Para imagens de produtos
- `qr-codes` - Para QR codes gerados

## 4. Testando o Deploy

### Backend
```bash
curl https://coisas-de-garagem-api.onrender.com/health
```

### Frontend
Acesse: https://coisas-de-garagem.vercel.app

## Troubleshooting

### Backend não responde
- Verificar logs no Render Dashboard
- Apps free dormem após 15 min - primeira requisição demora ~30s

### CORS errors
- Verificar variável CORS_ORIGINS no Render
- Confirmar URL do frontend no Vercel

### Imagens não carregam
- Verificar configuração do Supabase Storage
- Confirmar buckets criados e públicos

## Custos

### Plano Gratuito
- **Vercel**: 100GB bandwidth/mês
- **Render**: 750 horas/mês, app dorme após 15 min
- **Supabase**: 500MB storage, 2GB bandwidth

### Upgrade Recomendado (quando necessário)
- **Render Starter**: $7/mês (app não dorme)
- **Vercel Pro**: $20/mês (analytics, team)
- **Supabase Pro**: $25/mês (8GB storage)

## CI/CD

Ambos os serviços têm deploy automático configurado:
- Push para `prototipo-fullstack` → Deploy automático
- PRs criam preview deployments no Vercel

## Monitoramento

### Logs
- **Render**: Dashboard > Logs
- **Vercel**: Dashboard > Functions > Logs

### Métricas
- **Render**: Dashboard > Metrics
- **Vercel**: Dashboard > Analytics (plano Pro)

## Rollback

### Render
Dashboard > Deploys > Selecionar deploy anterior > "Rollback"

### Vercel
Dashboard > Deployments > Três pontos > "Promote to Production"
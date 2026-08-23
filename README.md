# Hiper Clean CRM

Sistema de CRM para gestão de relacionamento com clientes — **Hiper Clean Limpeza de Estofados**.

Automatiza a descoberta de clientes a serem contactados (aniversários, lembretes pós-atendimento, datas comemorativas) e monta mensagens pré-preenchidas para WhatsApp via links `wa.me`.

## Stack

| Camada | Tecnologia | Deploy |
|--------|-----------|--------|
| Backend | Python, FastAPI, SQLModel, Alembic | Render |
| Banco de dados | Supabase (Postgres gerenciado) | Supabase |
| Frontend | React, Vite | Vercel |

## Arquitetura

```
Frontend (Vercel) ←→ Backend API (Render) ←→ Supabase Postgres
                                                 ↓
                              wa.me links → WhatsApp (envio manual)
```

## Setup Local

### Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Copiar e configurar variáveis de ambiente
cp .env.example .env
# Editar .env com sua DATABASE_URL do Supabase

# Rodar migrations
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

# Copiar e configurar variáveis de ambiente
cp .env.example .env
# Editar .env com a URL da API

# Iniciar dev server
npm run dev
```

### Variáveis de Ambiente

#### Backend (`.env`)
| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATABASE_URL` | Connection string do Supabase | `postgresql://postgres:PASS@db.XXX.supabase.co:5432/postgres` |
| `SECRET_KEY` | Chave secreta para JWT | `sua-chave-secreta-aqui` |
| `ADMIN_EMAIL` | Email de login | `admin@hiperclean.com` |
| `ADMIN_PASSWORD` | Senha de login | `sua-senha-segura` |
| `CORS_ORIGINS` | Origins permitidos (comma-separated) | `http://localhost:5173,https://app.vercel.app` |

#### Frontend (`.env`)
| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `VITE_API_URL` | URL base da API | `https://sua-api.onrender.com` |

## Deploy

### Backend (Render)
1. Criar um Web Service no Render apontando para o diretório `backend/`
2. Build command: `pip install -r requirements.txt && alembic upgrade head`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Configurar variáveis de ambiente

### Frontend (Vercel)
1. Importar o repositório na Vercel
2. Root directory: `frontend/`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Adicionar variável de ambiente `VITE_API_URL`

## Funcionalidades

- ✅ Dashboard com pendentes de hoje agrupados por campanha
- ✅ Botão "Enviar" que abre o WhatsApp com mensagem pré-preenchida
- ✅ Barra de progresso de envios do dia
- ✅ Campanhas configuráveis (aniversário, lembrete pós-atendimento, datas fixas)
- ✅ CRUD completo de clientes, atendimentos e campanhas
- ✅ Autenticação JWT
- ✅ Design dark theme responsivo

# NeuroCap Docker — Deployment

Docker Compose configuration for running the full NeuroCap stack in a single command.

---

## Services

| Service | Image | Port | Description |
|---|---|---|---|
| `backend` | Python 3.11 slim | 8001 | FastAPI + Uvicorn |
| `frontend` | Node 20 + Nginx | 80 | React SPA served by Nginx |

---

## Quick start

```bash
# 1. Copy and fill environment variables
cp ../app/Backend/.env.example ../app/Backend/.env

# 2. Build and start
docker compose up --build

# 3. Access
#   Frontend: http://localhost
#   Backend API: http://localhost:8001
#   API docs: http://localhost:8001/docs
```

---

## docker-compose.yml structure

```yaml
services:
  backend:
    build: ./app/Backend
    ports: ["8001:8001"]
    env_file: ./app/Backend/.env
    restart: unless-stopped

  frontend:
    build: ./app/Frontend
    ports: ["80:80"]
    depends_on: [backend]
    restart: unless-stopped
```

---

## Environment variables

The backend container reads from `app/Backend/.env`. Ensure these are set before building:

```env
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SECRET_KEY=...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

> **Never commit `.env` to version control.**

---

## Production notes

- Use a reverse proxy (Nginx / Caddy) in front for TLS termination.
- Set `SECRET_KEY` to a long random string (e.g. `openssl rand -hex 32`).
- Enable Supabase RLS policies for additional database-level security.
- The frontend Nginx config should proxy `/api` and `/ws` to the backend container.

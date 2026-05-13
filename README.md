# 🦌 WildLog — Hunting Game Tracker

Track game across your hunting group with a clean web dashboard, leaderboard, filters, and saved views.

## Architecture

```
Browser
  └── Nginx (port 8080)
        ├── /          → serves index.html (static)
        └── /api/      → proxied to Flask API (internal)
                              └── SQLite DB (named volume)
```

Two containers, one network, one persistent volume.

---

## Quick Start (Docker)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/wildlog.git
cd wildlog

# 2. Configure
cp .env.example .env
# edit .env if you want a different port

# 3. Build & start
docker compose up -d --build

# 4. Open
open http://localhost:8080
```

Logs:
```bash
docker compose logs -f
```

Stop:
```bash
docker compose down          # keeps data volume
docker compose down -v       # also deletes the database
```

---

## Local Development (without Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py          # runs on :5050

# Frontend — open in browser directly
open frontend/index.html
```

---

## Deployment on Your Own Server

### Option A — Docker Compose (recommended)

```bash
# On your server
git clone https://github.com/YOUR_USERNAME/wildlog.git
cd wildlog
cp .env.example .env

# Set your domain/port in .env
echo "WEB_PORT=80" >> .env

docker compose up -d --build
```

To put it behind a reverse proxy (Nginx/Caddy/Traefik on the host), expose only the `web` container and point your proxy to it. Example Caddyfile snippet:

```
hunting.yourdomain.com {
    reverse_proxy localhost:8080
}
```

### Option B — Pull pre-built images from GHCR

After the CI workflow runs, images are published to GitHub Container Registry:

```bash
# docker-compose.prod.yml override example
services:
  api:
    image: ghcr.io/YOUR_USERNAME/wildlog-api:main
  web:
    image: ghcr.io/YOUR_USERNAME/wildlog-web:main
```

Then:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Configuration

| Variable | Container | Default | Description |
|---|---|---|---|
| `WEB_PORT` | host `.env` | `8080` | Host port for the web UI |
| `DB_PATH` | api | `/app/data/hunting.db` | Path inside container (don't change unless remapping the volume) |
| `CORS_ORIGINS` | api | `*` | Restrict to your domain in production |
| `FLASK_DEBUG` | api | `false` | Set `true` for local dev only |
| `API_URL` | web | `` (empty) | Leave empty — Nginx proxies internally |

---

## Data Persistence

The SQLite database lives in a Docker named volume (`wildlog-data`). It survives container restarts and image updates.

**Backup:**
```bash
docker run --rm \
  -v wildlog-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/wildlog-backup-$(date +%Y%m%d).tar.gz /data
```

**Restore:**
```bash
docker run --rm \
  -v wildlog-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/wildlog-backup-YYYYMMDD.tar.gz -C /
```

---

## CI / CD

Push to `main` → GitHub Actions builds both images and pushes to GHCR automatically.
Tag a release (`v1.2.3`) → versioned images are published.

See `.github/workflows/build.yml`.

---

## Project Structure

```
wildlog/
├── backend/
│   ├── app.py              # Flask API
│   ├── wsgi.py             # Gunicorn entrypoint
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html          # Single-page app
│   └── Dockerfile
├── nginx/
│   ├── default.conf        # Nginx site config
│   └── docker-entrypoint.sh
├── .github/
│   └── workflows/
│       └── build.yml       # CI: build + push to GHCR
├── docker-compose.yml
├── .env.example
└── .gitignore
```

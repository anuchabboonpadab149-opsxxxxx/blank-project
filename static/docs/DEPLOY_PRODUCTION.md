# Production Deployment Guide (VM + Docker + Caddy HTTPS)

This guide helps you deploy the Jasmine x Salmon system to a real server with HTTPS using Caddy.

## Prerequisites

- A VM (Ubuntu/Debian preferred) with public IP
- A domain name pointing (A record) to the VM IP
- Docker + Docker Compose installed
- Open ports 80 and 443 on firewall (and 22 for SSH)

## 1) Configure environment

Edit `.env` (use `.env.example` as reference):

- DOMAIN=your.domain.com
- ACME_EMAIL=admin@your.domain.com
- PUBLIC_URL=https://your.domain.com
- CORS_ALLOW_ORIGIN=https://your.domain.com
- AI_PROVIDER=gemini
- GEMINI_API_KEY=YOUR_KEY
- GEMINI_MODEL=gemini-1.5-flash

Other core variables:
- RUN_MODE=daemon
- TIMEZONE=Asia/Bangkok
- WEB_DASHBOARD=true
- WEB_PORT=8000

## 2) DNS

Create/verify DNS A record:
- your.domain.com -> YOUR_VM_PUBLIC_IP

## 3) Start services

Use the production compose file with Caddy:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

This will:
- Build and start the app (`promote-ayutthaya`)
- Start Caddy reverse proxy, obtain Let's Encrypt certificates automatically
- Serve HTTPS at https://your.domain.com

To check logs:
```bash
docker compose logs -f --tail=200
```

## 4) Verify

Open:
- https://your.domain.com
- https://your.domain.com/healthz
- https://your.domain.com/events
- https://your.domain.com/tony

On first run, the app runs in DEMO mode; to enable AI:
- Set GEMINI_API_KEY in `.env`
- Restart: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

## 5) Credentials

Visit https://your.domain.com/credentials to add provider keys at runtime. Values are stored in `credentials.json` and applied without restarts.

## 6) Optional: Render/Heroku

- Heroku: Use `Procfile` and set env `PORT` (app auto-detects `PORT` for WEB_PORT).
- Render: Use Docker deploy; set Health check path `/healthz`.

## 7) Backup and persistence

By default, Caddy stores TLS data in Docker volumes `caddy_data` and `caddy_config`.
App outputs/credentials are stored in the container filesystem if not mounted; mount volumes as needed.

## 8) Troubleshooting

- DNS not propagated: wait or verify with `dig your.domain.com`
- Port blocked: open 80/443 on firewall
- ACME rate limit: ensure DOMAIN is reachable over port 80
- Mixed Content: always use HTTPS URLs on the frontend; set `CORS_ALLOW_ORIGIN` to your domain
- SSE issues: Caddy supports SSE out-of-the-box; ensure reverse proxy points to the app on port 8000

Happy shipping.
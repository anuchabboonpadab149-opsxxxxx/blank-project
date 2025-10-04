# Jasmine x Salmon — Autonomous Social + Podcast Machine

An always-on, 24/7 autonomous content system that:
- Generates Thai comedic/romantic content (Jasmine x Salmon persona) every second
- Produces audio/image/video (gTTS + Pillow + moviepy)
- Streams live events via SSE to a web dashboard
- Distributes to multiple social platforms (Twitter/X, Facebook/IG, LinkedIn, LINE, Telegram, Discord, Reddit, Mastodon, TikTok Ads placeholder)
- Supports Twitter Ads (campaign, line-items, metrics)
- Operates with circuit breaker and retry backoff for resilience
- Provides a credentials UI to inject real keys at runtime without restarts

The project is optimized to run fully unattended and be observable and configurable in real-time.

---

## Features

- 24/7 Scheduler (APScheduler): 
  - Default: post every 1 second, collect analytics every 1 minute
  - Reschedulable at runtime via API/UI
- Live Dashboard (Flask + SSE): 
  - `/` events feed, latest media, settings
  - `/events` Server-Sent Events (SSE)
  - `/api/recent`, `/api/feed`, `/api/latest`
  - `/credentials` for runtime key injection (masked readback)
  - `/nodes`, `/about`, `/workflows`
  - `/healthz` health endpoint
- Media generation:
  - Audio (gTTS, Thai)
  - Quote card images (Pillow + Thai fonts)
  - Video (moviepy + ffmpeg)
- Providers dispatcher with Circuit Breaker (open/half-open/closed), retry backoff, and optional simulation
- Zero-downtime configuration updates `/api/config` (providers, intervals, persona words, etc.)

---

## Quickstart (Docker Compose)

Prerequisites:
- Docker + Docker Compose plugin

Start:
```bash
docker compose up -d --build
```

Open dashboard:
- Local: http://localhost:8000
- LAN example: http://192.168.10.121:8000

Health check:
```bash
curl http://localhost:8000/healthz
```

Live events (SSE):
```bash
curl http://localhost:8000/events
```

---

## Environment (.env)

See [.env.example](./.env.example) for all supported variables. Common ones:
```
RUN_MODE=daemon
TIMEZONE=Asia/Bangkok

WEB_DASHBOARD=true
WEB_PORT=8000

POST_INTERVAL_SECONDS=1
COLLECT_INTERVAL_MINUTES=1

PROVIDERS=twitter,facebook,linkedin,line,telegram,discord,instagram,reddit,tiktok,mastodon
DISTRIBUTE_ALL=true

# Safety defaults for first run (if you do not want real posts yet)
SIMULATE_ALL_PROVIDERS=false
SIMULATE_ON_ERROR=false

CONTENT_MODE=generate
SENDER_NAME=จัสมินชอบกินแซลมอน
```

Tip: For real postings, put your keys in `.env` or add them at runtime via `/credentials`.

---

## Tony Fortune Platform (Premium Credits + LLM + Vision)

Landing website and app:
- Website (landing): `/tony-site`
- App (fortune services): `/tony`
- Admin approvals (top-up): `/tony/admin`

User flow:
1. Register/Login at `/tony`
2. Top-up credits by uploading a slip (manual approval)
3. Use any fortune service (1 credit per use)
4. View your history

Services:
- Astrology (dob/tob + question)
- Tools (tarot/dice/siamsee/pok)
- Analysis (palm/face via image, dream via text)
- Numbers (phone/license/name)

Credits and top-up:
- Manual approval with `ADMIN_SECRET` at `/tony/admin`
- Default packages: 100฿→10, 300฿→35, 500฿→60 (configurable in `user_store.py`)

LLM and Vision:
- Supports OpenAI and Gemini for text and vision (image inline base64)
- Prompt templates per science can be edited at `/credentials` (saved to runtime config)

Required env:
```
# Sessions & Admin
SECRET_KEY=change-me-tony-secret
ADMIN_SECRET=your-strong-secret
TONY_ADMINS=adminuser1,adminuser2

# LLM provider selection and keys
LLM_PROVIDER=openai            # or gemini
OPENAI_API_KEY=...             # if using OpenAI
OPENAI_MODEL=gpt-4o-mini       # default suggested
GEMINI_API_KEY=...             # if using Gemini
GEMINI_MODEL=gemini-1.5-flash  # default suggested
```

How to configure:
1. Set `SECRET_KEY`, `ADMIN_SECRET` in `.env` (strong values)
2. Open `/credentials` and set `LLM_PROVIDER` and API keys (OpenAI or Gemini)
3. Optionally edit prompt templates per science in the same page
4. Go to `/tony` to register/login and test services; use `/tony/admin` to approve top-ups

Data files:
- `outputs/tony_transactions.jsonl` — credit changes, top-up requests
- `outputs/tony_history.jsonl` — user fortune history
- `outputs/uploads` — uploaded images (palm/face), `outputs/topups` — slips

---

## Credentials (Runtime)

Open the credentials UI:
- http://localhost:8000/credentials

API:
```
GET  /api/credentials       # returns masked credentials
POST /api/credentials       # accepts JSON with allowed keys
```

Allowed keys include:
- Twitter: `TW_CONSUMER_KEY`, `TW_CONSUMER_SECRET`, `TW_ACCESS_TOKEN`, `TW_ACCESS_TOKEN_SECRET`, `TW_BEARER_TOKEN`
- Facebook/IG: `FB_PAGE_ID`, `FB_ACCESS_TOKEN`, `IG_USER_ID`, `IG_IMAGE_URL`
- LinkedIn: `LI_ACCESS_TOKEN`, `LI_ORG_URN`
- LINE: `LINE_CHANNEL_ACCESS_TOKEN`
- Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- Discord: `DISCORD_WEBHOOK_URL`
- Reddit: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`, `REDDIT_SUBREDDIT`
- Mastodon: `MASTODON_BASE_URL`, `MASTODON_ACCESS_TOKEN`
- TikTok Ads (placeholder): `TIKTOK_APP_ID`, `TIKTOK_SECRET`, `TIKTOK_ADVERTISER_ID`
- Twitter Ads: `ADS_ACCOUNT_ID`, `FUNDING_INSTRUMENT_ID`, `CAMPAIGN_ID`, `LINE_ITEM_ID`, `ADS_ENTITY_IDS`
- LLM: `LLM_PROVIDER`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `GEMINI_API_KEY`, `GEMINI_MODEL`

---

## Makefile (Convenience)

Use [Makefile](./Makefile) to streamline operations:
- `make up` — build and start
- `make down` — stop
- `make logs` — follow logs
- `make health` — GET /healthz
- `make post` — POST /api/post-now
- `make reload` — POST /api/reload-schedule
- `make feed` — GET /api/feed

Override host:
```bash
make health HOST=192.168.10.121:8000
```

---

## Architecture

Key modules:
- `cli.py` — Orchestrates scheduler, starts web dashboard in background, handles "post" and "collect" jobs; emits SSE events.
- `web_dashboard.py` — Flask app (SSE events, settings, credentials, nodes, workflows, metrics, Tony platform & site).
- `content_generator.py` — Persona-based content (auto-switch to Jasmine x Salmon based on SENDER_NAME or runtime config).
- `media_generator.py` — gTTS audio, Pillow image (Thai fonts), moviepy video.
- `social_dispatcher.py` — Dispatch to providers with Circuit Breaker wrapper and optional simulation.
- `realtime_bus.py` — In-memory + JSONL events, SSE streaming.
- `config_store.py` — JSON runtime config with concurrency control and prompt templates.
- `credentials_store.py` — Securely stores credentials.json (masked GET, env injection on update).
- `user_store.py` — Users, credits, top-up requests, and history for Tony platform.
- `divination_engine.py` — Rule-based + LLM-backed divination and vision.
- `promote_ayutthaya.py` — X/Twitter + Ads utilities (campaign/line-items/metrics).

HTTP Endpoints:
- `/` — dashboard
- `/tony-site` — Tony official website (landing)
- `/tony` — Tony app (fortune + credits)
- `/tony/admin` — Admin approvals
- `/events` — SSE
- `/api/recent`, `/api/feed`, `/api/latest`
- `/api/config` (GET/POST), `/api/reload-schedule`, `/api/post-now`
- `/api/credentials` (GET/POST)
- `/api/metrics`, `/api/circuit-states`, `/api/workflows`
- `/api/nodes`, `/api/nodes/register`, `/api/nodes/heartbeat`, `/api/nodes/summary`
- `/media/...` serve outputs/ files
- `/healthz` healthcheck

More docs:
- [SSH and Backend Guide](./static/docs/SSH_BACKEND_GUIDE.md)
- [Architecture Deep Dive](./static/docs/ARCHITECTURE.md)
- [Operations Playbook](./static/docs/OPERATIONS.md)

---

## LAN vs Public Hosting

- LAN: Access dashboard at `http://LAN_IP:8000`. No mixed content issues.
- Public: If the front page is HTTPS and backend is HTTP (LAN), browsers may block mixed content. Consider:
  - Opening dashboard directly via LAN
  - Adding a reverse proxy with HTTPS (Caddy/NGINX/Traefik)

---

## Security Hardening (SSH Shortlist)

- Use key-based auth; disable passwords after confirming keys work
- `PermitRootLogin no` in sshd_config
- Restrict auth tries, keepalive settings
- Apply file permissions:
  ```
  chmod 700 ~/.ssh
  chmod 600 ~/.ssh/authorized_keys
  ```

Refer to Cisco SSH hardening guidance and your org's policy.

---

## Troubleshooting

- Connection refused: backend or sshd not running / firewall closed
- Permission denied (publickey): recheck key + permissions
- Timeout: network/firewall/NAT not set up
- Mixed Content: HTTPS page calling HTTP backend — open via LAN or add HTTPS to backend

---

## License

Proprietary — for internal deployment and evaluation unless otherwise agreed.
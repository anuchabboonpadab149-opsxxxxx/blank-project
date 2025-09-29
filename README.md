Fortune System - Microservices + Web

Overview
This repository contains:
- Microservices (FastAPI) for gateway, credit, payment, fortune
- Docker Compose for local/prod orchestration
- Static Web (web/) ready to deploy to a free domain
- Basic test suite (pytest)

Run with Docker Compose
1) Set up environment (optional)
   export INTERNAL_TOKEN=internal-secret
   export PROMPTPAY_ID=0916974995
   export ADMIN_TOKEN=admin-secret

2) Build and start
   docker compose up --build

Services
- Gateway: http://localhost:8000
- Credit:  http://localhost:8001
- Payment: http://localhost:8002
- Fortune: http://localhost:8003

Gateway (Public API)
- POST /auth/register
- POST /auth/login
- POST /auth/logout
- GET  /packages
- POST /payment/create
- POST /payment/verify
- GET  /payment/status/{tx_id}
- GET  /user/credits
- GET  /user/history/all
- GET  /fortune/sources
- POST /fortune/draw                  # Sen-Si (1 credit)
- POST /fortune/tarot/draw-multi      # Tarot multi: count=5 (1 credit) or 10 (2 credits)

Admin (via Gateway)
- GET  /admin/dashboard               (Header: Authorization: Bearer <ADMIN_TOKEN>)
- POST /admin/payment/confirm
- POST /admin/content/source
- POST /admin/content/sen-si
- POST /admin/content/tarot

Internal Contracts
- Credit:
  - POST /internal/credits/add
  - POST /internal/credits/deduct
  - GET  /internal/credits/{user_id}
  - GET  /internal/admin/stats
- Payment:
  - POST /internal/payment/create
  - POST /internal/payment/verify
  - POST /internal/payment/confirm
  - GET  /internal/payment/lookup/{tx_id}
  - GET  /internal/payment/user-history/{user_id}
  - GET  /internal/packages
  - GET  /internal/admin/stats
- Fortune:
  - GET  /internal/fortune/sources
  - POST /internal/fortune/execute
  - POST /internal/fortune/tarot-multi
  - POST /internal/fortune/record
  - GET  /internal/fortune/user-history/{user_id}
  - Admin: /internal/admin/source, /internal/admin/sen-si, /internal/admin/tarot, /internal/admin/stats

PromptPay QR (Real)
- Implemented via Python library `promptpay`
- Payment service generates EMVCo payload and on-the-fly QR PNG
- Response includes both qr_payload and qr_code_url

Static Web
- web/index.html: Landing (temple plaques), full flow in-page (auth → buy → pay → draw), tabs for Sen-Si and Tarot (5/10)
- web/admin/index.html: dashboard + confirm payment + content management (hidden route; open with Alt+Shift+A)
- web/config.js: set API_BASE and ADMIN_BEARER (or set at runtime)

Local Dev (without Docker)
- Install deps: pip install -r requirements.txt
- Start services in separate shells:
  uvicorn services.credit.app.main:app --port 8001
  uvicorn services.payment.app.main:app --port 8002
  uvicorn services.fortune.app.main:app --port 8003
  uvicorn services.gateway.app.main:app --port 8000
- Open web/index.html in a static server and set API_BASE to http://localhost:8000

Deploy on Render (example)
- See deploy/render.yaml. Create 4 web services (one per folder).
- Set environment variables:
  - All: INTERNAL_TOKEN
  - Gateway: ADMIN_TOKEN, CREDIT_SERVICE_URL, PAYMENT_SERVICE_URL, FORTUNE_SERVICE_URL, CORS_ALLOW_ORIGINS
  - Payment: PROMPTPAY_ID, PUBLIC_BASE_URL (its own public URL)
- Point the static web (cosine.page or any CDN) to the gateway domain via APP_CONFIG.API_BASE in web/config.js or ?api= query string.

Tests
- Run: pytest

Monolith (legacy)
- Old monolith (app/) remains for reference and can be run with:
  uvicorn app.main:app --reload
  Note: Payment QR in monolith is mocked; the microservices path uses real PromptPay payload.
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
- GET  /user/credits
- GET  /user/history/all
- GET  /fortune/sources
- POST /fortune/draw

Admin (via Gateway)
- POST /admin/payment/confirm  (Header: Authorization: Bearer <ADMIN_TOKEN>)
- POST /admin/content/source
- POST /admin/content/sen-si
- POST /admin/content/tarot

Internal Contracts
- Credit: /internal/credits/add, /internal/credits/deduct, /internal/credits/{user_id}
- Payment: /internal/payment/create, /internal/payment/verify, /internal/payment/confirm, /internal/payment/lookup/{tx_id}, /internal/payment/user-history/{user_id}, /internal/packages
- Fortune: /internal/fortune/sources, /internal/fortune/execute, /internal/fortune/record, /internal/fortune/user-history/{user_id}, admin endpoints above

PromptPay QR (Real)
- Implemented via Python library `promptpay`
- Payment service generates EMVCo payload and on-the-fly QR PNG
- Response includes both qr_payload and qr_code_url

Static Web
- web/index.html: user flows (register/login, buy, scan QR, verify slip, draw fortune, credits/history)
- web/admin.html: confirm payment and manage content
- web/config.js: set API_BASE and ADMIN_BEARER (or set at runtime)

Local Dev (without Docker)
- Install deps: pip install -r requirements.txt
- Start services in separate shells:
  uvicorn services.credit.app.main:app --port 8001
  uvicorn services.payment.app.main:app --port 8002
  uvicorn services.fortune.app.main:app --port 8003
  uvicorn services.gateway.app.main:app --port 8000
- Open web/index.html in a static server and set API_BASE to http://localhost:8000

Tests
- Run: pytest

Monolith (legacy)
- Old monolith (app/) remains for reference and can be run with:
  uvicorn app.main:app --reload
  Note: Payment QR in monolith is mocked; the microservices path uses real PromptPay payload.
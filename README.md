Fortune API - FastAPI Implementation

Overview
This is a working scaffold that implements the External (Public) API and Internal (Microservices) API described in the blueprint. It uses FastAPI, SQLAlchemy and JWT Auth with SQLite by default.

Quickstart
1) Install dependencies
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt

2) Run the server
   uvicorn app.main:app --reload

3) Default config (env)
   - DATABASE_URL=sqlite:///./app.db
   - JWT_SECRET=dev-secret-change-me
   - JWT_EXPIRES_MIN=60
   - INTERNAL_TOKEN=internal-secret

Key Endpoints (External)
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

Key Endpoints (Internal)
- POST /internal/credits/deduct
- POST /internal/credits/add
- GET  /internal/credits/{user_id}
- POST /internal/payment/process-success
- GET  /internal/payment/lookup/{tx_id}
- POST /internal/fortune/execute
- POST /internal/fortune/record

Notes
- Payment QR is mocked with a placeholder URL for now. Integrate a PromptPay QR generator later.
- Data is seeded with a few packages, a Sen_Si source and sample slips, and a Tarot source with a few cards.
- This monolith simulates microservices with Internal endpoints secured via X-Internal-Token.
# Backend Deployment Guide (Production)

This repository contains 4 services:
- gateway (Public API + Admin)
- credit-service
- payment-service (PromptPay QR)
- fortune-service

We recommend deploying to Render using the Blueprint file `deploy/render.yaml`.

## One-time Setup on Render (5–10 minutes)
1) Create a new Render account (or log in).
2) Click "New" → "Blueprint" and connect this repository.
3) Render will create 4 Web Services automatically from `deploy/render.yaml`.

Environment variables:
- We already set secure defaults in `deploy/render.yaml`:
  - gateway:
    - ADMIN_TOKEN = prod-admin-7KcG3N2wVtLxq8P4nY1rS9mZ6uQ0bF5D
    - JWT_SECRET  = prod-jwt-3u7Q3V6rBnZq1mT8fWc4yH9pLk2s
    - INTERNAL_TOKEN = internal-secret (change if desired)
    - CREDIT_SERVICE_URL / PAYMENT_SERVICE_URL / FORTUNE_SERVICE_URL = placeholders; update after first deploy
  - payment-service:
    - PROMPTPAY_ID = 0916974995 (replace with your real PromptPay ID)
    - PUBLIC_BASE_URL = set to the payment-service URL after first deploy
- After the first deploy completes, copy each service URL (credit/payment/fortune) and paste them into the gateway service ENV:
  - CREDIT_SERVICE_URL = https://<credit-service>.onrender.com
  - PAYMENT_SERVICE_URL = https://<payment-service>.onrender.com
  - FORTUNE_SERVICE_URL = https://<fortune-service>.onrender.com
- Also set `PUBLIC_BASE_URL` on payment-service to its own Render URL.
- Redeploy gateway and payment-service.

Health checks:
- All services expose /healthz; Render will keep them healthy.

## Option B: Docker Compose on a VPS
1) Install Docker & Docker Compose.
2) Create a `.env` file (example):
   ```
   INTERNAL_TOKEN=internal-secret
   ADMIN_TOKEN=prod-admin-7KcG3N2wVtLxq8P4nY1rS9mZ6uQ0bF5D
   PROMPTPAY_ID=0916974995
   ```
3) Run:
   ```
   docker compose up --build -d
   ```
4) Put Nginx in front of the gateway (http://localhost:8000) with HTTPS.

## Web Frontend (Production)
- The static site reads API base from:
  - URL param: `?api=https://<gateway-domain>`
  - LocalStorage: `api_base_override`
  - Fallback in `web/config.js`
- After gateway is live, update `web/config.js` to set API_BASE to your gateway domain and redeploy `web/`.

## Admin Access
- Visit: https://<frontend-domain>/admin/index.html
- Enter `ADMIN_TOKEN` from gateway ENV to operate admin functions.
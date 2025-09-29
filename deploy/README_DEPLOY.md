# Backend Deployment Guide

This repository contains 4 services:
- gateway (public API + admin)
- credit-service
- payment-service (PromptPay QR)
- fortune-service

## Option A: Render (recommended free starter)
1) Connect this repo to Render.
2) Render auto-detects `deploy/render.yaml`. It will create 4 services.
3) After first deploy, update environment variables on the `gateway` service:
   - INTERNAL_TOKEN = internal-secret
   - ADMIN_TOKEN = your-production-admin-token
   - CREDIT_SERVICE_URL = the Render URL of credit-service (e.g., https://credit-service.onrender.com)
   - PAYMENT_SERVICE_URL = the Render URL of payment-service
   - FORTUNE_SERVICE_URL = the Render URL of fortune-service
   - CORS_ALLOW_ORIGINS = *
4) On `payment-service`, set:
   - PROMPTPAY_ID = your PromptPay ID (phone or e-wallet ID)
   - Optionally set PUBLIC_BASE_URL to the `payment-service` URL if you want its internal QR endpoint to be directly fetchable.
5) Redeploy. Test gateway at its public URL.

## Option B: Docker Compose on a VPS
1) Install Docker & Docker Compose.
2) Create a `.env` file with:
   ```
   INTERNAL_TOKEN=internal-secret
   ADMIN_TOKEN=admin-secret
   PROMPTPAY_ID=0916974995
   ```
3) Run:
   ```
   docker compose up --build
   ```
4) Reverse proxy the `gateway` (http://localhost:8000) via Nginx and set HTTPS.

## Web Frontend
The static site reads API base from:
- URL param: `?api=https://your-gateway-domain`
- LocalStorage key `api_base_override`
- Fallback in `web/config.js`

Deploy the `web/` folder to any static host and point it to your gateway domain.
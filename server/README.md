# อ.โทนี่สะท้อนกรรม — Backend API

Node.js + Express backend for real authentication, credits, and PromptPay via Stripe or SCB Payment Gateway (เลือกได้ด้วย PAY_PROVIDER).

## Features

- User signup/login with token (JWT)
- Credits: consume 1 credit per reading
- Packages listing (5 promotions)
- Payment provider selectable:
  - Stripe PromptPay (PaymentIntent → QR image URL → webhook)
  - SCB Payment Gateway/Open API (Create QR → webhook or polling check)
- Poll order status endpoint (refresh from provider)
- Webhook endpoint (Stripe or SCB) to auto-credit on payment success
- SQLite database (better-sqlite3)

## Quick start

1) Install dependencies

```
cd server
npm install
```

2) Configure environment

```
cp .env.example .env
```

Edit `.env`:

- Set `PAY_PROVIDER=stripe` or `PAY_PROVIDER=scb`

Stripe:
- `STRIPE_SECRET_KEY` — from your Stripe account (enable PromptPay)
- `STRIPE_WEBHOOK_SECRET` — webhook signing secret from Stripe Dashboard

SCB:
- `SCB_OAUTH_URL` — OAuth token endpoint
- `SCB_CLIENT_ID`, `SCB_CLIENT_SECRET` — SCB OAuth credentials
- `SCB_QR_CREATE_URL` — API endpoint to create dynamic QR
- `SCB_CHECK_BILLPAY_URL` — API endpoint to check bill payment status (ref1/ref2/date)
- `SCB_MERCHANT_ID`, `SCB_TERMINAL_ID`, `SCB_BILLER_ID` — merchant parameters required by SCB
- `SCB_WEBHOOK_SECRET` — shared secret to validate webhook requests (query/header)

Common:
- `JWT_SECRET` — random string for JWT
- `PORT` — default 3000
- `CORS_ORIGIN` — your frontend origin (e.g., https://your-domain.com)

3) Run server

```
npm start
```

4) Frontend

In `tarot-app/index.html`, ensure:

```html
<script>
  window.API_BASE = "http://localhost:3000"; // or your deployed server URL
</script>
```

Deploy frontend and backend; the site will consume credits and show real QR codes depending on provider.

## Webhook setup

Stripe:
- Set Webhook endpoint:
  ```
  https://your-server.com/api/webhooks/stripe
  ```
- Use `STRIPE_WEBHOOK_SECRET` to verify header `Stripe-Signature`.

SCB:
- Set Webhook endpoint:
  ```
  https://your-server.com/api/webhooks/scb?secret=SCB_WEBHOOK_SECRET
  ```
- Or send header `x-scb-webhook-secret: SCB_WEBHOOK_SECRET`.
- On payment success, send payload containing `ref1` and `status` (exact format depends on SCB setup).

## API

- `GET /api/packages` — list packages
- `POST /api/signup { name, phone, password }` — returns `{ token }`
- `POST /api/login { phone, password }` — returns `{ token }`
- `GET /api/me` — returns `{ name, phone, credits }`
- `POST /api/credits/consume` — deduct 1 credit
- `POST /api/topup/create-order { packageId }` — returns `{ orderId, qrImage }`
- `GET /api/orders/:orderId` — returns `{ status }` and refreshes from provider
- `POST /api/webhooks/stripe` — Stripe events webhook (auto-credit)
- `POST /api/webhooks/scb` — SCB webhook (auto-credit)

## Database

`data.sqlite` created automatically.

Tables:
- `users(id, phone UNIQUE, name, password_hash, credits INTEGER DEFAULT 0)`
- `orders(id, order_id TEXT UNIQUE, user_id INTEGER, package_id TEXT, credits INTEGER, amount INTEGER, status TEXT, pi_id TEXT, created_at TEXT)`

Notes:
- For Stripe, `pi_id` stores PaymentIntent ID.
- For SCB, `pi_id` stores `ref1` (reference1) to match bill payment checks/webhooks.

## Deployment

- Use a Node.js host (Render, Railway, Fly.io, etc.)
- Ensure HTTPS and public access for webhook
- Configure firewall to allow provider webhook IPs if needed

## Notes

- Amounts are in satang (`THB * 100`)
- If webhook is not yet configured, frontend can poll via `/api/orders/:orderId` to detect payment completion and auto-credit.
- For security, always use HTTPS and strong secrets.
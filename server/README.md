# อ.โทนี่สะท้อนกรรม — Backend API

Node.js + Express backend for real authentication, credits, and PromptPay via Stripe. Handles creating PaymentIntents for PromptPay, returning QR code image URL for scanning, polling status, and secure webhook updates to credit users automatically.

## Features

- User signup/login with token (JWT)
- Credits: consume 1 credit per reading
- Packages listing (5 promotions)
- Create PromptPay PaymentIntent via Stripe and return QR image URL (`next_action.promptpay_display_qr_code.image_url`)
- Poll order status endpoint (refresh from Stripe PaymentIntent)
- Webhook endpoint for Stripe events (`payment_intent.succeeded`) to auto-credit on payment success
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

- `STRIPE_SECRET_KEY` — from your Stripe account (enable PromptPay)
- `STRIPE_WEBHOOK_SECRET` — webhook signing secret from Stripe Dashboard
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

Deploy frontend and backend; the site will consume credits and show real Stripe PromptPay QR codes.

## Webhook setup (Stripe)

- In Stripe Dashboard, set Webhook endpoint to:

```
https://your-server.com/api/webhooks/stripe
```

- Use `STRIPE_WEBHOOK_SECRET` from `.env` in the backend to verify the signature header `Stripe-Signature`.
- On `payment_intent.succeeded`, backend marks the order as paid and credits the user automatically.

## API

- `GET /api/packages` — list packages
- `POST /api/signup { name, phone, password }` — returns `{ token }`
- `POST /api/login { phone, password }` — returns `{ token }`
- `GET /api/me` — returns `{ name, phone, credits }`
- `POST /api/credits/consume` — deduct 1 credit
- `POST /api/topup/create-order { packageId }` — returns `{ orderId, qrImage }`
- `GET /api/orders/:orderId` — returns `{ status }` and refreshes from Stripe
- `POST /api/webhooks/stripe` — Stripe events webhook (auto-credit)

## Database

`data.sqlite` created automatically.

Tables:
- `users(id, phone UNIQUE, name, password_hash, credits INTEGER DEFAULT 0)`
- `orders(id, order_id TEXT UNIQUE, user_id INTEGER, package_id TEXT, credits INTEGER, amount INTEGER, status TEXT, pi_id TEXT, created_at TEXT)`

## Deployment

- Use a Node.js host (Render, Railway, Fly.io, etc.)
- Ensure HTTPS and public access for webhook
- Configure firewall to allow Stripe webhook IPs if needed

## Notes

- Amounts are in satang (`THB * 100`)
- If webhook is not yet configured, frontend can poll via `/api/orders/:orderId` to detect payment completion and auto-credit.
- For security, always use HTTPS and strong secrets.
# อ.โทนี่สะท้อนกรรม — Backend API

Node.js + Express backend for real authentication, credits, and PromptPay via Omise (Opn). Handles creating PromptPay QR charges, polling status, and secure webhook updates to credit users automatically.

## Features

- User signup/login with token (JWT)
- Credits: consume 1 credit per reading
- Packages listing (5 promotions)
- Create PromptPay order via Omise and return QR image URI
- Poll order status endpoint (refresh from Omise)
- Webhook endpoint for Omise events to auto-credit on payment success
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

- `OMISE_PUBLIC_KEY` and `OMISE_SECRET_KEY` — from your Omise/Opn account (enable PromptPay)
- `WEBHOOK_SECRET` — random string to verify webhooks (see below)
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

Deploy frontend and backend; the site will consume credits and show real Omise PromptPay QR codes.

## Webhook setup (Omise)

- In Omise Dashboard, set Webhook URL to:

```
https://your-server.com/api/webhooks/omise?secret=WEBHOOK_SECRET_VALUE
```

Replace `WEBHOOK_SECRET_VALUE` with your `WEBHOOK_SECRET` from `.env`.

- On `charge.complete` event, if `status === "successful"`, backend marks the order paid and credits the user automatically.

Note: If you want signature verification, we support the header names `omise-signature` or `x-omise-signature`. The signature should be HMAC SHA256 of raw body with `WEBHOOK_SECRET`. If your account uses a different header name, adjust in `server.js` (verifyWebhookSignature).

## API

- `GET /api/packages` — list packages
- `POST /api/signup { name, phone, password }` — returns `{ token }`
- `POST /api/login { phone, password }` — returns `{ token }`
- `GET /api/me` — returns `{ name, phone, credits }`
- `POST /api/credits/consume` — deduct 1 credit
- `POST /api/topup/create-order { packageId }` — returns `{ orderId, qrImage }`
- `GET /api/orders/:orderId` — returns `{ status }` and refreshes from Omise
- `POST /api/webhooks/omise` — Omise events webhook (auto-credit)

## Database

`data.sqlite` created automatically.

Tables:
- `users(id, phone UNIQUE, name, password_hash, credits INTEGER DEFAULT 0)`
- `orders(id, order_id TEXT UNIQUE, user_id INTEGER, package_id TEXT, credits INTEGER, amount INTEGER, status TEXT, charge_id TEXT, created_at TEXT)`

## Deployment

- Use a Node.js host (Render, Railway, Fly.io, etc.)
- Ensure HTTPS and public access for webhook
- Configure firewall to allow Omise webhook IPs if needed

## Notes

- Amounts are in satang (`THB * 100`)
- If webhook is not yet configured, frontend can poll via `/api/orders/:orderId` to detect payment completion and auto-credit.
- For security, always use HTTPS and strong secrets.
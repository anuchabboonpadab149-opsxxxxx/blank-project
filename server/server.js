/**
 * อ.โทนี่สะท้อนกรรม — Backend API (Express + SQLite + Stripe PromptPay or SCB Payment Gateway)
 */
const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const Database = require('better-sqlite3');
const Stripe = require('stripe');
const fetch = require('node-fetch');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

dotenv.config();

const PORT = process.env.PORT || 3000;
const CORS_ORIGIN = process.env.CORS_ORIGIN || '*';
const JWT_SECRET = process.env.JWT_SECRET || 'change_this_jwt_secret';

const PAY_PROVIDER = (process.env.PAY_PROVIDER || 'stripe').toLowerCase();

// Stripe
const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY || '';
const STRIPE_WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET || '';
const stripe = STRIPE_SECRET_KEY ? new Stripe(STRIPE_SECRET_KEY) : null;

// SCB
const SCB_OAUTH_URL = process.env.SCB_OAUTH_URL || '';
const SCB_CLIENT_ID = process.env.SCB_CLIENT_ID || '';
const SCB_CLIENT_SECRET = process.env.SCB_CLIENT_SECRET || '';
const SCB_QR_CREATE_URL = process.env.SCB_QR_CREATE_URL || '';
const SCB_CHECK_BILLPAY_URL = process.env.SCB_CHECK_BILLPAY_URL || '';
const SCB_MERCHANT_ID = process.env.SCB_MERCHANT_ID || '';
const SCB_TERMINAL_ID = process.env.SCB_TERMINAL_ID || '';
const SCB_BILLER_ID = process.env.SCB_BILLER_ID || '';
const SCB_WEBHOOK_SECRET = process.env.SCB_WEBHOOK_SECRET || '';

const app = express();

// Capture raw body for webhook signature verify
app.use(express.json({
  verify: (req, res, buf) => {
    req.rawBody = buf.toString();
  }
}));
app.use(cors({
  origin: CORS_ORIGIN,
  credentials: true,
}));
app.use(helmet());
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 1000, // generous limit to avoid blocking provider webhooks
});
app.use(limiter);

/* ===== Database ===== */
const db = new Database('data.sqlite');
db.pragma('journal_mode = WAL');

db.exec(`
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phone TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  credits INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id TEXT UNIQUE NOT NULL,
  user_id INTEGER NOT NULL,
  package_id TEXT NOT NULL,
  credits INTEGER NOT NULL,
  amount INTEGER NOT NULL,
  status TEXT NOT NULL,
  pi_id TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
`);

const packages = [
  { id: "P10",  title: "10 สิทธิ์",   credits: 10,  price: 39 },
  { id: "P30",  title: "30 สิทธิ์",   credits: 30,  price: 99 },
  { id: "P50",  title: "50 สิทธิ์",   credits: 50,  price: 149 },
  { id: "P100", title: "100 สิทธิ์",  credits: 100, price: 279 },
  { id: "P300", title: "300 สิทธิ์",  credits: 300, price: 699 },
];

/* ===== Helpers ===== */
function satang(thb) {
  return Math.round(Number(thb) * 100);
}
function nowIso() {
  return new Date().toISOString();
}
function makeOrderId(userId) {
  return `ORD-${userId}-${Date.now()}`;
}
function signToken(user) {
  return jwt.sign({ uid: user.id, phone: user.phone, name: user.name }, JWT_SECRET, { expiresIn: '7d' });
}
function authMiddleware(req, res, next) {
  const hdr = req.headers['authorization'] || '';
  const token = hdr.startsWith('Bearer ') ? hdr.slice(7) : '';
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = payload;
    next();
  } catch (e) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
function ref1FromOrder(orderId) {
  // limit to 12-16 chars numeric if needed; fall back to base36 slice
  const base = orderId.replace(/[^0-9A-Z]/g, '').slice(-16);
  return base || String(Date.now()).slice(-12);
}

/* ===== SCB Provider Utils ===== */
async function scbAuthToken() {
  if (!SCB_OAUTH_URL || !SCB_CLIENT_ID || !SCB_CLIENT_SECRET) {
    throw new Error('SCB OAuth is not configured');
  }
  const resp = await fetch(SCB_OAUTH_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_id: SCB_CLIENT_ID,
      client_secret: SCB_CLIENT_SECRET,
      grant_type: 'client_credentials',
    }),
  });
  const data = await resp.json();
  if (!resp.ok) {
    throw new Error(data.error_description || data.error || 'SCB OAuth error');
  }
  const token = data.access_token || data.token;
  if (!token) throw new Error('SCB OAuth: no access_token');
  return token;
}
function asDataUrlIfBase64(img) {
  if (!img) return '';
  if (/^data:image/.test(img)) return img;
  // try to detect if already http
  if (/^https?:\/\//.test(img)) return img;
  return `data:image/png;base64,${img}`;
}
async function scbCreateQRCode({ amountSatang, orderId, phone, pkg }) {
  if (!SCB_QR_CREATE_URL || !SCB_MERCHANT_ID || !SCB_TERMINAL_ID) {
    throw new Error('SCB QR create is not configured');
  }
  const token = await scbAuthToken();
  const ref1 = ref1FromOrder(orderId);
  const body = {
    merchantId: SCB_MERCHANT_ID,
    terminalId: SCB_TERMINAL_ID,
    billerId: SCB_BILLER_ID || undefined,
    amount: (amountSatang / 100).toFixed(2),
    currencyCode: '764',
    reference1: ref1,
    reference2: pkg.id,
    reference3: String(pkg.credits),
    description: `Topup ${pkg.title} by ${phone}`,
  };
  const resp = await fetch(SCB_QR_CREATE_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.message || data.error || 'SCB create QR failed');
  }
  const qrImage = asDataUrlIfBase64(data.qrImage || data.qr_image || data.qrCodeImage);
  const scbTxn = data.transactionId || data.qrId || ref1; // fallback to ref1
  return { qrImage, scbTxn, ref1 };
}
async function scbCheckBillPayment({ ref1, ref2, createdAt }) {
  if (!SCB_CHECK_BILLPAY_URL) throw new Error('SCB check bill payment URL not configured');
  const token = await scbAuthToken();
  // Generate date string YYYYMMDD from createdAt
  const d = new Date(createdAt);
  const transDate = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;
  const body = {
    ref1: ref1,
    ref2: ref2 || '',
    transDate: transDate,
  };
  const resp = await fetch(SCB_CHECK_BILLPAY_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.message || data.error || 'SCB check bill payment failed');
  }
  // Expect data.transactions array
  const txns = data.transactions || data.result || [];
  return Array.isArray(txns) ? txns : [];
}

/* ===== Auth ===== */
app.post('/api/signup', async (req, res) => {
  try {
    const { name, phone, password } = req.body || {};
    if (!name || !phone || !password) return res.status(400).json({ error: 'Missing fields' });

    const nameTrim = String(name).trim();
    const rawPhone = String(phone);
    const phoneDigits = rawPhone.replace(/\\D/g, '').trim();
    const passTrim = String(password);

    if (nameTrim.length < 1 || nameTrim.length > 100) return res.status(400).json({ error: 'Invalid name length' });
    if (!/^[0-9]{8,15}$/.test(phoneDigits)) return res.status(400).json({ error: 'Invalid phone format' });
    if (passTrim.length < 6 || passTrim.length > 128) return res.status(400).json({ error: 'Invalid password length' });

    const exists = db.prepare('SELECT id FROM users WHERE phone = ?').get(phoneDigits);
    if (exists) return res.status(409).json({ error: 'Phone already registered' });

    const hash = await bcrypt.hash(passTrim, 10);
    const info = db.prepare('INSERT INTO users (phone, name, password_hash, credits) VALUES (?, ?, ?, ?)').run(phoneDigits, nameTrim, hash, 0);
    const user = { id: info.lastInsertRowid, phone: phoneDigits, name: nameTrim, credits: 0 };
    return res.json({ token: signToken(user) });
  } catch (e) {
    return res.status(500).json({ error: 'Signup failed' });
  }
});
    const ok = await bcrypt.compare(passTrim, user.password_hash);
    if (!ok) return res.status(401).json({ error: 'Invalid credentials' });
    return res.json({ token: signToken(user) });
  } catch {
    return res.status(500).json({ error: 'Login failed' });
  }
});

app.get('/api/me', authMiddleware, (req, res) => {
  const user = db.prepare('SELECT name, phone, credits FROM users WHERE id = ?').get(req.user.uid);
  if (!user) return res.status(404).json({ error: 'Not found' });
  return res.json(user);
});

/* ===== Credits ===== */
app.post('/api/credits/consume', authMiddleware, (req, res) => {
  const user = db.prepare('SELECT id, credits FROM users WHERE id = ?').get(req.user.uid);
  if (!user) return res.status(404).json({ error: 'User not found' });
  if ((user.credits || 0) < 1) return res.status(402).json({ error: 'Insufficient credits' });
  db.prepare('UPDATE users SET credits = credits - 1 WHERE id = ?').run(user.id);
  return res.json({ ok: true });
});

/* ===== Packages ===== */
app.get('/api/packages', (req, res) => {
  res.json(packages);
});

/* ===== Topup / Orders ===== */
app.post('/api/topup/create-order', authMiddleware, async (req, res) => {
  try {
    const { packageId } = req.body || {};
    const pkg = packages.find(p => p.id === packageId);
    if (!pkg) return res.status(400).json({ error: 'Invalid package' });
    const amountSatang = satang(pkg.price);
    const orderId = makeOrderId(req.user.uid);

    if (PAY_PROVIDER === 'stripe') {
      if (!stripe) return res.status(500).json({ error: 'Stripe not configured' });

      // Create PaymentIntent for PromptPay
      const intent = await stripe.paymentIntents.create({
        amount: amountSatang,
        currency: 'thb',
        payment_method_types: ['promptpay'],
        description: `Topup ${pkg.title} by ${req.user.phone}`
      });

      // Confirm intent to get next_action with PromptPay QR code
      const confirmed = await stripe.paymentIntents.confirm(intent.id, {
        payment_method_data: { type: 'promptpay' }
      });

      const qrImage =
        confirmed?.next_action?.promptpay_display_qr_code?.image_url || '';

      db.prepare(`
        INSERT INTO orders (order_id, user_id, package_id, credits, amount, status, pi_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `).run(orderId, req.user.uid, pkg.id, pkg.credits, amountSatang, 'pending', intent.id, nowIso());

      return res.json({ orderId, qrImage });
    } else if (PAY_PROVIDER === 'scb') {
      const { qrImage, scbTxn, ref1 } = await scbCreateQRCode({
        amountSatang,
        orderId,
        phone: req.user.phone,
        pkg
      });

      db.prepare(`
        INSERT INTO orders (order_id, user_id, package_id, credits, amount, status, pi_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `).run(orderId, req.user.uid, pkg.id, pkg.credits, amountSatang, 'pending', ref1, nowIso());

      return res.json({ orderId, qrImage });
    } else {
      return res.status(400).json({ error: 'Unsupported payment provider' });
    }
  } catch (e) {
    console.error('create-order error:', e);
    return res.status(500).json({ error: 'Failed to create order' });
  }
});

app.get('/api/orders/:orderId', authMiddleware, async (req, res) => {
  try {
    const { orderId } = req.params;
    const order = db.prepare('SELECT * FROM orders WHERE order_id = ? AND user_id = ?').get(orderId, req.user.uid);
    if (!order) return res.status(404).json({ error: 'Order not found' });

    if (order.status === 'pending' && order.pi_id) {
      if (PAY_PROVIDER === 'stripe') {
        try {
          const intent = await stripe.paymentIntents.retrieve(order.pi_id);
          if (intent && intent.status) {
            if (intent.status === 'succeeded') {
              db.prepare('UPDATE orders SET status = ? WHERE order_id = ?').run('paid', orderId);
              db.prepare('UPDATE users SET credits = credits + ? WHERE id = ?').run(order.credits, order.user_id);
              order.status = 'paid';
            } else if (intent.status === 'canceled' || intent.status === 'requires_payment_method') {
              db.prepare('UPDATE orders SET status = ? WHERE order_id = ?').run('failed', orderId);
              order.status = 'failed';
            }
          }
        } catch (e) {
          console.warn('refresh intent failed:', e.message || e);
        }
      } else if (PAY_PROVIDER === 'scb') {
        try {
          const txns = await scbCheckBillPayment({ ref1: order.pi_id, ref2: order.package_id, createdAt: order.created_at });
          const paid = Array.isArray(txns) && txns.length > 0;
          if (paid) {
            db.prepare('UPDATE orders SET status = ? WHERE order_id = ?').run('paid', orderId);
            db.prepare('UPDATE users SET credits = credits + ? WHERE id = ?').run(order.credits, order.user_id);
            order.status = 'paid';
          }
        } catch (e) {
          console.warn('scb check failed:', e.message || e);
        }
      }
    }

    return res.json({ status: order.status });
  } catch {
    return res.status(500).json({ error: 'Failed to get order status' });
  }
});

/* ===== Webhooks ===== */

// Stripe webhook
app.post('/api/webhooks/stripe', (req, res) => {
  if (PAY_PROVIDER !== 'stripe') return res.status(200).json({ ok: true });
  const sig = req.headers['stripe-signature'];
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.rawBody, sig, STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    console.error('Stripe webhook signature verification failed:', err.message || err);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  try {
    if (event.type === 'payment_intent.succeeded') {
      const intent = event.data.object;
      const piId = intent.id;
      const order = db.prepare('SELECT * FROM orders WHERE pi_id = ?').get(piId);
      if (order && order.status !== 'paid') {
        db.prepare('UPDATE orders SET status = ? WHERE id = ?').run('paid', order.id);
        db.prepare('UPDATE users SET credits = credits + ? WHERE id = ?').run(order.credits, order.user_id);
      }
    } else if (event.type === 'payment_intent.payment_failed') {
      const intent = event.data.object;
      const piId = intent.id;
      const order = db.prepare('SELECT * FROM orders WHERE pi_id = ?').get(piId);
      if (order && order.status !== 'failed') {
        db.prepare('UPDATE orders SET status = ? WHERE id = ?').run('failed', order.id);
      }
    }
  } catch (e) {
    console.error('Stripe webhook processing failed:', e);
  }
  res.status(200).json({ ok: true });
});

// SCB webhook (generic secret or HMAC header)
app.post('/api/webhooks/scb', (req, res) => {
  if (PAY_PROVIDER !== 'scb') return res.status(200).json({ ok: true });
  // Verify by query secret or header; exact method depends on SCB setup
  const qSecret = (req.query || {}).secret;
  const hdrSecret = req.headers['x-scb-webhook-secret'];
  if (!(qSecret === SCB_WEBHOOK_SECRET || hdrSecret === SCB_WEBHOOK_SECRET)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  try {
    const payload = req.body || {};
    // Expect fields like { ref1, ref2, status } or similar
    const ref1 = payload.ref1 || payload.reference1 || payload.orderRef || '';
    const status = payload.status || payload.paymentStatus || '';
    if (ref1) {
      const order = db.prepare('SELECT * FROM orders WHERE pi_id = ?').get(ref1);
      if (order) {
        if (/success|paid|succeeded/i.test(status)) {
          db.prepare('UPDATE orders SET status = ? WHERE id = ?').run('paid', order.id);
          db.prepare('UPDATE users SET credits = credits + ? WHERE id = ?').run(order.credits, order.user_id);
        } else if (/fail|rejected|canceled/i.test(status)) {
          db.prepare('UPDATE orders SET status = ? WHERE id = ?').run('failed', order.id);
        }
      }
    }
  } catch (e) {
    console.error('SCB webhook processing failed:', e);
  }
  res.status(200).json({ ok: true });
});

/* ===== Health ===== */
app.get('/health', (req, res) => {
  res.json({ ok: true, provider: PAY_PROVIDER });
});

/* ===== Start ===== */
app.listen(PORT, () => {
  console.log(`Backend listening on http://localhost:${PORT} (provider=${PAY_PROVIDER})`);
});
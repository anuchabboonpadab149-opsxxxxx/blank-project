/**
 * อ.โทนี่สะท้อนกรรม — Backend API (Express + SQLite + Stripe PromptPay)
 */
const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const Database = require('better-sqlite3');
const Stripe = require('stripe');

dotenv.config();

const PORT = process.env.PORT || 3000;
const CORS_ORIGIN = process.env.CORS_ORIGIN || '*';
const JWT_SECRET = process.env.JWT_SECRET || 'change_this_jwt_secret';
const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY || '';
const STRIPE_WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET || '';

const stripe = new Stripe(STRIPE_SECRET_KEY);

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

/* ===== Auth ===== */
app.post('/api/signup', async (req, res) => {
  try {
    const { name, phone, password } = req.body || {};
    if (!name || !phone || !password) return res.status(400).json({ error: 'Missing fields' });
    const exists = db.prepare('SELECT id FROM users WHERE phone = ?').get(phone);
    if (exists) return res.status(409).json({ error: 'Phone already registered' });
    const hash = await bcrypt.hash(password, 10);
    const info = db.prepare('INSERT INTO users (phone, name, password_hash, credits) VALUES (?, ?, ?, ?)').run(phone, name, hash, 0);
    const user = { id: info.lastInsertRowid, phone, name, credits: 0 };
    return res.json({ token: signToken(user) });
  } catch (e) {
    return res.status(500).json({ error: 'Signup failed' });
  }
});

app.post('/api/login', async (req, res) => {
  try {
    const { phone, password } = req.body || {};
    if (!phone || !password) return res.status(400).json({ error: 'Missing fields' });
    const user = db.prepare('SELECT * FROM users WHERE phone = ?').get(phone);
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });
    const ok = await bcrypt.compare(password, user.password_hash);
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

/* ===== Topup / Orders (Stripe PromptPay) ===== */
app.post('/api/topup/create-order', authMiddleware, async (req, res) => {
  try {
    const { packageId } = req.body || {};
    const pkg = packages.find(p => p.id === packageId);
    if (!pkg) return res.status(400).json({ error: 'Invalid package' });
    const amountSatang = satang(pkg.price);

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

    const orderId = makeOrderId(req.user.uid);

    const qrImage =
      confirmed?.next_action?.promptpay_display_qr_code?.image_url || '';

    db.prepare(`
      INSERT INTO orders (order_id, user_id, package_id, credits, amount, status, pi_id, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).run(orderId, req.user.uid, pkg.id, pkg.credits, amountSatang, 'pending', intent.id, nowIso());

    return res.json({ orderId, qrImage });
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

    // If pending, refresh status from Stripe
    if (order.status === 'pending' && order.pi_id) {
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
          } // processing/requires_action remain pending
        }
      } catch (e) {
        console.warn('refresh intent failed:', e.message || e);
      }
    }

    return res.json({ status: order.status });
  } catch {
    return res.status(500).json({ error: 'Failed to get order status' });
  }
});

/* ===== Webhooks (Stripe) ===== */
app.post('/api/webhooks/stripe', (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.rawBody, sig, STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message || err);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  try {
    // Handle PaymentIntent events
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
    console.error('webhook processing failed:', e);
  }
  res.status(200).json({ ok: true });
});

/* ===== Health ===== */
app.get('/health', (req, res) => {
  res.json({ ok: true });
});

/* ===== Start ===== */
app.listen(PORT, () => {
  console.log(`Backend listening on http://localhost:${PORT}`);
});
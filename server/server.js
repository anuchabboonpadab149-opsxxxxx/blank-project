/**
 * อ.โทนี่สะท้อนกรรม — Backend API (Express + SQLite + Omise PromptPay)
 */
const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const Database = require('better-sqlite3');
const Omise = require('omise');

dotenv.config();

const PORT = process.env.PORT || 3000;
const CORS_ORIGIN = process.env.CORS_ORIGIN || '*';
const JWT_SECRET = process.env.JWT_SECRET || 'change_this_jwt_secret';
const PROMPTPAY_PHONE = process.env.PROMPTPAY_PHONE || '0916974995';
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'change_this_webhook_secret';
const OMISE_PUBLIC_KEY = process.env.OMISE_PUBLIC_KEY || '';
const OMISE_SECRET_KEY = process.env.OMISE_SECRET_KEY || '';

const omise = new Omise({
  publicKey: OMISE_PUBLIC_KEY,
  secretKey: OMISE_SECRET_KEY,
});

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
  charge_id TEXT,
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
function verifyWebhookSignature(req) {
  const headerSig = req.headers['omise-signature'] || req.headers['x-omise-signature'];
  if (headerSig) {
    const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET);
    hmac.update(req.rawBody || '');
    const digest = hmac.digest('hex');
    try {
      return crypto.timingSafeEqual(Buffer.from(digest, 'hex'), Buffer.from(headerSig, 'hex'));
    } catch {
      return false;
    }
  }
  const q = (req.query || {}).secret;
  const h = req.headers['x-webhook-secret'];
  return (q && q === WEBHOOK_SECRET) || (h && h === WEBHOOK_SECRET);
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

/* ===== Topup / Orders ===== */
app.post('/api/topup/create-order', authMiddleware, async (req, res) => {
  try {
    const { packageId } = req.body || {};
    const pkg = packages.find(p => p.id === packageId);
    if (!pkg) return res.status(400).json({ error: 'Invalid package' });
    const amountSatang = satang(pkg.price);

    // Create source for PromptPay
    const source = await omise.sources.create({
      type: 'promptpay',
      amount: amountSatang,
      currency: 'thb',
      flow: 'offline'
    });

    // Create charge
    const charge = await omise.charges.create({
      amount: amountSatang,
      currency: 'thb',
      source: source.id,
      description: `Topup ${pkg.title} by ${req.user.phone}`
    });

    const orderId = makeOrderId(req.user.uid);
    const qrImage =
      (charge && charge.source && charge.source.scannable_code && charge.source.scannable_code.image && charge.source.scannable_code.image.download_uri)
      || (source && source.scannable_code && source.scannable_code.image && source.scannable_code.image.download_uri)
      || '';

    db.prepare(`
      INSERT INTO orders (order_id, user_id, package_id, credits, amount, status, charge_id, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).run(orderId, req.user.uid, pkg.id, pkg.credits, amountSatang, 'pending', charge.id, nowIso());

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

    // If pending, refresh status from Omise
    if (order.status === 'pending' && order.charge_id) {
      try {
        const charge = await omise.charges.retrieve(order.charge_id);
        if (charge && charge.status) {
          if (charge.status === 'successful') {
            db.prepare('UPDATE orders SET status = ? WHERE order_id = ?').run('paid', orderId);
            db.prepare('UPDATE users SET credits = credits + ? WHERE id = ?').run(order.credits, order.user_id);
            order.status = 'paid';
          } else if (charge.status === 'failed') {
            db.prepare('UPDATE orders SET status = ? WHERE order_id = ?').run('failed', orderId);
            order.status = 'failed';
          }
        }
      } catch (e) {
        console.warn('refresh charge failed:', e.message || e);
      }
    }

    return res.json({ status: order.status });
  } catch {
    return res.status(500).json({ error: 'Failed to get order status' });
  }
});

/* ===== Webhooks (Omise) ===== */
app.post('/api/webhooks/omise', (req, res) => {
  // Verify signature/secret
  const valid = verifyWebhookSignature(req);
  if (!valid) return res.status(401).json({ error: 'Invalid signature' });

  const event = req.body || {};
  try {
    if (event.key === 'charge.complete') {
      const charge = event.data;
      const chargeId = charge && charge.id;
      const status = charge && charge.status;

      if (chargeId) {
        const order = db.prepare('SELECT * FROM orders WHERE charge_id = ?').get(chargeId);
        if (order) {
          if (status === 'successful') {
            db.prepare('UPDATE orders SET status = ? WHERE id = ?').run('paid', order.id);
            db.prepare('UPDATE users SET credits = credits + ? WHERE id = ?').run(order.credits, order.user_id);
          } else if (status === 'failed') {
            db.prepare('UPDATE orders SET status = ? WHERE id = ?').run('failed', order.id);
          }
        }
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
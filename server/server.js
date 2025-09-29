/**
 * Tarot App Backend — PromptPay via Omise (real flow)
 * - User signup/login with token
 * - Credit management (1 credit per reading)
 * - Create PromptPay QR via Omise charges with source[type]=promptpay
 * - Webhook to auto-verify payment and credit user
 *
 * Requirements:
 *  - Set OMISE_SECRET_KEY and OMISE_PUBLIC_KEY in environment
 *  - Configure Omise Webhook to POST to /api/webhooks/omise with a secret
 *    - Set WEBHOOK_SECRET to the same secret value
 *
 * Note: Funds settle to your Omise merchant account. Auto-verification
 *       is provided via Omise webhook events. Paying to a raw PromptPay
 *       phone number cannot be auto-verified without a bank/PSP API.
 */

const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const crypto = require('crypto');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();

dotenv.config();

const OMISE_SECRET_KEY = process.env.OMISE_SECRET_KEY || '';
const OMISE_PUBLIC_KEY = process.env.OMISE_PUBLIC_KEY || '';
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || '';
const PORT = process.env.PORT || 3000;

let omise = null;
if (OMISE_SECRET_KEY) {
  try {
    omise = require('omise')({
      secretKey: OMISE_SECRET_KEY,
      publicKey: OMISE_PUBLIC_KEY,
    });
  } catch (e) {
    console.error('Failed to init Omise SDK:', e.message);
  }
}

const app = express();
app.use(cors());
app.use(express.json());

// SQLite database setup
const dbFile = path.join(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbFile);

db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      phone TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      password_hash TEXT NOT NULL,
      credits INTEGER NOT NULL DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  db.run(`
    CREATE TABLE IF NOT EXISTS sessions (
      token TEXT PRIMARY KEY,
      user_phone TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  db.run(`
    CREATE TABLE IF NOT EXISTS orders (
      id TEXT PRIMARY KEY,
      user_phone TEXT NOT NULL,
      package_id TEXT NOT NULL,
      amount INTEGER NOT NULL,
      credits INTEGER NOT NULL,
      status TEXT NOT NULL, -- 'pending' | 'paid' | 'failed' | 'expired'
      charge_id TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
});

// Packages (must match frontend)
const PACKAGES = [
  { id: 'P10', title: '10 สิทธิ์', credits: 10, price: 39 },
  { id: 'P30', title: '30 สิทธิ์', credits: 30, price: 99 },
  { id: 'P50', title: '50 สิทธิ์', credits: 50, price: 149 },
  { id: 'P100', title: '100 สิทธิ์', credits: 100, price: 279 },
  { id: 'P300', title: '300 สิทธิ์', credits: 300, price: 699 },
];

// Helpers
function hashPassword(password) {
  return crypto.createHash('sha256').update(password).digest('hex');
}
function makeToken() {
  return crypto.randomBytes(24).toString('hex');
}
function now() {
  return new Date().toISOString();
}

// Auth middleware
function auth(req, res, next) {
  const hdr = req.headers.authorization || '';
  const token = hdr.startsWith('Bearer ') ? hdr.slice(7) : '';
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  db.get('SELECT user_phone FROM sessions WHERE token = ?', [token], (err, session) => {
    if (err) return res.status(500).json({ error: 'DB error' });
    if (!session) return res.status(401).json({ error: 'Invalid token' });
    db.get('SELECT phone, name, credits FROM users WHERE phone = ?', [session.user_phone], (e2, user) => {
      if (e2) return res.status(500).json({ error: 'DB error' });
      if (!user) return res.status(401).json({ error: 'User not found' });
      req.user = user;
      req.token = token;
      next();
    });
  });
}

// Routes
app.get('/api/packages', (req, res) => {
  res.json(PACKAGES);
});

app.post('/api/signup', (req, res) => {
  const { name, phone, password } = req.body || {};
  if (!name || !phone || !password) return res.status(400).json({ error: 'Missing fields' });
  const pw = hashPassword(password);
  db.run('INSERT INTO users (phone, name, password_hash, credits) VALUES (?, ?, ?, ?)',
    [phone, name, pw, 0],
    function(err) {
      if (err) {
        if (err.message.includes('UNIQUE')) {
          return res.status(409).json({ error: 'Phone already registered' });
        }
        return res.status(500).json({ error: 'DB error' });
      }
      const token = makeToken();
      db.run('INSERT INTO sessions (token, user_phone) VALUES (?, ?)', [token, phone], (e2) => {
        if (e2) return res.status(500).json({ error: 'DB error' });
        res.json({ token });
      });
    }
  );
});

app.post('/api/login', (req, res) => {
  const { phone, password } = req.body || {};
  if (!phone || !password) return res.status(400).json({ error: 'Missing fields' });
  db.get('SELECT phone, password_hash FROM users WHERE phone = ?', [phone], (err, user) => {
    if (err) return res.status(500).json({ error: 'DB error' });
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });
    if (user.password_hash !== hashPassword(password)) return res.status(401).json({ error: 'Invalid credentials' });
    const token = makeToken();
    db.run('INSERT INTO sessions (token, user_phone) VALUES (?, ?)', [token, phone], (e2) => {
      if (e2) return res.status(500).json({ error: 'DB error' });
      res.json({ token });
    });
  });
});

app.get('/api/me', auth, (req, res) => {
  res.json({ phone: req.user.phone, name: req.user.name, credits: req.user.credits });
});

app.post('/api/credits/consume', auth, (req, res) => {
  const phone = req.user.phone;
  db.get('SELECT credits FROM users WHERE phone = ?', [phone], (err, row) => {
    if (err) return res.status(500).json({ error: 'DB error' });
    const credits = row ? row.credits : 0;
    if (credits < 1) return res.status(400).json({ error: 'Not enough credits' });
    db.run('UPDATE users SET credits = credits - 1, updated_at = ? WHERE phone = ?', [now(), phone], (e2) => {
      if (e2) return res.status(500).json({ error: 'DB error' });
      db.get('SELECT credits FROM users WHERE phone = ?', [phone], (e3, r2) => {
        if (e3) return res.status(500).json({ error: 'DB error' });
        res.json({ credits: r2.credits });
      });
    });
  });
});

app.post('/api/topup/create-order', auth, async (req, res) => {
  const { packageId } = req.body || {};
  const pkg = PACKAGES.find(p => p.id === packageId);
  if (!pkg) return res.status(400).json({ error: 'Invalid package' });
  if (!omise) return res.status(500).json({ error: 'Payment provider not configured' });

  const orderId = `ORD-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  const amountSatang = pkg.price * 100;

  // Create charge with PromptPay source
  try {
    const charge = await omise.charges.create({
      amount: amountSatang,
      currency: 'thb',
      source: { type: 'promptpay' },
      description: `Tarot credits ${pkg.title} for ${req.user.phone}`,
      metadata: {
        order_id: orderId,
        phone: req.user.phone,
        package_id: pkg.id,
        credits: pkg.credits
      }
    });

    const qrImage = charge && charge.source && charge.source.scannable_code && charge.source.scannable_code.image;
    const chargeId = charge && charge.id;

    db.run(
      'INSERT INTO orders (id, user_phone, package_id, amount, credits, status, charge_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [orderId, req.user.phone, pkg.id, pkg.price, pkg.credits, 'pending', chargeId, now(), now()],
      (err) => {
        if (err) return res.status(500).json({ error: 'DB error' });
        res.json({ orderId, amount: pkg.price, credits: pkg.credits, qrImage, chargeId });
      }
    );
  } catch (e) {
    res.status(500).json({ error: 'Payment error', detail: e.message });
  }
});

app.get('/api/orders/:orderId', auth, (req, res) => {
  const orderId = req.params.orderId;
  db.get('SELECT id, status, amount, credits, charge_id FROM orders WHERE id = ? AND user_phone = ?', [orderId, req.user.phone], (err, row) => {
    if (err) return res.status(500).json({ error: 'DB error' });
    if (!row) return res.status(404).json({ error: 'Order not found' });
    res.json(row);
  });
});

// Omise Webhook
app.post('/api/webhooks/omise', (req, res) => {
  // Validate signature if WEBHOOK_SECRET is set
  if (WEBHOOK_SECRET) {
    const signature = req.headers['omise-signature'] || '';
    const body = JSON.stringify(req.body);
    const expected = crypto.createHmac('sha256', WEBHOOK_SECRET).update(body).digest('hex');
    if (signature !== expected) {
      return res.status(400).send('Invalid signature');
    }
  }

  const event = req.body || {};
  // We expect charge.complete events when a PromptPay charge is paid
  if (event.key === 'charge.complete') {
    const charge = event.data && event.data.object;
    const chargeId = charge && charge.id;
    const paid = charge && charge.paid;
    const status = charge && charge.status; // 'successful' or 'failed'

    if (paid && status === 'successful') {
      // Find order by charge_id
      db.get('SELECT id, user_phone, credits, status FROM orders WHERE charge_id = ?', [chargeId], (err, order) => {
        if (err) {
          console.error('DB error on webhook:', err.message);
          return res.status(500).send('DB error');
        }
        if (!order) {
          // Not our order
          return res.status(200).send('No matching order');
        }
        if (order.status === 'paid') {
          return res.status(200).send('Already processed');
        }
        // Mark order as paid and add credits
        db.run('UPDATE orders SET status = ?, updated_at = ? WHERE id = ?', ['paid', now(), order.id], (e2) => {
          if (e2) {
            console.error('DB error updating order:', e2.message);
            return res.status(500).send('DB error');
          }
          db.run('UPDATE users SET credits = credits + ?, updated_at = ? WHERE phone = ?', [order.credits, now(), order.user_phone], (e3) => {
            if (e3) {
              console.error('DB error updating credits:', e3.message);
              return res.status(500).send('DB error');
            }
            return res.status(200).send('OK');
          });
        });
      });
    } else if (status === 'failed') {
      // Mark order failed
      db.run('UPDATE orders SET status = ?, updated_at = ? WHERE charge_id = ?', ['failed', now(), chargeId], (err) => {
        if (err) console.error('DB error marking failed:', err.message);
        return res.status(200).send('OK');
      });
    } else {
      // Not paid yet
      return res.status(200).send('OK');
    }
  } else {
    // Ignore other events
    return res.status(200).send('Ignored');
  }
});

// Simple health
app.get('/api/health', (req, res) => {
  res.json({ ok: true, providerConfigured: !!omise });
});

app.listen(PORT, () => {
  console.log(`Tarot backend listening on http://localhost:${PORT}`);
  if (!omise) {
    console.warn('Omise not configured. Set OMISE_SECRET_KEY/OMISE_PUBLIC_KEY to enable payments.');
  }
});
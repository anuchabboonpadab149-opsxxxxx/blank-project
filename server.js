/**
 * Minimal agent-based top-up system (no payments)
 * - Static form at / (public/index.html)
 * - Create orders via POST /api/orders
 * - View order status at /order/:id
 * - Agent dashboard at /agent (assign/fulfill)
 * - Fulfill endpoints to mark success/failed
 *
 * Note: This is an MVP using in-memory storage. Restarting the server clears data.
 */

const express = require('express');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// In-memory DB
const db = {
  orders: [], // {id, bigoId, diamonds, note, status, agentId, createdAt, updatedAt}
  users: [
    // Minimal seed for agents (no auth; just placeholder)
    { id: 1, role: 'agent', name: 'Agent 1' },
    { id: 2, role: 'agent', name: 'Agent 2' }
  ]
};
let idSeq = 1;

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Health
app.get('/health', (req, res) => res.json({ ok: true }));

// Create order (no payment flow)
app.post('/api/orders', (req, res) => {
  const { bigoId, diamonds, note } = req.body || {};
  const bigoStr = String(bigoId || '').trim();
  const diamondsNum = Number(diamonds);

  if (!/^[0-9]{5,15}$/.test(bigoStr)) {
    return res.status(400).json({ error: 'invalid_bigo_id', message: 'Bigo ID must be 5–15 digits' });
  }
  if (!Number.isInteger(diamondsNum) || diamondsNum < 1 || diamondsNum > 200000) {
    return res.status(400).json({ error: 'invalid_diamonds', message: 'Diamonds must be 1–200,000' });
  }

  const now = new Date().toISOString();
  const order = {
    id: idSeq++,
    bigoId: bigoStr,
    diamonds: diamondsNum,
    note: (note || '').toString().slice(0, 200),
    status: 'QUEUED', // QUEUED -> FULFILLING -> SUCCESS/FAILED
    agentId: null,
    createdAt: now,
    updatedAt: now
  };
  db.orders.push(order);
  return res.json({ id: order.id, status: order.status });
});

// Get raw order JSON
app.get('/api/orders/:id', (req, res) => {
  const order = db.orders.find(o => o.id === Number(req.params.id));
  if (!order) return res.status(404).json({ error: 'not_found' });
  res.json(order);
});

// Simple status page
app.get('/order/:id', (req, res) => {
  const order = db.orders.find(o => o.id === Number(req.params.id));
  if (!order) return res.status(404).send('Order not found');
  res.send(`
    <!doctype html>
    <html lang="th">
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
      <title>สถานะคำสั่งเติม #${order.id}</title>
      <style>
        body{font-family:system-ui,sans-serif;margin:24px;}
        .card{max-width:560px;margin:auto;border:1px solid #ddd;border-radius:12px;padding:18px;}
        .status{font-weight:700}
        .ok{color:#0b7a0b}
        .fail{color:#b00020}
        .muted{color:#666;font-size:12px}
        a.btn{display:inline-block;margin-top:12px;padding:10px 12px;background:#4a90e2;color:#fff;border-radius:8px;text-decoration:none}
      </style>
    </head>
    <body>
      <div class="card">
        <h2>สถานะคำสั่งเติม #${order.id}</h2>
        <p>Bigo ID: <strong>${order.bigoId}</strong></p>
        <p>จำนวนเพชร: <strong>${order.diamonds}</strong></p>
        <p class="status">สถานะ: ${
          order.status === 'SUCCESS' ? '<span class="ok">สำเร็จ</span>'
            : order.status === 'FAILED' ? '<span class="fail">ล้มเหลว</span>'
            : order.status === 'FULFILLING' ? 'กำลังดำเนินการ'
            : 'เข้าคิว'
        }</p>
        <p class="muted">อัปเดตล่าสุด: ${order.updatedAt}</p>
        <a class="btn" href="/">สร้างคำสั่งเติมใหม่</a>
      </div>
    </body>
    </html>
  `);
});

// Agent dashboard (no auth; for demo)
app.get('/agent', (req, res) => {
  // Group orders by status
  const queued = db.orders.filter(o => o.status === 'QUEUED');
  const fulfilling = db.orders.filter(o => o.status === 'FULFILLING');
  const done = db.orders.filter(o => o.status === 'SUCCESS' || o.status === 'FAILED');

  function renderOrderRow(o) {
    const action = o.status === 'QUEUED'
      ? `<form method="post" action="/api/orders/${o.id}/assign" style="display:inline">
           <button>รับงาน</button>
         </form>`
      : o.status === 'FULFILLING'
        ? `<form method="post" action="/api/orders/${o.id}/fulfill" style="display:inline;margin-right:6px">
             <input type="hidden" name="result" value="success">
             <button style="background:#0b7a0b;color:#fff;border:0;padding:6px 10px;border-radius:6px">สำเร็จ</button>
           </form>
           <form method="post" action="/api/orders/${o.id}/fulfill" style="display:inline">
             <input type="hidden" name="result" value="failed">
             <button style="background:#b00020;color:#fff;border:0;padding:6px 10px;border-radius:6px">ล้มเหลว</button>
           </form>`
        : '';
    return `
      <tr>
        <td>#${o.id}</td>
        <td>${o.bigoId}</td>
        <td>${o.diamonds}</td>
        <td>${o.status}</td>
        <td>${o.agentId ? 'Agent ' + o.agentId : '-'}</td>
        <td>
          <a href="https://www.bigo.tv/" target="_blank">เปิด bigo.tv</a>
          ${action}
          <a href="/order/${o.id}">สถานะ</a>
        </td>
      </tr>
    `;
  }

  res.send(`
    <!doctype html>
    <html lang="th">
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
      <title>แดชบอร์ดตัวแทน</title>
      <style>
        body{font-family:system-ui,sans-serif;margin:24px;}
        h2{margin-top:24px}
        table{width:100%;border-collapse:collapse;margin-top:12px}
        th,td{border:1px solid #ddd;padding:8px;text-align:left}
        th{background:#f5f5f5}
        .muted{color:#666;font-size:12px}
        a.btn{display:inline-block;margin-top:12px;padding:10px 12px;background:#4a90e2;color:#fff;border-radius:8px;text-decoration:none}
      </style>
    </head>
    <body>
      <h1>แดชบอร์ดตัวแทน (เดโม่ - ไม่มีระบบล็อกอิน)</h1>
      <p class="muted">ขั้นตอน: รับงาน → เปิด bigo.tv เติมจริง → กดสำเร็จ/ล้มเหลว</p>

      <h2>คิวใหม่ (QUEUED)</h2>
      <table>
        <tr><th>Order</th><th>Bigo ID</th><th>Diamonds</th><th>Status</th><th>Agent</th><th>การทำงาน</th></tr>
        ${queued.map(renderOrderRow).join('')}
      </table>

      <h2>กำลังดำเนินการ (FULFILLING)</h2>
      <table>
        <tr><th>Order</th><th>Bigo ID</th><th>Diamonds</th><th>Status</th><th>Agent</th><th>การทำงาน</th></tr>
        ${fulfilling.map(renderOrderRow).join('')}
      </table>

      <h2>เสร็จสิ้น</h2>
      <table>
        <tr><th>Order</th><th>Bigo ID</th><th>Diamonds</th><th>Status</th><th>Agent</th><th>การทำงาน</th></tr>
        ${done.map(renderOrderRow).join('')}
      </table>

      <p><a class="btn" href="/">กลับไปหน้าแบบฟอร์ม</a></p>
    </body>
    </html>
  `);
});

// Assign order to an agent (auto-assign Agent 1 for demo)
app.post('/api/orders/:id/assign', (req, res) => {
  const order = db.orders.find(o => o.id === Number(req.params.id));
  if (!order) return res.status(404).send('Order not found');
  if (order.status !== 'QUEUED') return res.status(400).send('Order not in queue');

  order.agentId = 1;
  order.status = 'FULFILLING';
  order.updatedAt = new Date().toISOString();
  res.redirect('/agent');
});

// Fulfill order result
app.post('/api/orders/:id/fulfill', (req, res) => {
  const order = db.orders.find(o => o.id === Number(req.params.id));
  if (!order) return res.status(404).send('Order not found');
  if (order.status !== 'FULFILLING') return res.status(400).send('Order not fulfilling');

  const result = (req.body.result || req.query.result || '').toString().toLowerCase();
  if (result === 'success') {
    order.status = 'SUCCESS';
  } else if (result === 'failed') {
    order.status = 'FAILED';
  } else {
    return res.status(400).send('Invalid result');
  }
  order.updatedAt = new Date().toISOString();
  res.redirect('/agent');
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running: http://localhost:${PORT}`);
  console.log(`Form: http://localhost:${PORT}/`);
  console.log(`Agent dashboard: http://localhost:${PORT}/agent`);
});
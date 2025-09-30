/* eslint-disable no-console */
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const cookieParser = require('cookie-parser');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');

const app = express();

// Config
const PORT = process.env.PORT ? Number(process.env.PORT) : 8080;
// If ALLOWED_ORIGINS is empty or '*', allow all origins (useful for preview environments)
const rawOrigins = (process.env.ALLOWED_ORIGINS || '').trim();
const allowAllOrigins = rawOrigins === '' || rawOrigins === '*';
const allowedOrigins = allowAllOrigins
  ? []
  : rawOrigins.split(',').map(s => s.trim()).filter(Boolean);

// Middlewares
app.use(morgan('combined'));
app.use(helmet({
  crossOriginResourcePolicy: { policy: 'cross-origin' }
}));
app.use(compression());
app.use(express.json({ limit: '1mb' }));
app.use(cookieParser());

// Rate limiting
const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 300, // 300 req/min/ IP
  standardHeaders: true,
  legacyHeaders: false
});
app.use(limiter);

// CORS
app.use(cors({
  origin(origin, cb) {
    if (allowAllOrigins) return cb(null, true);
    if (!origin || allowedOrigins.includes(origin)) return cb(null, true);
    return cb(new Error('Not allowed by CORS'));
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 86400
}));

// Cache correctness for multiple origins
app.use((req, res, next) => {
  res.setHeader('Vary', 'Origin');
  next();
});

// Handle preflight globally
app.options('*', cors());

// Health endpoints
app.get('/api/health', (req, res) => {
  res.json({
    ok: true,
    service: 'backend',
    time: new Date().toISOString()
  });
});

// Example login - demo only
app.post('/api/login', (req, res) => {
  const { email } = req.body || {};
  const sid = 'sid_' + Math.random().toString(36).slice(2);
  const isHttps = (req.secure || req.get('x-forwarded-proto') === 'https' || process.env.NODE_ENV === 'production');

  res.cookie('sid', sid, {
    httpOnly: true,
    secure: isHttps,
    sameSite: isHttps ? 'none' : 'lax',
    path: '/'
  });
  res.json({ ok: true, user: { email }, sid });
});

// Example data endpoint
app.get('/api/data', (req, res) => {
  res.json({
    items: [
      { id: 1, name: 'Alpha' },
      { id: 2, name: 'Beta' }
    ]
  });
});

// 404 for unknown API routes
app.use('/api', (req, res) => {
  res.status(404).json({ ok: false, error: 'Not Found' });
});

// Error handler
// Note: keep signature (err, req, res, next)
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err && (err.stack || err));
  if (res.headersSent) return next(err);
  res.status(500).json({ ok: false, error: 'Internal Server Error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`API listening on http://localhost:${PORT}`);
  console.log(
    allowAllOrigins
      ? 'Allowed origins: ALL (preview mode)'
      : `Allowed origins: ${allowedOrigins.join(', ')}`
  );
});
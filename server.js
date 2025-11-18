import express from 'express';
import path from 'path';
import cors from 'cors';
import bodyParser from 'body-parser';
import dotenv from 'dotenv';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import admin from 'firebase-admin';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

dotenv.config();

const app = express();
app.use(cors({ origin: true, credentials: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(process.cwd(), 'public')));

const admin = require("firebase-admin");

// --- Firebase Admin Initialization (Using Render Secret File) ---
try {
  const serviceAccount = require("/etc/secrets/service-account.json");

  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });

  console.log("🔥 Firebase Admin initialized using /etc/secrets/service-account.json");
} catch (err) {
  console.error("❌ Failed to load Firebase service account file:", err.message);
  process.exit(1);
}

// --- SQLite DB ---
let db;
(async () => {
  db = await open({
    filename: process.env.SQLITE_FILE || './tokens.db',
    driver: sqlite3.Database
  });
  await db.exec(`CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userId TEXT,
    token TEXT UNIQUE,
    platform TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
  await db.exec(`CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT,
    payload TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
})();

// --- Auth utils ---
const JWT_SECRET = process.env.ADMIN_JWT_SECRET || 'change_this_secret';
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || 'admin@example.com';
const ADMIN_PASSWORD_HASH = process.env.ADMIN_PASSWORD_HASH || null; // bcrypt hash; if not provided, ADMIN_PASSWORD is used
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'changeme';

// create JWT
function signAdmin(user) {
  return jwt.sign({ sub: user.email, role: 'admin' }, JWT_SECRET, { expiresIn: '8h' });
}

// middleware: verify admin via Authorization: Bearer <token>
function requireAuth(req, res, next) {
  const auth = req.headers['authorization'] || req.headers['x-api-key'];
  if (!auth) return res.status(401).json({ success: false, error: 'Missing auth token' });

  // if x-api-key style (legacy) accept direct match with ADMIN_API_KEY
  if (req.headers['x-api-key'] && process.env.ADMIN_API_KEY && req.headers['x-api-key'] === process.env.ADMIN_API_KEY) {
    return next();
  }

  const parts = auth.split(' ');
  if (parts.length === 2 && parts[0] === 'Bearer') {
    try {
      const payload = jwt.verify(parts[1], JWT_SECRET);
      req.admin = payload;
      return next();
    } catch (e) {
      return res.status(401).json({ success: false, error: 'Invalid or expired token' });
    }
  }

  return res.status(401).json({ success: false, error: 'Invalid auth format' });
}

// --- Routes ---

// Admin login
app.post('/api/admin/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ success: false, error: 'email and password required' });

  if (email !== ADMIN_EMAIL) return res.status(401).json({ success: false, error: 'Invalid credentials' });

  try {
    let ok = false;
    if (ADMIN_PASSWORD_HASH) {
      ok = await bcrypt.compare(password, ADMIN_PASSWORD_HASH);
    } else {
      ok = password === ADMIN_PASSWORD;
    }
    if (!ok) return res.status(401).json({ success: false, error: 'Invalid credentials' });

    const token = signAdmin({ email });
    return res.json({ success: true, token, expiresIn: '8h' });
  } catch (e) {
    return res.status(500).json({ success: false, error: e.message });
  }
});

// Register token
app.post('/register', async (req, res) => {
  const { userId, token, platform } = req.body;
  if (!userId || !token) return res.status(400).json({ success: false, error: 'userId and token required' });
  try {
    await db.run('INSERT OR REPLACE INTO tokens (userId, token, platform) VALUES (?, ?, ?)', [userId, token, platform || null]);
    await db.run('INSERT INTO audit_logs (action, payload) VALUES (?, ?)', ['register', JSON.stringify({ userId, token })]);
    res.json({ success: true, message: 'Token registered' });
  } catch (err) {
    console.error('Register error', err);
    res.status(500).json({ success: false, error: err.message });
  }
});

// Unregister token
app.post('/unregister', async (req, res) => {
  const { token } = req.body;
  if (!token) return res.status(400).json({ success: false, error: 'token required' });
  try {
    await db.run('DELETE FROM tokens WHERE token = ?', [token]);
    await db.run('INSERT INTO audit_logs (action, payload) VALUES (?, ?)', ['unregister', JSON.stringify({ token })]);
    res.json({ success: true, message: 'Token removed' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Send notification (protected)
app.post('/send', requireAuth, async (req, res) => {
  const { userId, token, title, body, data } = req.body;
  if (!title || !body) return res.status(400).json({ success: false, error: 'title and body required' });
  let tokens = [];
  try {
    if (token) tokens = [token];
    else if (userId) {
      const rows = await db.all('SELECT token FROM tokens WHERE userId = ?', [userId]);
      tokens = rows.map(r => r.token);
    } else {
      return res.status(400).json({ success: false, error: 'Provide userId or token' });
    }
    if (!tokens.length) return res.status(404).json({ success: false, error: 'No tokens found for target' });

    const message = { notification: { title, body }, data: data || {} };

    if (!admin.apps.length) {
      return res.status(500).json({ success: false, error: 'FCM not initialized on server' });
    }

    if (tokens.length === 1) {
      const resp = await admin.messaging().sendToDevice(tokens[0], message);
      await db.run('INSERT INTO audit_logs (action, payload) VALUES (?, ?)', ['send', JSON.stringify({ userId, token: tokens[0], resp })]);
      return res.json({ success: true, resp });
    } else {
      const response = await admin.messaging().sendToDevice(tokens, message);
      // handle invalid tokens
      const toRemove = [];
      response.results.forEach((r, idx) => {
        if (r.error) {
          const errMsg = r.error.message || r.error.toString();
          if (errMsg.includes('registration-token-not-registered') || errMsg.includes('invalid-registration-token')) {
            toRemove.push(tokens[idx]);
          }
        }
      });
      if (toRemove.length) {
        const placeholders = toRemove.map(()=>'?').join(',');
        await db.run(`DELETE FROM tokens WHERE token IN (${placeholders})`, toRemove);
      }
      await db.run('INSERT INTO audit_logs (action, payload) VALUES (?, ?)', ['send_bulk', JSON.stringify({ userId, count: tokens.length })]);
      return res.json({ success: true, response });
    }
  } catch (err) {
    console.error('Send error', err);
    res.status(500).json({ success: false, error: err.message });
  }
});

// Broadcast (protected)
app.post('/broadcast', requireAuth, async (req, res) => {
  const { title, body, data } = req.body;
  if (!title || !body) return res.status(400).json({ success: false, error: 'title and body required' });
  try {
    const rows = await db.all('SELECT token FROM tokens');
    const tokens = rows.map(r => r.token);
    if (!tokens.length) return res.status(404).json({ success: false, error: 'No tokens registered' });

    if (!admin.apps.length) {
      return res.status(500).json({ success: false, error: 'FCM not initialized on server' });
    }

    const chunkSize = 500;
    let sent = 0;
    for (let i = 0; i < tokens.length; i += chunkSize) {
      const chunk = tokens.slice(i, i + chunkSize);
      const response = await admin.messaging().sendToDevice(chunk, { notification: { title, body }, data: data || {} });
      sent += chunk.length;
      // cleanup invalid tokens
      const toRemove = [];
      response.results.forEach((r, idx) => {
        if (r.error) {
          const errMsg = r.error.message || r.error.toString();
          if (errMsg.includes('registration-token-not-registered') || errMsg.includes('invalid-registration-token')) {
            toRemove.push(chunk[idx]);
          }
        }
      });
      if (toRemove.length) {
        const placeholders = toRemove.map(()=>'?').join(',');
        await db.run(`DELETE FROM tokens WHERE token IN (${placeholders})`, toRemove);
      }
    }
    await db.run('INSERT INTO audit_logs (action, payload) VALUES (?, ?)', ['broadcast', JSON.stringify({ sent })]);
    res.json({ success: true, sent });
  } catch (err) {
    console.error('Broadcast error', err);
    res.status(500).json({ success: false, error: err.message });
  }
});

// List tokens (protected)
app.get('/tokens', requireAuth, async (req, res) => {
  try {
    const rows = await db.all('SELECT id, userId, token, platform, created_at FROM tokens ORDER BY created_at DESC LIMIT 2000');
    res.json({ success: true, tokens: rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Audit logs (protected)
app.get('/logs', requireAuth, async (req, res) => {
  try {
    const rows = await db.all('SELECT id, action, payload, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 1000');
    res.json({ success: true, logs: rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// health
app.get('/health', (req, res) => res.json({ success: true, time: new Date() }));

// serve index
app.get('/', (req, res) => {
  res.sendFile(path.join(process.cwd(), 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, ()=> console.log(`Professional WebPush backend running on ${PORT}`));

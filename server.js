import express from 'express';
import path from 'path';
import cors from 'cors';
import bodyParser from 'body-parser';
import dotenv from 'dotenv';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import admin from 'firebase-admin';

dotenv.config();

const app = express();
app.use(cors({ origin: '*' }));
app.use(bodyParser.json());
app.use(express.static(path.join(process.cwd(), 'public')));

// Initialize Firebase Admin using SERVICE_ACCOUNT_JSON env var (recommended for Render)
let serviceAccount;
if (process.env.SERVICE_ACCOUNT_JSON) {
  try {
    serviceAccount = JSON.parse(process.env.SERVICE_ACCOUNT_JSON);
    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount)
    });
    console.log('Firebase admin initialized from SERVICE_ACCOUNT_JSON');
  } catch (e) {
    console.error('Failed to parse SERVICE_ACCOUNT_JSON:', e.message);
    process.exit(1);
  }
} else if (process.env.GOOGLE_APPLICATION_CREDENTIALS) {
  admin.initializeApp();
  console.log('Firebase admin initialized using GOOGLE_APPLICATION_CREDENTIALS');
} else {
  console.error('No Firebase credentials found. Set SERVICE_ACCOUNT_JSON or GOOGLE_APPLICATION_CREDENTIALS.');
  process.exit(1);
}

// Open (or create) SQLite DB
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
})();

// Simple auth middleware for protected endpoints (set ADMIN_API_KEY in env)
function requireApiKey(req, res, next) {
  const key = req.headers['x-api-key'] || req.query.api_key;
  if (process.env.ADMIN_API_KEY && key === process.env.ADMIN_API_KEY) return next();
  return res.status(401).json({ success: false, error: 'Unauthorized - missing/invalid API key' });
}

// Register a device token for a user
app.post('/register', async (req, res) => {
  const { userId, token, platform } = req.body;
  if (!userId || !token) return res.status(400).json({ success: false, error: 'userId and token required' });
  try {
    await db.run('INSERT OR REPLACE INTO tokens (userId, token, platform) VALUES (?, ?, ?)', [userId, token, platform || null]);
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
    res.json({ success: true, message: 'Token removed' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Send notification to a single user (by userId) or to a single token
app.post('/send', requireApiKey, async (req, res) => {
  const { userId, token, title, body, data, android, apns } = req.body;
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

    // build message
    const message = {
      notification: { title, body },
      data: data || {},
    };

    // use multicast for multiple tokens
    if (tokens.length === 1) {
      await admin.messaging().sendToDevice(tokens[0], message, { android: android || {}, apns: apns || {} });
      return res.json({ success: true, sent: 1 });
    } else {
      const response = await admin.messaging().sendToDevice(tokens, message, { android: android || {}, apns: apns || {} });
      // response.results can have errors; remove invalid tokens
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
        console.log('Removed invalid tokens:', toRemove);
      }
      return res.json({ success: true, response });
    }
  } catch (err) {
    console.error('Send error', err);
    res.status(500).json({ success: false, error: err.message });
  }
});

// Broadcast to all registered tokens (protected)
app.post('/broadcast', requireApiKey, async (req, res) => {
  const { title, body, data } = req.body;
  if (!title || !body) return res.status(400).json({ success: false, error: 'title and body required' });
  try {
    const rows = await db.all('SELECT token FROM tokens');
    const tokens = rows.map(r => r.token);
    if (!tokens.length) return res.status(404).json({ success: false, error: 'No tokens registered' });

    // chunk tokens by 500 (FCM limit)
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
        console.log('Removed invalid tokens:', toRemove);
      }
    }
    res.json({ success: true, sent });
  } catch (err) {
    console.error('Broadcast error', err);
    res.status(500).json({ success: false, error: err.message });
  }
});

// List tokens (protected)
app.get('/tokens', requireApiKey, async (req, res) => {
  try {
    const rows = await db.all('SELECT id, userId, token, platform, created_at FROM tokens ORDER BY created_at DESC LIMIT 1000');
    res.json({ success: true, tokens: rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Health check
app.get('/health', (req, res) => res.json({ success: true, time: new Date() }));

// Serve simple dashboard for testing (optional)
app.get('/', (req, res) => {
  res.sendFile(path.join(process.cwd(), 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, ()=> console.log(`Advanced WebPush backend running on port ${PORT}`));

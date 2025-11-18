import express from 'express';
import bodyParser from 'body-parser';
import fs from 'fs';
import { GoogleAuth } from 'google-auth-library';
import path from 'path';

const app = express();
app.use(bodyParser.json());
app.use(express.static(path.join(process.cwd(), 'public')));

const SUB_FILE = 'subscribers.json';

// Ensure subscribers file exists
if (!fs.existsSync(SUB_FILE)) fs.writeFileSync(SUB_FILE, '[]', 'utf8');

// Helper to read/write subscribers
function readSubscribers() {
  try {
    return JSON.parse(fs.readFileSync(SUB_FILE, 'utf8') || '[]');
  } catch (e) { return []; }
}
function writeSubscribers(list) {
  fs.writeFileSync(SUB_FILE, JSON.stringify(list, null, 2), 'utf8');
}

// Load service account placeholder (replace with real file)
let serviceAccount = null;
const servicePath = 'service-account.json';
if (fs.existsSync(servicePath)) {
  serviceAccount = JSON.parse(fs.readFileSync(servicePath, 'utf8'));
} else {
  console.warn('[WARN] service-account.json not found. FCM send will fail until you add it.');
}

// Google Auth setup (lazy)
let auth = null;
function getAuth() {
  if (!serviceAccount) throw new Error('service-account.json missing');
  if (!auth) {
    auth = new GoogleAuth({
      credentials: serviceAccount,
      scopes: ['https://www.googleapis.com/auth/firebase.messaging']
    });
  }
  return auth;
}

// Public API: register token (widget will POST here)
app.post('/api/register-token', (req, res) => {
  const { token } = req.body;
  if (!token) return res.status(400).json({ success: false, error: 'token required' });

  const list = readSubscribers();
  const exists = list.find(i => i.token === token);
  if (!exists) {
    const entry = { token, date: new Date().toISOString() };
    list.push(entry);
    writeSubscribers(list);
  }
  res.json({ success: true });
});

// Get subscribers (dashboard)
app.get('/api/subscribers', (req, res) => {
  const list = readSubscribers();
  res.json(list);
});

// Delete subscriber
app.delete('/api/subscribers/:token', (req, res) => {
  const token = req.params.token;
  let list = readSubscribers();
  list = list.filter(i => i.token !== token);
  writeSubscribers(list);
  res.json({ success: true });
});

// Send notification: body { title, body, token? } - if token omitted sends to all
app.post('/api/send', async (req, res) => {
  const { title, body: messageBody, token } = req.body;
  if (!title || !messageBody) return res.status(400).json({ success: false, error: 'title and body required' });

  if (!serviceAccount) return res.status(500).json({ success: false, error: 'service-account.json missing on server' });

  try {
    const client = await getAuth().getClient();
    const projectId = serviceAccount.project_id;
    const url = `https://fcm.googleapis.com/v1/projects/${projectId}/messages:send`;

    const sendOne = async (targetToken) => {
      const message = {
        message: {
          token: targetToken,
          notification: { title, body: messageBody }
        }
      };
      const response = await client.request({ url, method: 'POST', data: message });
      return response.data;
    };

    if (token) {
      const resp = await sendOne(token);
      return res.json({ success: true, results: [resp] });
    } else {
      const list = readSubscribers();
      const results = [];
      for (const entry of list) {
        try {
          const r = await sendOne(entry.token);
          results.push({ token: entry.token, ok: true, resp: r });
        } catch (err) {
          results.push({ token: entry.token, ok: false, error: String(err.message) });
        }
      }
      return res.json({ success: true, results });
    }

  } catch (error) {
    return res.status(500).json({ success: false, error: String(error.message) });
  }
});

// Serve dashboard UI
app.get('/dashboard', (req, res) => {
  res.sendFile(path.join(process.cwd(), 'public', 'dashboard.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

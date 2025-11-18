import express from 'express';
import path from 'path';
import bodyParser from 'body-parser';
import fetch from 'node-fetch';
import dotenv from 'dotenv';
dotenv.config();

const app = express();
app.use(bodyParser.json());
app.use(express.static(path.join(process.cwd(), 'public')));

app.post('/send', async (req, res) => {
  const { title, body, token } = req.body;

  try {
    const response = await fetch('https://fcm.googleapis.com/fcm/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `key=${process.env.FCM_SERVER_KEY}`
      },
      body: JSON.stringify({
        to: token,
        notification: { title, body }
      })
    });

    const data = await response.json();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.listen(3000, () => console.log('Dashboard running on port 3000'));

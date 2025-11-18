// Usage example: include this script in your public website to register token and send to backend
// Make sure to replace firebaseConfig fields and VAPID key.
import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.6.10/firebase-app.js';
import { getMessaging, getToken, onMessage } from 'https://www.gstatic.com/firebasejs/9.6.10/firebase-messaging.js';

const firebaseConfig = {
  apiKey: 'AIzaSyBlarIHSJMrD64TX9wq3TBPAZ_e-a2qEk0',
  authDomain: 'pushii-75128.firebaseapp.com',
  projectId: 'pushii-75128',
  messagingSenderId: '856171295104',
  appId: '1:856171295104:web:799355339f9c1f21a61165'
};

export async function enablePush(userId){
  const app = initializeApp(firebaseConfig);
  const messaging = getMessaging(app);
  try {
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') throw new Error('Permission not granted');

    const token = await getToken(messaging, { vapidKey: 'BC6YV7StPElT8J1JySEyeOfLkW27cfcEmBNHDG7WIteAi2xpN2DZ1Pea9Z0BKTFJYS76KSa6E3k2ASajX3PlJCQ' });
    console.log('FCM Token', token);

    // send to your backend register endpoint
    await fetch('/register', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ userId, token }) });
    return token;
  } catch (e) {
    console.error('Push enable failed', e);
    throw e;
  }
}

export function handleForeground(messaging, onPayload){
  onMessage(messaging, payload => onPayload(payload));
}

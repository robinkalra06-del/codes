/*
  Frontend widget to include on any site.
  Usage: include firebase scripts (compat) and this file.
  Replace firebaseConfig and VAPID key.
*/

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// init firebase (expects firebase-app-compat and firebase-messaging-compat loaded in page)
if (typeof firebase === 'undefined') {
  console.error('Firebase not found. Please include firebase-app-compat and firebase-messaging-compat scripts.');
} else {
  firebase.initializeApp(firebaseConfig);
  const messaging = firebase.messaging();

  async function registerForPush(vapidKey, registerUrl) {
    try {
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') return console.warn('Permission not granted');

      const token = await messaging.getToken({ vapidKey });
      console.log('FCM token', token);

      // send to backend
      await fetch(registerUrl || '/api/register-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      });

      return token;
    } catch (err) {
      console.error('Push registration failed', err);
    }
  }

  // expose helper
  window.webpushRegister = registerForPush;
}

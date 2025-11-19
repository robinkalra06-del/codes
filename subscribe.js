// public/subscribe.js
// Usage: include this file on client site. It will register service worker and send subscription to backend.
(async function () {
  const serverBase = window.__WEBPUSH_SERVER_BASE__ || ''; // Optional override by site owner
  // Put your server's public VAPID key here if not overriding from server.
  const VAPID_PUBLIC_KEY = '7F2hiW6vMAMbcCaWygcBoYYcu0KIA6wVjb1WOo0RZk1cOmU685Q3rMVEaM1MlCWBMgtE-1aTvS63IdeL1xj29Q0'; // replace after deployment

  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.warn('Push not supported');
    return;
  }

  try {
    const reg = await navigator.serviceWorker.register('/sw.js');
    console.log('Service Worker registered', reg);

    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      console.warn('Notification permission not granted');
      return;
    }

    const sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
    });

    // send to server
    const endpoint = (serverBase || '') + '/api/save-subscription.php';
    await fetch(endpoint, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(sub)
    });

    console.log('Subscribed and sent to server');
  } catch (err) {
    console.error('Subscription error:', err);
  }
})();

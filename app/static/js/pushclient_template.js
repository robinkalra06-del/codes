// pushclient_template.js - served per-site with replaced keys
const SITE_KEY = "__SITE_KEY__";
const VAPID_PUBLIC_KEY = "__VAPID_PUBLIC_KEY__";

async function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, "+").replace(/_/g, "/");
    const rawData = atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

async function registerPush() {
    if (!('serviceWorker' in navigator)) return;
    const sw = await navigator.serviceWorker.register('/service-worker.js');
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') return;
    const applicationServerKey = await urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
    const subscription = await sw.pushManager.subscribe({userVisibleOnly:true, applicationServerKey});
    await fetch('/api/subscribe', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({site_key: SITE_KEY, subscription})});
}
registerPush();

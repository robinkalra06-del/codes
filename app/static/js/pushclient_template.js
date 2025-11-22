// Replace __SITE_KEY__ and __VAPID_PUBLIC_KEY__ when serving dynamically
const SITE_KEY = "__SITE_KEY__";
const VAPID_PUBLIC_KEY = "__VAPID_PUBLIC_KEY__";

function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

async function registerPush() {
  if (!("serviceWorker" in navigator)) return;

  try {
    // 1. REGISTER SW (ensure this file exists!)
    const swReg = await navigator.serviceWorker.register("/service-worker.js");

    // 2. ASK PERMISSION
    let permission = Notification.permission;
    if (permission !== "granted") {
      permission = await Notification.requestPermission();
    }
    if (permission !== "granted") return;

    // 3. SUBSCRIBE
    const applicationServerKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
    const subscription = await swReg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey,
    });

    // 4. SEND TO BACKEND
    await fetch("/api/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        site_key: SITE_KEY,
        subscription,
      }),
    });
  } catch (err) {
    console.error("Push registration error:", err);
  }
}

registerPush();

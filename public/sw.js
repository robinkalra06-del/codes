// public/sw.js
self.addEventListener('push', function(event) {
  let data = { title: 'Notification', body: '' };
  try {
    data = event.data.json();
  } catch (e) {
    data.body = event.data ? event.data.text() : '';
  }
  const options = {
    body: data.body || '',
    icon: data.icon || undefined,
    data: { timestamp: data.timestamp || Date.now() }
  };
  event.waitUntil(self.registration.showNotification(data.title, options));
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(clients.openWindow('/'));
});

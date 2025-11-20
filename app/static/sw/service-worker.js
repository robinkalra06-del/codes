self.addEventListener('push', function(event) {
    let data = {};
    try { data = event.data.json(); } catch (e) { data = { title: 'Notification', body: event.data ? event.data.text() : '' }; }
    const title = data.title || 'Notification';
    const options = { body: data.body || '', icon: data.icon || '/static/img/icon-192.png', image: data.image || undefined, data: { url: data.url || '/' } };
    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    const url = event.notification.data && event.notification.data.url ? event.notification.data.url : '/';
    event.waitUntil(clients.matchAll({ type: 'window' }).then(function(clientList) {
        for (let i=0;i<clientList.length;i++){ let c = clientList[i]; if (c.url === url && 'focus' in c) return c.focus(); }
        if (clients.openWindow) return clients.openWindow(url);
    }));
});

self.addEventListener('push', function(event) {
  let data = {};
  if (event.data) {
    try { data = event.data.json(); } catch(e) { data = { title: 'New', body: event.data.text() }; }
  }
  const title = data.title || 'New Notification';
  const options = {
    body: data.body || '',
    icon: data.icon || '/static/default-icon.png',
    image: data.image || undefined,
    data: { url: data.url }
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

importScripts('https://www.gstatic.com/firebasejs/9.6.10/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.10/firebase-messaging-compat.js');

self.addEventListener('message', () => { /* placeholder */ });

firebase.initializeApp({
  apiKey: 'AIzaSyBlarIHSJMrD64TX9wq3TBPAZ_e-a2qEk0',
  authDomain: 'pushii-75128.firebaseapp.com',
  projectId: 'pushii-75128',
  messagingSenderId: '856171295104',
  appId: '1:856171295104:web:799355339f9c1f21a61165'
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  const title = (payload.notification && payload.notification.title) || 'Notification';
  const options = {
    body: (payload.notification && payload.notification.body) || '',
    icon: payload.notification && payload.notification.icon
  };
  self.registration.showNotification(title, options);
});

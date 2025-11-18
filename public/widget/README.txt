How to use the widget:

1) Add these scripts into your site's <head>:
<script src="https://www.gstatic.com/firebasejs/9.6.11/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.6.11/firebase-messaging-compat.js"></script>

2) Add widget script (adjust path if you host elsewhere):
<script src="/widget/widget.js"></script>

3) Call the helper with your public VAPID key:
<script>
  // replace with your VAPID key and the register endpoint if different
  webpushRegister('YOUR_PUBLIC_VAPID_KEY', 'https://your-dashboard.example.com/api/register-token');
</script>

Note: ensure service worker file (firebase-messaging-sw.js) is served at the site root.

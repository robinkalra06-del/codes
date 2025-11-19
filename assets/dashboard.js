// assets/dashboard.js
document.getElementById('sendForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const form = e.target;
  const title = form.title.value;
  const body = form.body.value;
  const icon = form.icon.value;

  const res = await fetch('/api/send-notification.php', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ title, body, icon })
  });
  const json = await res.json();
  document.getElementById('out').textContent = JSON.stringify(json, null, 2);
});

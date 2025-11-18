async function sendNoti() {
  const title = document.getElementById('title').value;
  const body = document.getElementById('bodyTxt').value;
  const token = document.getElementById('token').value;

  const res = await fetch('/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, body, token })
  });

  const data = await res.json();
  alert(JSON.stringify(data));
}

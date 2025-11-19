<?php
// public/dashboard.php
require __DIR__ . '/../vendor/autoload.php';
use App\Database;

$subsCount = Database::count();
?>
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Push Dashboard</title>
  <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
  <div class="container">
    <h1>Push Notification Dashboard</h1>
    <p>Total subscribers: <strong id="subsCount"><?= $subsCount ?></strong></p>

    <section class="card">
      <h2>Send Notification</h2>
      <form id="sendForm">
        <label>Title</label>
        <input type="text" name="title" placeholder="Title" required />
        <label>Body</label>
        <textarea name="body" placeholder="Message" required></textarea>
        <label>Icon URL (optional)</label>
        <input type="text" name="icon" placeholder="https://..." />
        <button type="submit">Send to All</button>
      </form>
      <pre id="out"></pre>
    </section>

    <section class="card">
      <h2>Quick Info</h2>
      <p>To subscribe a client, include the script: <code>&lt;script src="https://your-domain/subscribe.js"&gt;&lt;/script&gt;</code></p>
      <p>Service worker file: <code>/sw.js</code></p>
    </section>
  </div>
  <script src="/assets/dashboard.js"></script>
</body>
</html>

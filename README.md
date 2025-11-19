# WebPush Backend (Simple)

## Setup (local, Windows/XAMPP)
1. PHP & Composer installed.
2. Clone project.
3. Run `composer install`.
4. Generate VAPID keys:
   - `php vendor\minishlink\web-push\src\CLI\generateVAPID.php`
   - Copy keys to `.env`.
5. Start local server:
   - `php -S localhost:8000 -t public`
6. Open `http://localhost:8000` (Dashboard).

## Deploy on Render
1. Push repo to GitHub.
2. Create new Web Service on Render, select repo.
3. Use Dockerfile (auto) or set:
   - Build: `composer install`
   - Start: `php -S 0.0.0.0:10000 -t public`
4. Add environment variables (VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY, VAPID_SUBJECT).
5. Deploy.

## Client integration
Include `/subscribe.js` on client page (replace VAPID public key).

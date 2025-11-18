# Professional WebPush System

This project provides a production-ready backend + admin dashboard for sending Firebase Cloud Messaging (FCM) web push notifications.

## Features
- Firebase Admin integration (SERVICE_ACCOUNT_JSON)
- CORS enabled
- SQLite token store
- Admin authentication (JWT or legacy API key)
- Admin dashboard (login, tokens, send, broadcast, logs)
- Service worker and frontend helper for token registration

## Quick start
1. Copy `.env.example` to `.env` and fill values.
2. Install dependencies: `npm install`
3. Run: `npm start`
4. Deploy on Render (recommended) by connecting GitHub repo, set env vars in Render dashboard.

## Render notes
- Paste the entire service account JSON into the `SERVICE_ACCOUNT_JSON` environment variable.
- Set `ADMIN_EMAIL` and either `ADMIN_PASSWORD` or hashed `ADMIN_PASSWORD_HASH`.
- Use `ADMIN_JWT_SECRET` strong secret.

## Testing
- Open the admin UI (`/`) and login.
- Use browser client to register tokens (via fcm.js + firebase-messaging-sw.js).
- Send a test notification from dashboard.


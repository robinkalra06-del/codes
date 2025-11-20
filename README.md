# WebPush Dashboard (Render-ready)

This sample project is a FastAPI-based Web Push Notification Dashboard ready to deploy on Render.
It includes:
- FastAPI backend with Jinja2 templates and HTMX for dashboard interactions
- SQLAlchemy (Postgres) models
- pywebpush integration for sending Web Push notifications
- VAPID key generation script
- Admin login + multi-user accounts
- Simple analytics (counts)
- File upload support (S3 or local)
- Render deployment files: Dockerfile + render.yaml

**Note**: This is a starter project. For production hardening (encryption of private keys, background workers for bulk sends, rate limiting), see the notes in README.


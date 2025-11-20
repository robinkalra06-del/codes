1. Copy .env.example -> .env and fill VAPID keys (generate with `python generate_vapid.py`).
2. Create virtualenv: python -m venv venv && source venv/bin/activate
3. pip install -r requirements.txt
4. flask db init && flask db migrate && flask db upgrade
   (or use the run.py directly to create sqlite file automatically)
5. Create an admin user (in flask shell):
   from app import create_app
   from models import db, User
   app = create_app(); app.app_context().push()
   u = User(email='admin@example.com', password_hash='admin', is_admin=True)
   db.session.add(u); db.session.commit()
6. python run.py
7. Visit http://localhost:5000 and login (admin@example.com / admin)

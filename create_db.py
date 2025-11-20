from main import create_app
from models import db, User

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    print("✔ Database tables created.")

    # Create admin user
    admin = User(
        email="admin@example.com",
        password_hash="admin123",   # Use your hashing logic if needed
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()

    print("✔ Admin user created: admin@example.com / admin123")

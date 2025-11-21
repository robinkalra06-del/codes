from flask import Flask
from .routes import dashboard
from .auth import auth

def create_app():
    app = Flask(__name__)
    app.secret_key = "SUPER_SECRET"

    app.register_blueprint(auth)
    app.register_blueprint(dashboard)

    return app

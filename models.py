from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # replace with hashed in production
    is_admin = db.Column(db.Boolean, default=False)

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    origin = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscriptions = db.relationship('Subscription', backref='site', lazy=True)
    notifications = db.relationship('Notification', backref='site', lazy=True)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    endpoint = db.Column(db.Text, nullable=False)
    p256dh = db.Column(db.Text, nullable=False)
    auth = db.Column(db.Text, nullable=False)
    # INFO ABOUT DEVICE/CLIENT
    browser = db.Column(db.String(100))       # e.g. 'chrome', 'safari'
    device_type = db.Column(db.String(50))    # e.g. 'desktop', 'android', 'ios', 'phone'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text)
    url = db.Column(db.String(1024))
    icon = db.Column(db.String(1024))    # saved icon path / URL
    image = db.Column(db.String(1024))   # big image path / URL
    target_group = db.Column(db.String(64))  # 'all' or 'desktop' or 'android', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

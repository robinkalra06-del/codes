from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base

# -----------------------------
# USER MODEL
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relation
    sites = relationship("Site", back_populates="owner")


# -----------------------------
# SITE MODEL (FINAL)
# -----------------------------
class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    site_key = Column(String(128), unique=True, index=True)

    vapid_public = Column(Text, nullable=True)
    vapid_private = Column(Text, nullable=True)

    allow_origins = Column(Text, nullable=True)  # optional
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relations
    owner = relationship("User", back_populates="sites")
    subscriptions = relationship(
        "Subscription",
        back_populates="site",
        cascade="all, delete-orphan"
    )
    notifications = relationship("NotificationLog", back_populates="site")


# -----------------------------
# SUBSCRIPTION MODEL
# -----------------------------
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"))

    endpoint = Column(Text, nullable=False)
    keys_json = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    site = relationship("Site", back_populates="subscriptions")


# -----------------------------
# NOTIFICATION LOG MODEL
# -----------------------------
class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="SET NULL"))

    title = Column(String(255))
    message = Column(Text)
    payload = Column(Text)
    sent_to = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    site = relationship("Site", back_populates="notifications")

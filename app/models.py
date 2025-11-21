from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sites = relationship("Site", back_populates="owner")

class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255))
    domain = Column(String(255), nullable=False, unique=True, index=True)
    site_key = Column(String(128), unique=True, index=True)
    vapid_public = Column(Text, nullable=True)
    vapid_private = Column(Text, nullable=True)
    allow_origins = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = relationship("User", back_populates="sites")
    subscriptions = relationship("Subscription", back_populates="site", cascade="all, delete-orphan")
    notifications = relationship("NotificationLog", back_populates="site")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"))
    endpoint = Column(Text, nullable=False)
    keys_json = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    site = relationship("Site", back_populates="subscriptions")

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
    
class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)  # <-- this stores allowed origin!
    site_key = Column(String, unique=True)
    vapid_public = Column(Text)
    vapid_private = Column(Text)

    user = relationship("User", back_populates="sites")

from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))
    domain = Column(String(255))
    site_key = Column(String(255), unique=True, index=True)
    vapid_public = Column(String(999))
    vapid_private = Column(String(999))

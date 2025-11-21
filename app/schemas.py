# app/schemas.py
from pydantic import BaseModel
from typing import Optional, Any, Dict

class RegisterIn(BaseModel):
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

class SiteCreate(BaseModel):
    name: str
    domain: str

class SubscribeIn(BaseModel):
    site_key: str
    subscription: Dict[str, Any]

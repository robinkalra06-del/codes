# app/utils/domain_validator.py

from app.db import Website

def get_allowed_domains():
    """
    Returns list of domains stored in DB (entered by user in dashboard)
    Example: ['https://example.com', 'https://myblog.com']
    """
    try:
        rows = Website.select()
        return [w.domain for w in rows]
    except:
        return []

# app/storage.py
import os, uuid
from fastapi import UploadFile
from app.config import settings

def save_file(upload: UploadFile, folder: str = "") -> str:
    os.makedirs(settings.UPLOADS_PATH, exist_ok=True)
    if folder:
        folder_path = os.path.join(settings.UPLOADS_PATH, folder)
        os.makedirs(folder_path, exist_ok=True)
    else:
        folder_path = settings.UPLOADS_PATH

    ext = os.path.splitext(upload.filename)[1] or ""
    name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(folder_path, name)
    with open(path, "wb") as f:
        f.write(upload.file.read())
    # return public path
    return f"/uploads/{folder}/{name}" if folder else f"/uploads/{name}"

import os
from .config import settings
from uuid import uuid4

if settings.USE_S3:
    import boto3
    s3 = boto3.client('s3', region_name=settings.S3_REGION or None,
                      aws_access_key_id=settings.S3_ACCESS_KEY, aws_secret_access_key=settings.S3_SECRET_KEY)

def save_file(upload_file, hint='file'):
    ext = os.path.splitext(upload_file.filename)[1]
    fname = f"{uuid4().hex}_{hint}{ext}"
    if settings.USE_S3:
        key = f"uploads/{fname}"
        s3.upload_fileobj(upload_file.file, settings.S3_BUCKET, key, ExtraArgs={'ACL':'public-read','ContentType': upload_file.content_type})
        return f"https://{settings.S3_BUCKET}.s3.amazonaws.com/{key}"
    else:
        path = os.path.join(settings.UPLOADS_PATH, fname)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            upload_file.file.seek(0)
            f.write(upload_file.file.read())
        return f'/uploads/{fname}'

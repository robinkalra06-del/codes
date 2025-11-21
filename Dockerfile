# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# install system deps for cryptography and bcrypt
RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python3-dev git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

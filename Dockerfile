FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY db.py charts.py watcher.py seed_data.py ./
COPY sql ./sql

# Compose sets ORACLE_* from .env; DB_BACKEND=oracle for server Docker
ENV DB_BACKEND=oracle
ENV PNG_EXPORT_DIR=/exports
ENV PNG_EXPORT_INTERVAL_SEC=120

RUN mkdir -p /exports

CMD ["python", "watcher.py"]

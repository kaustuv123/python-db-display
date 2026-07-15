FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY db.py charts.py watcher.py ./

# Paths inside the container; host mounts override via compose
ENV PORTS_DB_PATH=/data/ports.db
ENV PNG_EXPORT_DIR=/exports
ENV PNG_EXPORT_INTERVAL_SEC=120

RUN mkdir -p /data /exports

CMD ["python", "watcher.py"]

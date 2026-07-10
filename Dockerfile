# ── Stage: Python runtime with FastAPI + Streamlit ──
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend.py .
COPY frontend.py .
COPY database.py .
COPY add_data.py .
COPY start.sh .

# Make startup script executable
RUN chmod +x start.sh

# Expose ports: 8000 (FastAPI), 8501 (Streamlit)
EXPOSE 8000 8501

# Run both services via startup script
CMD ["./start.sh"]

# ── Python runtime with FastAPI pie-chart SVG API ──
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=600 -r requirements.txt

# Copy application code
COPY backend.py .
COPY database.py .
COPY chart_render.py .
COPY png_export.py .
COPY add_data.py .
COPY start.sh .

# Optional: mount or set PNG_EXPORT_DIR so charts write every 2 min on data change
ENV PNG_EXPORT_DIR=/home/oracle/product/fmw14.1.2/forms/images/

# Make startup script executable
RUN chmod +x start.sh

# Expose FastAPI
EXPOSE 8000

CMD ["./start.sh"]

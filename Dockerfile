FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=600 -r requirements.txt

COPY backend.py database.py chart_render.py png_export.py add_data.py start.sh ./
RUN chmod +x start.sh

# PNG export path (override at runtime if needed)
ENV PNG_EXPORT_DIR=/home/oracle/product/fmw14.1.2/forms/images/

EXPOSE 8000
CMD ["./start.sh"]

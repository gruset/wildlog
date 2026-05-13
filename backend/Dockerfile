FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY app.py wsgi.py ./

# Data volume mount point
RUN mkdir -p /app/data

ENV DB_PATH=/app/data/hunting.db \
    FLASK_DEBUG=false \
    CORS_ORIGINS=*

EXPOSE 5050

# Gunicorn: 2 workers, 4 threads each — tune to your hardware
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "2", "--threads", "4", "--timeout", "60", "wsgi:app"]

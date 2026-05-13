FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py wsgi.py ./

RUN mkdir -p /app/data

ENV DB_PATH=/app/data/hunting.db \
    FLASK_DEBUG=false \
    CORS_ORIGINS=* \
    SESSION_COOKIE_SECURE=true \
    SESSION_HOURS=12
# SECRET_KEY and ADMIN_PASSWORD must be set via docker-compose or .env — never hardcoded

EXPOSE 5050

CMD ["gunicorn","--bind","0.0.0.0:5050","--workers","2","--threads","4","--timeout","60","wsgi:app"]

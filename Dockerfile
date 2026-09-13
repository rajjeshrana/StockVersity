FROM python:3.11-slim

WORKDIR /app

COPY website_backend/requirements.txt /app/website_backend/requirements.txt

RUN pip install --no-cache-dir -r /app/website_backend/requirements.txt

COPY website_backend /app/website_backend
COPY index.html /app/index.html
COPY app.js /app/app.js
COPY market_api.js /app/market_api.js
COPY assets /app/assets

COPY production_server.py /app/production_server.py

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn production_server:app --host 0.0.0.0 --port ${PORT:-8000}"]

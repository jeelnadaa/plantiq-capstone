# PlantIQ backend for a cloud VM / server.
#   docker build -t plantiq-backend -f backend/Dockerfile .          (from claude-plantiq/)
#   docker run --gpus all -p 8000:8000 --env-file backend/.env -v plantiq-var:/app/backend/var plantiq-backend
# CPU-only hosts work too (RAG auto-selects the "balanced" profile).

FROM node:20-slim AS web
WORKDIR /src/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npx vite build

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 ENV=production HF_HOME=/app/hf-cache
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/* \
 && useradd --create-home --uid 1000 plantiq
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
COPY --from=web /src/frontend/dist ./static
RUN mkdir -p var /app/hf-cache && chown -R plantiq:plantiq /app
USER plantiq
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/health')"
# TRUST_PROXY_HEADERS=true only when running behind your own reverse proxy (nginx/caddy terminating TLS).
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "8000"]

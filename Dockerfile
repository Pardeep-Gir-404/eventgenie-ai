# ==========================================
# Stage 1: Build Frontend Single-Page App
# ==========================================
FROM node:22-alpine AS frontend-builder
WORKDIR /build

# Copy dependency definitions and install (including devDependencies required for Vite build)
COPY frontend/package*.json ./
RUN npm ci || npm install

# Copy frontend source and compile production bundle inside the container
COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Production Python FastAPI Server
# ==========================================
FROM python:3.12-slim AS production

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PORT=8080 \
  HOST=0.0.0.0

WORKDIR /app

# Install curl for container health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Create an unprivileged user to run the application
RUN groupadd --system app \
  && useradd --system --gid app --home-dir /app --no-create-home appuser

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY --chown=appuser:app backend/app ./app

# Copy compiled frontend assets from Stage 1 into /app/static (served by FastAPI)
COPY --from=frontend-builder --chown=appuser:app /build/dist ./static

# Let the app create local cache files inside /app if it needs to
RUN chown appuser:app /app

USER appuser

# Render.com automatically overrides PORT (e.g. 10000); default to 8080 for Cloud Run / local
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:${PORT:-8080}/api/health || exit 1

# Launch uvicorn dynamically bound to $PORT with exec to handle process signals cleanly
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
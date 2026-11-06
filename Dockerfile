# PEC: one image serves the API (Django + gunicorn) and the built frontend (WhiteNoise).
# No database (D-10), so the root filesystem can be read-only; gunicorn needs only /tmp.

# 1. Build the frontend
FROM node:24-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-fund --no-audit
COPY frontend/ ./
RUN npm run build

# 2. Runtime
FROM python:3.15-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app

# Runtime dependencies only, exactly as locked; this layer is reused until uv.lock changes.
COPY pyproject.toml uv.lock .python-version ./
COPY backend/core/pyproject.toml backend/core/
COPY backend/web/pyproject.toml backend/web/
RUN uv sync --frozen --no-dev --no-install-workspace --no-cache

COPY backend/ backend/
RUN uv sync --frozen --no-dev --no-cache

COPY --from=frontend /frontend/dist frontend/dist
RUN DJANGO_DEBUG=0 DJANGO_SECRET_KEY=build-only python backend/web/manage.py collectstatic --noinput \
    && useradd --system --uid 10001 pec

USER pec
EXPOSE 8000
# --preload: the app (and the component data) load once, before the workers fork.
CMD ["gunicorn", "pecweb.wsgi:application", "--preload", "--bind", "0.0.0.0:8000", \
     "--workers", "2", "--timeout", "120", "--access-logfile", "-"]

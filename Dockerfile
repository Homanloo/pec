# PEC web app: Django behind gunicorn, static files served by WhiteNoise.
# numpy 1.25 has no wheels past Python 3.11.
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.10.0 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    PATH=/opt/venv/bin:$PATH \
    MPLBACKEND=Agg \
    MPLCONFIGDIR=/tmp/matplotlib \
    DJANGO_DB_PATH=/tmp/pec.sqlite3

WORKDIR /app

# Runtime only, exactly as locked: no dev tools, no notebooks.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-cache

COPY web-framework/ .
RUN rm -f db.sqlite3 \
    && DJANGO_DEBUG=0 DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput \
    && useradd --system --uid 10001 pec

USER pec
EXPOSE 8000

# The database holds no app data (admin and sessions only), so it lives in
# /tmp and is rebuilt on every start; the root filesystem can be read-only.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn vleW1.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --access-logfile -"]

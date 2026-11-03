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

# Runtime only, exactly as locked: no dev tools, no notebooks. Bytecode is
# compiled here: the root filesystem is read-only, so Python could never cache
# it and would recompile numpy, scipy and matplotlib on every start.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-cache --compile-bytecode

COPY web-framework/ .
RUN rm -f db.sqlite3 \
    && DJANGO_DEBUG=0 DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput \
    && python -m compileall -q . \
    && useradd --system --uid 10001 pec

USER pec
EXPOSE 8000

# The database holds no app data (admin and sessions only), so it lives in
# /tmp and is rebuilt on every start; the root filesystem can be read-only.
# --skip-checks: the checks import the whole science stack just to migrate.
# --preload: the app (see wsgi.py) loads once, before the workers fork.
CMD ["sh", "-c", "python manage.py migrate --noinput --skip-checks && exec gunicorn vleW1.wsgi:application --preload --bind 0.0.0.0:8000 --workers 2 --timeout 120 --access-logfile -"]

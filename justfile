# PEC — run `just` to list commands. CI runs the same recipes.

set shell := ["bash", "-uc"]

manage := "uv run python web-framework/manage.py"
pg_url := "postgres://pec:pec@localhost:25432/pec"

default:
    @just --list

# ========================================
# Setup & run
# ========================================

# Locked dependencies into .venv (add --group notebooks for Jupyter)
install:
    uv sync --locked

# Development server on http://localhost:8000
run:
    {{manage}} runserver

# Any manage.py command: just manage createsuperuser
manage *args:
    {{manage}} {{args}}

# ========================================
# Checks
# ========================================

# Everything CI checks, in its order
check: lint typecheck test migrations audit

lint:
    uv run ruff check .

# Apply ruff's safe fixes (import order, pyupgrade)
fix:
    uv run ruff check --fix .

typecheck:
    uv run ty check

# Tests with coverage (fails under the floor in pyproject.toml)
test *args:
    uv run pytest {{args}}

# Coverage as HTML in htmlcov/
cov:
    uv run pytest --cov-report=html && echo "open htmlcov/index.html"

# No model change without its migration
migrations:
    {{manage}} makemigrations --check --dry-run

# Known vulnerabilities in the runtime dependencies (what ships in the image)
audit:
    tmp=$(mktemp) && uv export --frozen --no-dev --no-hashes --no-header --no-annotate -o "$tmp" && uv run pip-audit --disable-pip --no-deps -r "$tmp"; s=$?; rm -f "$tmp"; exit $s

# ========================================
# Postgres (as in CI), on port 25432
# ========================================

pg-up:
    docker run -d --rm --name pec-pg -e POSTGRES_USER=pec -e POSTGRES_PASSWORD=pec -e POSTGRES_DB=pec -p 25432:5432 postgres:18
    until docker exec pec-pg pg_isready -U pec -q; do sleep 1; done

pg-down:
    docker stop pec-pg

# Tests and migrations against Postgres (just pg-up first)
test-pg:
    DATABASE_URL={{pg_url}} uv run pytest --create-db
    DATABASE_URL={{pg_url}} {{manage}} migrate --noinput

# ========================================
# Image
# ========================================

# Build the production image as zig1 runs it (linux/amd64)
build:
    docker build --platform linux/amd64 -t pec:local .

# Run it hardened like production on http://localhost:18000
serve: build
    docker run --rm --platform linux/amd64 --read-only --tmpfs /tmp --cap-drop ALL \
      --security-opt no-new-privileges -e DJANGO_DEBUG=0 -e DJANGO_SECRET_KEY=local \
      -e DJANGO_ALLOWED_HOSTS=localhost -p 18000:8000 pec:local

# PEC: run `just` to list recipes. CI runs the same ones.

set shell := ["bash", "-uc"]

default:
    @just --list

# Locked dependencies: Python into .venv, the frontend's into frontend/node_modules
install:
    uv sync --locked
    npm --prefix frontend ci --no-fund --no-audit

# Everything CI checks, in its order
check: lint typecheck test front-check audit

# Lint and format check
lint:
    uv run ruff check .
    uv run ruff format --check .

# Apply safe lint fixes and format
fmt:
    uv run ruff check --fix .
    uv run ruff format .

typecheck:
    uv run ty check backend

# Tests with coverage (fails under the floor in pyproject.toml)
test *args:
    uv run pytest {{args}}

# Coverage as HTML in htmlcov/
cov:
    uv run pytest --cov-report=html && echo "open htmlcov/index.html"

# Known vulnerabilities in the runtime dependencies (Python and the frontend's)
audit:
    tmp=$(mktemp) && uv export --frozen --no-dev --no-hashes --no-header --no-annotate --no-emit-workspace -o "$tmp" && uv run pip-audit --disable-pip --no-deps -r "$tmp"; s=$?; rm -f "$tmp"; exit $s
    npm --prefix frontend audit --omit=dev

# Frontend type check
front-check:
    npm --prefix frontend run check

# Build the frontend into frontend/dist (Django serves it from there)
build:
    npm --prefix frontend run build

# The site on http://127.0.0.1:8000 (API + the last `just build`)
web:
    uv run python backend/web/manage.py runserver 127.0.0.1:8000

# Frontend dev server with hot reload on http://127.0.0.1:5173 (needs `just web` for the API)
front:
    npm --prefix frontend run dev

# The production image, run the way zig1 runs it: read-only, no capabilities, DEBUG off
image:
    docker build -t pec:local .

serve: image
    docker run --rm --name pec --read-only --tmpfs /tmp --cap-drop ALL \
        --security-opt no-new-privileges -e DJANGO_DEBUG=0 -e DJANGO_SECRET_KEY=local \
        -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 -p 8000:8000 pec:local

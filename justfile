# PEC: run `just` to list recipes. CI runs the same ones.

set shell := ["bash", "-uc"]

default:
    @just --list

# Locked dependencies into .venv
install:
    uv sync --locked

# Everything CI checks, in its order
check: lint typecheck test audit

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

# Known vulnerabilities in the runtime dependencies
audit:
    tmp=$(mktemp) && uv export --frozen --no-dev --no-hashes --no-header --no-annotate --no-emit-workspace -o "$tmp" && uv run pip-audit --disable-pip --no-deps -r "$tmp"; s=$?; rm -f "$tmp"; exit $s

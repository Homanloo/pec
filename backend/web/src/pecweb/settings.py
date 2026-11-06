"""Django settings. No database (D-10): the API is stateless, the site is static files.

Environment (same names the old image used on zig1):
  DJANGO_DEBUG          "1" (default, local) or "0" (production)
  DJANGO_SECRET_KEY     required when DEBUG is off
  DJANGO_ALLOWED_HOSTS  comma-separated host names
  PEC_FRONTEND_DIST     built frontend (default: <repo>/frontend/dist)
"""

import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is off")
    SECRET_KEY = "insecure-local-development-key"
ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]

if not DEBUG:
    # Behind the TLS-terminating proxy on zig1
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",  # Swagger UI files served locally, not from a CDN (B-24)
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
]
ROOT_URLCONF = "pecweb.urls"
WSGI_APPLICATION = "pecweb.wsgi.application"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}]
DATABASES = {}
USE_TZ = True

# The frontend is built by Vite with base "/static/", so its files are plain static files.
FRONTEND_DIST = Path(os.environ.get("PEC_FRONTEND_DIST", REPO / "frontend" / "dist"))
STATIC_URL = "/static/"
STATIC_ROOT = REPO / "staticfiles"
STATICFILES_DIRS = [FRONTEND_DIST] if FRONTEND_DIST.is_dir() else []
STORAGES = {"staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"}}


def WHITENOISE_IMMUTABLE_FILE_TEST(path, url):
    # Vite puts a content hash in every asset name (index-B2x9fQ1a.js): cache those forever.
    return re.match(r"^.+-[0-9A-Za-z_-]{8}\.\w+$", url) is not None


REST_FRAMEWORK = {
    # No users, no sessions: the API is open and stateless.
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
SPECTACULAR_SETTINGS = {
    "TITLE": "PEC API",
    "DESCRIPTION": (
        "Phase equilibrium calculations with cubic equations of state (vdW, RK, SRK, PR). "
        "Inputs in SI (K, Pa) or as {value, unit}; outputs in SI."
    ),
    "VERSION": "1",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

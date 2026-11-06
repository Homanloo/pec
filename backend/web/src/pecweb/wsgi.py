"""WSGI entry point for gunicorn."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pecweb.settings")
application = get_wsgi_application()

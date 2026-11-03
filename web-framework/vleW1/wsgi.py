"""
WSGI config for vleW1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vleW1.settings')

application = get_wsgi_application()

# Load the URLconf (and with it numpy, scipy and matplotlib) now, not on the
# first request: under gunicorn --preload the workers fork with it loaded.
from django.urls import get_resolver  # noqa: E402

get_resolver().url_patterns

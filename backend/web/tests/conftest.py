import os

import django

# The test client sends Host: testserver; no database is needed (D-10).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pecweb.settings")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "testserver")
django.setup()

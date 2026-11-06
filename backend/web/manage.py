"""Django's command-line entry point (runserver, collectstatic, check)."""

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pecweb.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

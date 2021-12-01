#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os


from core.models import PostContent

if __name__ == '__main__':

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smi_django.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    s = PostContent.objects.create(
        content="text",
        cache_id=1,
        keyword_id=10000003)
    main()

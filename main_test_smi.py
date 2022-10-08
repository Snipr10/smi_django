#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os

if __name__ == '__main__':
    while True:
        try:
            from threading import Thread
            from multiprocessing import Process

            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smi_django.settings')
            try:
                from django.core.management import execute_from_command_line
            except ImportError as exc:
                raise ImportError(
                    "Couldn't import Django. Are you sure it's installed and "
                    "available on your PYTHONPATH environment variable? Did you "
                    "forget to activate a virtual environment?"
                ) from exc
            from core.sites.tass import parsing_tass
            from datetime import datetime

            articles, proxy = parsing_tass("единая россия", datetime.strptime("21/05/2022", "%d/%m/%Y"), None, [])

        except Exception as e:
            print(f"__name__{e}")
            pass

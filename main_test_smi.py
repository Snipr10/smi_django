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
            from datetime import datetime
            from core.sites.thecitym24 import parsing_thecitym24
            from core.sites.utils import save_articles

            articles, proxy = parsing_thecitym24("Ярмарка современного искусства", datetime.strptime("05/09/2022", "%d/%m/%Y"), None, [])
            save_articles(14935787485712012734, articles)

        except Exception as e:
            print(f"__name__{e}")
            pass

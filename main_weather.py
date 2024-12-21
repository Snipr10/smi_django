import os
import datetime
import time


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

    print(1)
    import django

    django.setup()

    while True:
        try:
            import django.db

            from django.utils import timezone
            from core.models import GlobalSite, ParsingPrecipitation
            from core.weather.gismeteo import parsing_gismeteo

            parsing_gismeteo()


            time.sleep(60)
        except Exception as e:
            print(f"Error {e}")
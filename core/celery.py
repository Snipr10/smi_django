import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smi_django.settings')

import django

django.setup()

app = Celery('smi_django', include=['smi_django.tasks'])
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'start_task_parsing_by_time': {
        'task': 'smi_django.tasks.start_task_parsing_by_time',
        'schedule': crontab(minute='*/5')
    },
    'add_new_key': {
        'task': 'smi_django.tasks.add_new_key',
        'schedule': crontab(minute='29')
        # 'schedule': crontab(minute='*/12')
    },
    'task_parsing_key': {
        'task': 'smi_django.tasks.task_parsing_key',
        # 'schedule': crontab(minute='5, 35')
        'schedule': 2.0,
        # 'schedule': crontab(minute='*/1')

    },
    'untaken_key': {
        'task': 'smi_django.tasks.untaken_key',
        'schedule': crontab(minute='31')
        # 'schedule': crontab(minute='*/12')
    },



    # 'activate_key': {
    #     'task': 'smi_django.tasks.activate_key',
    #     'schedule': crontab(minute='1')
    #     # 'schedule': crontab(minute='*/12')
    # },

    # 'update_time': {
    #     'task': 'smi_django.tasks.update_time',
    #      'schedule': crontab(minute='57')
    # }
    # 'delete_bad_posts': {
    #     'task': 'smi_django.tasks.delete_bad_posts',
    #      'schedule': crontab(minute='30')
    # }
    # 'start_task_parsing_echo': {
    #     'task': 'smi_django.tasks.start_task_parsing_echo',
    #     'schedule': crontab(minute='5, 35')
    # },
    # 'start_task_parsing_radio': {
    #     'task': 'smi_django.tasks.start_task_parsing_radio',
    #     'schedule': crontab(minute='10, 40')
    # },
    # 'start_task_parsing_zenit': {
    #     'task': 'smi_django.tasks.start_task_parsing_zenit',
    #     'schedule': crontab(minute='15, 45')
    # },
    # 'start_task_parsing_radiosvodoba': {
    #     'task': 'smi_django.tasks.start_task_parsing_radiosvodoba',
    #     'schedule': crontab(minute='20, 50')
    #
    # },
}

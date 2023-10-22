import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smi_django.settings')

import django

try:
    django.setup()
except Exception as e:
    print("can not start django")

app = Celery('smi_django', include=['smi_django.tasks'])
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # #
    # # 'rabbit_mq': {
    # #     'task': 'smi_django.tasks.rabbit_mq',
    # #     'schedule': crontab(minute='*/1')
    # # },
    #
    # # 'start_task_parsing_by_time': {
    # #     'task': 'smi_django.tasks.start_task_parsing_by_time',
    # #     'schedule': crontab(minute='*/10')
    # # },
    # 'add_new_key': {
    #     'task': 'smi_django.tasks.add_new_key',
    #     # 'schedule': crontab(minute='29')
    #     'schedule': crontab(minute='*/15')
    # },
    'task_parsing_key': {
        'task': 'smi_django.tasks.task_parsing_key',
        # 'schedule': crontab(minute='5, 35')
        'schedule': 2.0,
        # 'schedule': crontab(minute='*/1')

    },
    # 'untaken_key': {
    #     'task': 'smi_django.tasks.untaken_key',
    #     'schedule': crontab(minute='*/30')
    #     # 'schedule': crontab(minute='*/12')
    # },
    # 'update_key_pool': {
    #     'task': 'smi_django.tasks.update_key_pool',
    #     'schedule': crontab(minute='*/5')
    #     # 'schedule': crontab(minute='*/12')
    # }
    # # 'update_smi': {
    # #     'task': 'smi_django.tasks.update_smi',
    # #     # 'schedule': crontab(minute='*/1')
    # #     'schedule': 2.0,
    # #
    # #     # 'schedule': crontab(minute='*/12')
    # # },
    # # 'update_smi_new': {
    # #     'task': 'smi_django.tasks.update_smi_new',
    # #     'schedule': crontab(minute='*/1')
    # #     # 'schedule': 2.0,
    # #
    # #     # 'schedule': crontab(minute='*/12')
    # # },
    #
    # #
    # #
    # # 'update_dp': {
    # #     'task': 'smi_django.tasks.update_dp',
    # #     'schedule': crontab(minute='30')
    # #     # 'schedule': crontab(minute='*/12')
    # # },
    #
    # # 'update_time': {
    # #     'task': 'smi_django.tasks.update_time',
    # #      'schedule': crontab(minute='57')
    # # }
    # # 'delete_bad_posts': {
    # #     'task': 'smi_django.tasks.delete_bad_posts',
    # #      'schedule': crontab(minute='30')
    # # }
    # # 'start_task_parsing_echo': {
    # #     'task': 'smi_django.tasks.start_task_parsing_echo',
    # #     'schedule': crontab(minute='5, 35')
    # # },
    # # 'start_task_parsing_radio': {
    # #     'task': 'smi_django.tasks.start_task_parsing_radio',
    # #     'schedule': crontab(minute='10, 40')
    # # },
    # # 'start_task_parsing_zenit': {
    # #     'task': 'smi_django.tasks.start_task_parsing_zenit',
    # #     'schedule': crontab(minute='15, 45')
    # # },
    # # 'start_task_parsing_radiosvodoba': {
    # #     'task': 'smi_django.tasks.start_task_parsing_radiosvodoba',
    # #     'schedule': crontab(minute='20, 50')
    # #
    # # },
}

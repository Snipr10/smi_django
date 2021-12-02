#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import time
from concurrent.futures import ThreadPoolExecutor

import pika

from core.models import PostContent
from core.sites.utils import get_sphinx_id
from core.utils.parsing_smi_url import parsing_smi_url


def create_rmq(i):
    print("rabbit_mq")
    print("len " + str(i))

    try:
        parameters = pika.URLParameters("amqp://full_posts_parser:nJ6A07XT5PgY@192.168.5.46:5672/smi_tasks")
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel(channel_number=i)
        print("channel " + str(i))

        def callback(ch, method, properties, body):
            try:
                text = parsing_smi_url(body.decode("utf-8"))
                print(text)
                if text is not None and text.strip() != "":
                    try:
                        s = PostContent.objects.create(
                                content=text,
                                cache_id=get_sphinx_id(body.decode("utf-8")),
                                keyword_id=10000003)
                        print(get_sphinx_id(body.decode("utf-8")))
                    except Exception as e:
                            print("save " + str(e))

            except Exception as e:
                    print(e)
        channel.basic_consume(queue='full_posts_tasks', on_message_callback=callback)
        # channel.basic_consume(queue='full_posts_tasks', on_message_callback=callback, auto_ack=False)
        channel.start_consuming()
    except Exception as e:
        print(e)
        time.sleep(1)

def prin(i):
    print(i)
    time.sleep(10)


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
    pool_source = ThreadPoolExecutor(500)
    for i in range(500):
        pool_source.submit(create_rmq, i)
    pool_source.shutdown()

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

import pika

from core.models import PostContent
from core.sites.utils import get_sphinx_id, delete_html_tags
from core.utils.parsing_smi_url import parsing_smi_url

contents = []

CHANNELS = {}


def open_save_chanel(i):
    parameters_save = pika.URLParameters("amqp://full_posts_parser:nJ6A07XT5PgY@192.168.5.46:5672/smi_tasks")
    connection_save = pika.BlockingConnection(parameters=parameters_save)
    channel_save = connection_save.channel(channel_number=i * 20)
    print("open_save_chanel " + str(i))
    return channel_save


def save_data(rmq_json_data, i, attempts=0):
    try:
        channel_save = CHANNELS.get(i)
        channel_save.basic_publish(exchange='',
                                   routing_key='smi_posts',
                                   body=json.dumps(rmq_json_data))
        if attempts ==0:
            return False
        else:
            return True
    except Exception as e:
        if attempts < 5:
            attempts += 1
            try:
                CHANNELS.get(i).close()
            except Exception as e:
                print(e)
            channel_save = open_save_chanel(i)
            CHANNELS[i] = channel_save
            return save_data(rmq_json_data, i, attempts=attempts)
        else:
            raise e


def print_status(i):
    while True:
        print("work")
        time.sleep(3600)


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
                body = json.loads(body.decode("utf-8"))
                url = body.get("url")
                text = parsing_smi_url(url)
                if text is not None and text.strip() != "":
                    try:
                        title = delete_html_tags(body.get("title"))
                        rmq_json_data = {
                            "title": title,
                            "content": text,
                            "created": body.get("created"),
                            "url": url,
                            "author_name": "",
                            "author_icon": "",
                            "group_id": "",
                            "images": [],
                            "keyword_id": 10000003,
                        }
                        # if save_data(rmq_json_data, ch, i):
                        save_data(rmq_json_data, i)
                        print(get_sphinx_id(url))
                    except Exception as e:
                        print("save " + str(e))

            except Exception as e:
                print(e)

        # channel.basic_consume(queue='full_posts_tasks', on_message_callback=callback)
        channel.basic_consume(queue='full_posts_tasks', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except Exception as e:
        time.sleep(100)
        create_rmq(i)


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
            treads = []
            for i in range(10):
                CHANNELS.update({i: open_save_chanel(i)})
                treads.append(Process(target=create_rmq, args=(i,)))
            treads.append(Process(target=print_status, args=(0,)))

            for t in treads:
                t.start()
            for t in treads:
                t.join()
        except Exception as e:
            pass

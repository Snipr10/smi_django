import logging
from datetime import timedelta
import datetime

import requests
from django.db.models import Q

from core.models import Sources, KeywordSource, Keyword, SourcesItems
from core.parsing_by_hashtag import parsing_hashtag
from core.parsing_by_username import parsing_username
from core.utils.utils import update_time_timezone
from tiktok.celery.celery import app
from django.utils import timezone


@app.task
def start_task_parsing_echo():
    articles, proxy = parsing_radio_echo(get_late_date(ECHO_RADIO_URL), update_proxy(None))
    stop_proxy(proxy)
    save_articles(ECHO_RADIO_URL, articles)


@app.task
def start_task_parsing_radio():
    articles, proxy = parsing_radio(get_late_date(RADIO_URL), update_proxy(None))
    stop_proxy(proxy)
    save_articles(RADIO_URL, articles)


@app.task
def start_task_parsing_zenit():
    articles, proxy = parsing_radio_zenit(get_late_date(ZENIT_RADIO_URL), update_proxy(None))
    stop_proxy(proxy)
    save_articles(ZENIT_RADIO_URL, articles)


@app.task
def start_task_parsing_radiosvodoba():
    articles, proxy = parsing_radiosvoboda(get_late_date(SVOBODA_RADIO_URL), update_proxy(None))
    stop_proxy(proxy)
    save_articles(SVOBODA_RADIO_URL, articles)

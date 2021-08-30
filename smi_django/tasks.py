from smi_django.celery.celery import app

from core.sites.utils import get_late_date, update_proxy, stop_proxy, save_articles
from core.sites.echo import parsing_radio_echo, RADIO_URL as ECHO_RADIO_URL
from core.sites.radio import parsing_radio, RADIO_URL
from core.sites.radiozenit import parsing_radio_zenit, RADIO_URL as ZENIT_RADIO_URL
from core.sites.svoboda import parsing_radiosvoboda, RADIO_URL as SVOBODA_RADIO_URL


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

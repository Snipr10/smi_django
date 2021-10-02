import datetime

from django.db.models import Q
from django.utils import timezone

from core.models import GlobalSite, SiteKeyword, Keyword
from smi_django.celery.celery import app

from core.sites.utils import get_late_date, update_proxy, stop_proxy, save_articles, update_time_timezone
from core.sites.echo import parsing_radio_echo, RADIO_URL as ECHO_RADIO_URL
from core.sites.radio import parsing_radio, RADIO_URL
from core.sites.radiozenit import parsing_radio_zenit, RADIO_URL as ZENIT_RADIO_URL
from core.sites.svoboda import parsing_radiosvoboda, RADIO_URL as SVOBODA_RADIO_URL


@app.task
def start_task_parsing_by_time():
    for site in GlobalSite.objects.filter(is_keyword=0, last_parsing__lte=update_time_timezone(
            timezone.localtime()
    ) - datetime.timedelta(minutes=5)):

        site.taken = 1
        site.save(update_fields=["taken"])

        try:
            if site.url == RADIO_URL:
                articles, proxy = parsing_radio(site.last_parsing, update_proxy(None))
            if site.url == RADIO_URL:
                articles, proxy = parsing_radio(site.last_parsing, update_proxy(None))
            save_articles(RADIO_URL, articles)
            site.last_parsing = update_time_timezone(timezone.localtime())
            site.taken = 0
            site.save(update_fields=["taken", "last_parsing"])

        except Exception as e:
            print(e)
            site.taken = 0
            site.save(update_fields=["taken"])


@app.task
def add_new_key():
    new_key_list = []
    for site in GlobalSite.objects.filter(is_keyword=1):
        keywords_list = list(SiteKeyword.objects.filter(site_id=site.site_id).values_list('keyword_id', flat=True))
        new_keys = Keyword.objects.filter(~Q(id__in=keywords_list), network_id=1, disabled=0)
        for new_key in new_keys:
            new_key_list.append(SiteKeyword(site_id=site.site_id, keyword_id=new_key.id))
    SiteKeyword.objects.bulk_create(new_key_list, batch_size=200, ignore_conflicts=True)


# @app.task
# def start_task_parsing_echo():
#     articles, proxy = parsing_radio_echo(get_late_date(ECHO_RADIO_URL), update_proxy(None))
#     stop_proxy(proxy)
#     save_articles(ECHO_RADIO_URL, articles)
#
#
# @app.task
# def start_task_parsing_radio():
#     articles, proxy = parsing_radio(get_late_date(RADIO_URL), update_proxy(None))
#     stop_proxy(proxy)
#     save_articles(RADIO_URL, articles)
#
#
# @app.task
# def start_task_parsing_zenit():
#     articles, proxy = parsing_radio_zenit(get_late_date(ZENIT_RADIO_URL), update_proxy(None))
#     stop_proxy(proxy)
#     save_articles(ZENIT_RADIO_URL, articles)
#
#
# @app.task
# def start_task_parsing_radiosvodoba():
#     articles, proxy = parsing_radiosvoboda(get_late_date(SVOBODA_RADIO_URL), update_proxy(None))
#     stop_proxy(proxy)
#     save_articles(SVOBODA_RADIO_URL, articles)

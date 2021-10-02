import datetime

from django.db.models import Q
from django.utils import timezone

from core.models import GlobalSite, SiteKeyword, Keyword, Sources, KeywordSource
from smi_django.celery.celery import app

from core.sites.utils import get_late_date, update_proxy, stop_proxy, save_articles, update_time_timezone
from core.sites.echo import parsing_radio_echo, RADIO_URL as ECHO_RADIO_URL
from core.sites.radio import parsing_radio, RADIO_URL
from core.sites.radiozenit import parsing_radio_zenit, RADIO_URL as ZENIT_RADIO_URL
from core.sites.svoboda import parsing_radiosvoboda, RADIO_URL as SVOBODA_RADIO_URL


@app.task
def start_task_parsing_by_time():
    for site in GlobalSite.objects.filter(taken=0, is_keyword=0, last_parsing__lte=update_time_timezone(
            timezone.localtime()
    ) - datetime.timedelta(minutes=5)):

        site.taken = 1
        site.save(update_fields=["taken"])

        try:
            if site.url == RADIO_URL:
                articles, proxy = parsing_radio(site.last_parsing, update_proxy(None))
            if site.url == ZENIT_RADIO_URL:
                articles, proxy = parsing_radio_zenit(site.last_parsing, update_proxy(None))
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
        new_keys = Keyword.objects.filter(~Q(id__in=keywords_list), network_id=1, disabled=0, enabled=1)
        for new_key in new_keys:
            new_key_list.append(SiteKeyword(site_id=site.site_id, keyword_id=new_key.id))
    SiteKeyword.objects.bulk_create(new_key_list, batch_size=200, ignore_conflicts=True)


@app.task
def parsing_key():
    select_sources = Sources.objects.filter(
        Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
        status=1)

    key_source = KeywordSource.objects.filter(source_id__in=list(select_sources.values_list('id', flat=True)))

    key_words = Keyword.objects.filter(network_id=1, enabled=1,
                                       id__in=list(key_source.values_list('keyword_id', flat=True))
                                       )

    site_key_words = SiteKeyword.objects.filter(taken=0, is_active=1,
                                                keyword_id__in=list(key_words.values_list('id', flat=True))
                                                ).order_by('last_modified')
    iteration = 0
    MAX_SIZE_PARSE_BY_WORD = 10
    for key_word in site_key_words:
        if iteration > MAX_SIZE_PARSE_BY_WORD or \
                SiteKeyword.objects.filter(network_id=1, taken=1).count() > MAX_SIZE_PARSE_BY_WORD:
            break
        if key_word is not None:
            select_source = select_sources.get(id=key_source.filter(keyword_id=key_word.keyword_id).first().source_id)
            last_update = key_word.last_modified
            if last_update < datetime.datetime(2001, 1, 1, 0, 0):
                depth = key_words.get(id=key_word.keyword_id).depth
                last_update = datetime.datetime(depth.year, depth.month, depth.day, 0, 0)
            time = select_source.sources
            if time is None:
                time = 10
            if last_update is None or (last_update + datetime.timedelta(minutes=time) <
                                       update_time_timezone(timezone.localtime())):
                key_word.taken = 1
                key_word.save(update_fields=['taken'])
                try:
                    print(1)
                except Exception as e:
                    print(e)
                    key_word.taken = 0
                    key_word.save(update_fields=['taken'])
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

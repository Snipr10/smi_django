import concurrent
import datetime
import time

import pika

from django.db.models import Q
from django.utils import timezone
import django.db

from pytz import UTC

from core.models import GlobalSite, SiteKeyword, Keyword, Sources, KeywordSource, Post, ParsingSite, PostContent, \
    PostContentGlobal
from core.sites.dp import parsing_dp, PAGE_URL as DP_URL
from core.sites.echo_msk import parsing_echo_msk
from core.sites.expertnw import parsing_expertnw
from core.sites.fontanka import parsing_fontanka
from core.sites.gorod_812 import parsing_gorod_812
from core.sites.gov_spb.pars_gov import start_parsing
from core.sites.interfax import parsing_interfax
from core.sites.moika_78 import parsing_moika78
from core.sites.news_admin_petr import parsing_news_admin_petr
from core.sites.news_spb import parsing_news_spb
from core.sites.novayagazeta import parsing_novayagazeta
from core.sites.radiorus import parsing_radio_rus
from core.sites.svoboda_new import parsing_svoboda_new
from core.sites.tass import parsing_tass
from core.sites.thecitym24 import parsing_thecitym24
from core.sites.vecherkaspb import parsing_vecherkaspb
from core.sites.vedomosti import parsing_vedomosti
from core.sites.zaks import parsing_zaks

from core.celery import app

from core.sites.utils import get_late_date, update_proxy, stop_proxy, save_articles, update_time_timezone, batch_size, \
    get_sphinx_id
from core.sites.echo import parsing_radio_echo, RADIO_URL as ECHO_RADIO_URL
from core.sites.radio import parsing_radio, RADIO_URL
from core.sites.radiozenit import parsing_radio_zenit, RADIO_URL as ZENIT_RADIO_URL
from core.sites.five_tv import parsing_5_tv
from concurrent.futures.thread import ThreadPoolExecutor

from core.utils.parsing_smi_url import parsing_smi_url
from smi_django.settings import START_RMQ



@app.task
def start_task_parsing_by_time():
    print("start")
    for site in GlobalSite.objects.filter(taken=0, is_keyword=0, last_parsing__lte=update_time_timezone(
            timezone.localtime()
    ) - datetime.timedelta(minutes=60)).order_by("last_parsing"):
        print(site.url)
        site.taken = 1
        site.save(update_fields=["taken"])
        django.db.close_old_connections()
        try:
            print(site.url)

            articles = []
            attempt = 0
            while attempt < 30 and len(articles) == 0:
                proxy = None
                if site.url == RADIO_URL:
                    articles, proxy = parsing_radio(site.last_parsing, update_proxy(None))
                if site.url == ZENIT_RADIO_URL:
                    articles, proxy = parsing_radio_zenit(site.last_parsing, update_proxy(None), [])
                if site.url == "https://www.gov.spb.ru":
                    articles, proxy = start_parsing(site.last_parsing, update_proxy(None))
                if site.url == DP_URL:
                    articles, proxy = parsing_dp(site.last_parsing, update_proxy(None))
                if site.url == "http://xn--e1aqccgid7fsa.xn--p1ai/":
                    articles, proxy = parsing_news_admin_petr(site.last_parsing, update_proxy(None))
                    break
                if site.url in ["http://www.admnews.ru/",
                                "http://www.krgv.ru/",
                                "http://www.petrogradnews.ru/",
                                "http://www.ksnews.ru/",
                                "http://www.news-kron.ru/",
                                "http://www.kurort-news.ru/",
                                "http://www.mr-news.ru/",
                                "http://www.nevnews.ru/",
                                # "http://xn--e1aqccgid7fsa.xn--p1ai/",
                                "http://www.pd-news.ru/",
                                "http://www.primorsknews.ru/",
                                "http://www.pushkin-news.ru/",
                                "http://www.frunznews.ru/",
                                "http://www.news-centre.ru/",
                                "http://www.newskolpino.ru/",
                                "http://www.kirnews.ru/",
                                "http://www.kalininnews.ru/",
                                "http://www.vybnews.ru/",
                                "http://www.vonews.ru/",
                                ]:
                    articles, proxy = parsing_news_spb(site.url, site.last_parsing, update_proxy(None))
                    break
                # parsing_news_spb(region, limit_date, proxy)
                attempt += 1
                stop_proxy(proxy)
            save_articles(site.url, articles)
            django.db.close_old_connections()
            if len(articles) > 0:
                site.last_parsing = update_time_timezone(timezone.localtime())
            site.taken = 0
            site.save(update_fields=["taken", "last_parsing"])

        except Exception as e:
            print(f"start_task_parsing_by_time {site.url} {e}")
            site.taken = 0
            site.save(update_fields=["taken"])


@app.task
def add_new_key():
    new_key_list = []
    stop_list = []
    print("start add")
    source = Sources.objects.filter(published=1,status=1)
    key_source = KeywordSource.objects.filter(source_id__in=list(source.values_list('id', flat=True)))
    active_keyword = Keyword.objects.filter(id__in=list(key_source.values_list('keyword_id', flat=True)), network_id=1, disabled=0, enabled=1)
    for site in GlobalSite.objects.filter(is_keyword=1):
        print(site.site_id)
        i = 0
        site_k = SiteKeyword.objects.filter(site_id=site.site_id)
        keywords_list = list(site_k.values_list('keyword_id', flat=True))
        new_keys = active_keyword.filter(~Q(id__in=keywords_list))
        for new_key in new_keys:
            new_key_list.append(SiteKeyword(site_id=site.site_id, keyword_id=new_key.id))
        # active_keys_list = list(active_keyword)
        # for k in site_k:
        #     if k.keyword_id not in active_keys_list:
        #         k.is_active = 0
        #         # print(k.keyword_id)
        #         stop_list.append(k)
    try:
        SiteKeyword.objects.bulk_create(new_key_list, batch_size=200, ignore_conflicts=True)
    except Exception as e:
        print(e)

    for site in GlobalSite.objects.filter(is_keyword=1):
        print(site.site_id)
        site_k = SiteKeyword.objects.filter(site_id=site.site_id)
        active_keys_list = list(active_keyword.values_list('id', flat=True))
        for k in site_k:
            if k.keyword_id not in active_keys_list:
                k.is_active = 0
                k.save(update_fields=['is_active'])
                # print(k.keyword_id)
                stop_list.append(k)

    try:
        print("SiteKeyword UPDATE")
        print(len(stop_list))
        print("SiteKeyword UPDATE")

        SiteKeyword.objects.bulk_update(stop_list, ['is_active'], batch_size=200)
    except Exception as e:
        print(e)

@app.task
def delete_bad_posts():
    i = 0
    for post in Post.objects.filter(display_link="https://expertnw.com"):
        print(i)
        i += 1
        if "/?sphrase_id=" in post.link:
            post.delete()


@app.task
def update_time():
    i = 0
    for site_id in SiteKeyword.objects.filter(site_id=11880147896115333104, last_parsing__gte=update_time_timezone(
            timezone.localtime()
    ) - datetime.timedelta(days=360 * 3)):
        print(i)
        site_id.last_parsing = update_time_timezone(
            timezone.localtime()
        ) - datetime.timedelta(days=360 * 3)
        site_id.save(update_fields=["last_parsing"])


@app.task
def untaken_key():
    SiteKeyword.objects.filter(taken=1).update(taken=0)


#
# @app.task
# def activate_key():
#     SiteKeyword.objects.filter(is_active=0).update(is_active=1)
#

@app.task
def update_text_delete_duplicates():
    i = 0
    for site_id in SiteKeyword.objects.filter(site_id=11880147896115333104, last_parsing__gte=update_time_timezone(
            timezone.localtime()
    ) - datetime.timedelta(days=360 * 3)):
        print(i)
        site_id.last_parsing = update_time_timezone(
            timezone.localtime()
        ) - datetime.timedelta(days=360 * 3)
        site_id.save(update_fields=["last_parsing"])


@app.task
def update_key_pool():
    MAX_UPDATE_KEY = 300

    pool_source = ThreadPoolExecutor(15)
    futures = []
    select_sources = Sources.objects.filter(
        Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
        status=1)

    key_source = KeywordSource.objects.filter(source_id__in=list(select_sources.values_list('id', flat=True)))

    key_words = Keyword.objects.filter(network_id=1, enabled=1,
                                       id__in=list(key_source.values_list('keyword_id', flat=True))
                                       )

    site_key_words = SiteKeyword.objects.filter(taken=0, is_active=1,
                                                keyword_id__in=list(key_words.values_list('id', flat=True))
                                                ).order_by('last_parsing')[:MAX_UPDATE_KEY]
    for site_key_word in site_key_words:
        select_source = select_sources.get(
            id=key_source.filter(keyword_id=site_key_word.keyword_id).first().source_id)
        last_update = site_key_word.last_parsing
        if last_update < datetime.datetime(2001, 1, 1, 0, 0, tzinfo=UTC):
            # depth = key_word.depth
            retro_date = select_source.retro
            last_update = datetime.datetime(retro_date.year, retro_date.month, retro_date.day, 0, 0, tzinfo=UTC)
            time = select_source.sources
            if time is None:
                time = 10
            if last_update is None or (last_update + datetime.timedelta(minutes=time) <
                                       update_time_timezone(timezone.localtime())):
                site_key_word.taken = 1

    SiteKeyword.objects.bulk_update(site_key_words, fields=['taken'])
    for site_key_word in site_key_words:
        key_word = key_words.get(id=site_key_word.keyword_id)
        last_update = site_key_word.last_parsing
        futures.append(
            pool_source.submit(parsing_key, site_key_word, last_update, key_word.keyword))
    for future in concurrent.futures.as_completed(futures, timeout=300):
        print(future.result())
    print("stop update_key_pool")


@app.task
def task_parsing_key():
    pool_source = ThreadPoolExecutor(10)
    futures = []
    select_sources = Sources.objects.filter(
        Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
        status=1)

    key_source = KeywordSource.objects.filter(source_id__in=list(select_sources.values_list('id', flat=True)))

    key_words = Keyword.objects.filter(network_id=1, enabled=1,
                                       id__in=list(key_source.values_list('keyword_id', flat=True))
                                       )
    # site_key_words = SiteKeyword.objects.filter(site_id__in=[17097923825390536162, 14036259156137978615], taken=0, is_active=1,

    site_key_words = SiteKeyword.objects.filter(taken=0, is_active=1,
                                                # keyword_id__in=list(key_words.values_list('id', flat=True))
                                                ).exclude(site_id=1813906118771286836).order_by('last_parsing')
    iteration = 0
    MAX_SIZE_PARSE_BY_WORD = 10
    site_key_word = site_key_words.first()
    print(site_key_word.last_parsing)

    print(site_key_word.last_parsing)

    # for site_key_word in site_key_words:
    print("start")
    if True:
        # if iteration > MAX_SIZE_PARSE_BY_WORD or \
        #         SiteKeyword.objects.filter(taken=1).count() > MAX_SIZE_PARSE_BY_WORD * MAX_SIZE_PARSE_BY_WORD:
        #     break
        print("start1")

        if site_key_word is not None:
            print("start2")
            try:
                key_word = key_words.get(id=site_key_word.keyword_id)
            except Exception as e:
                site_key_word.is_active = 0
                site_key_word.last_parsing = update_time_timezone(timezone.localtime())

                site_key_word.save()
                return
            select_source = select_sources.get(
                id=key_source.filter(keyword_id=site_key_word.keyword_id).first().source_id)
            last_update = site_key_word.last_parsing
            if last_update < datetime.datetime(2001, 1, 1, 0, 0, tzinfo=UTC):
                # depth = key_word.depth
                retro_date = select_source.retro
                last_update = datetime.datetime(retro_date.year, retro_date.month, retro_date.day, 0, 0, tzinfo=UTC)
            time = select_source.sources
            print("start3")

            if time is None:
                time = 10
            if last_update is None or (last_update + datetime.timedelta(minutes=time) <
                                       update_time_timezone(timezone.localtime())):
                site_key_word.taken = 1
                site_key_word.save(update_fields=['taken'])
                print("start4")

                try:
                    print("parsing_key")
                    django.db.close_old_connections()

                    parsing_key(site_key_word, last_update, key_word.keyword)
                    # futures.append(
                    #     pool_source.submit(parsing_key, site_key_word, last_update, key_word.keyword))
                except Exception as e:
                    print(e)
                    site_key_word.taken = 0
                    site_key_word.save(update_fields=['taken'])

    # for future in concurrent.futures.as_completed(futures, timeout=30000):
    #     print(future.result())


def parsing_key(key_word, last_update, key):
    print(f"start parsing_key {key}")
    try:
        # https://www.radiorus.ru/
        if key_word.site_id == 5409945336605195500:
            print("radiorus")
            articles, proxy = parsing_radio_rus(key, last_update, update_proxy(None), [])
            print("radiorus ok")
        # https://vecherkaspb.ru
        elif key_word.site_id == 819475629408721317:
            print("vecherkaspb")
            articles, proxy = parsing_vecherkaspb(key, last_update, update_proxy(None), [])

        # https://gorod-812.ru
        elif key_word.site_id == 7881634854484899633:
            print("gorod-812")
            articles, proxy = parsing_gorod_812(key, last_update, update_proxy(None), [])

        # https://expertnw.com
        elif key_word.site_id == 3575266616937685158:
            print("expertnw")
            articles, proxy = parsing_expertnw(key, last_update, update_proxy(None), [])

        # https://www.5-tv.ru
        elif key_word.site_id == 15938616575921065567:
            print("www.5-tv")
            articles, proxy = parsing_5_tv(key, last_update, update_proxy(None), [])

        # https://echo.msk.ru
        elif key_word.site_id == 148582668151048074:
            print("echo.msk.")
            articles, proxy = parsing_echo_msk(key, last_update, update_proxy(None), [])

        # https://www.svoboda.org
        elif key_word.site_id == 9223372036854775807:
            print("svoboda")
            articles, proxy = parsing_svoboda_new(key, last_update, update_proxy(None), [])

        # https://moika78.ru
        elif key_word.site_id == 14576566779249943874:
            print("moika78")
            articles, proxy = parsing_moika78(key, last_update, update_proxy(None), [])

        # http://novayagazeta.spb.ru
        elif key_word.site_id == 14580193992243647856:
            print("novayagazeta")
            articles, proxy = parsing_novayagazeta(key, last_update, update_proxy(None), [])

        # https://www.interfax.ru
        elif key_word.site_id == 7686074743359215703:
            print("interfax")
            articles, proxy = parsing_interfax(key, last_update, update_proxy(None), [])

        # https://www.fontanka.ru
        elif key_word.site_id == 11880147896115333104:
            print("fontanka")
            articles, proxy = parsing_fontanka(key, last_update, update_proxy(None), [])

        # https://www.zaks.ru
        elif key_word.site_id == 8361677330337893298:
            print("zaks")
            articles, proxy = parsing_zaks(key, last_update, update_proxy(None), [])
        # https://www.vedomosti.ru/
        elif key_word.site_id == 1813906118771286836:
            print("vedomosti")
            return
        elif key_word.site_id == 7878146650456123781:
            print("tass")
            articles, proxy = parsing_tass(key, last_update, update_proxy(None), [])
        elif key_word.site_id == 14935787485712012734:
            print("tass")
            articles, proxy = parsing_thecitym24(key, last_update, update_proxy(None), [])

        else:
            print("site_id not founded")
            raise Exception("site_id not founded")
        stop_proxy(proxy)

        # TODO fix
        print("save")
        save_articles(key_word.site_id, articles)
        key_word.taken = 0
        key_word.last_parsing = update_time_timezone(timezone.localtime())
        key_word.save(update_fields=["taken", "last_parsing"])
    except Exception as e:
        print("Exception" + str(e))
        print("Exception" + str(key_word.site_id))

        # key_word.taken = 0
        key_word.is_active = 0
        key_word.save(update_fields=["taken"])
        print(e)





@app.task
def rabbit_mq():
    for i in range(50):
        create_rmq(i)


@app.task
def update_smi_new():
    print("start update_smi_new")
    pool_source = ThreadPoolExecutor(5)
    futures = []

    MAX_UPDATE_SITE = 10

    parsing_sites = ParsingSite.objects.filter(last_parsing__isnull=True, is_active=True, taken=False)[:MAX_UPDATE_SITE]
    if not parsing_sites:
        parsing_sites = ParsingSite.objects.filter(last_parsing__isnull=False, is_active=True, taken=False).order_by(
            "last_parsing")[:MAX_UPDATE_SITE]
    print("start parsing_site")
    print("len parsing_sites" + str(len(parsing_sites)))
    i= 0
    for parsing_site in parsing_sites:
        print(i)
        i += 1
        parsing_site.taken = True
    ParsingSite.objects.bulk_update(parsing_sites, fields=['taken'])

    for parsing_site in parsing_sites:
        print("start parse" + str(parsing_site.url))

        futures.append(pool_source.submit(update_smi_text, parsing_site))

    for future in concurrent.futures.as_completed(futures, timeout=300):
        print(future.result())
    print("stop update_smi_new")


def update_smi_text(parsing_site):
    try:
        i = 0
        MAX_UPDATE_POST = 50
        print("start update_smi_text")
        update_posts = Post.objects.filter(display_link=parsing_site.url, parsing=0).order_by("-created")[
                       :MAX_UPDATE_POST]

        print("queryset")
        print(update_posts.query)
        print("queryset ok")

        if len(update_posts) == 0:
            parsing_site.last_parsing = update_time_timezone(timezone.localtime()) + datetime.timedelta(minutes=3 * 60)
            parsing_site.taken = False
            parsing_site.save(update_fields=["taken", "last_parsing"])
        else:
            for update_post in update_posts:
                update_post.parsing = 1
            Post.objects.bulk_update(update_posts, fields=['parsing'])

            posts_content = []
            for update_post in update_posts:
                text = parsing_smi_url(update_post.link)
                if text is not None and text.strip() != "":
                    try:
                        i += 1
                        posts_content.append(
                            PostContent(
                                content=text,
                                cache_id=update_post.cache_id,
                                keyword_id=10000005,
                            )
                        )
                        update_post.parsing = 2
                    except Exception:
                        update_post.parsing = 0
                else:
                    update_post.parsing = 0
            try:
                PostContent.objects.bulk_create(posts_content, batch_size=batch_size, ignore_conflicts=True)
                Post.objects.bulk_update(update_posts, fields=['parsing'])
            except Exception as e:
                print("bulk_create and bulk_update" +str(e))
                for update_post in update_posts:
                    update_post.parsing = 0
                Post.objects.bulk_update(update_posts, fields=['parsing'])
        parsing_site.last_parsing = update_time_timezone(timezone.localtime())
        parsing_site.taken = False
        parsing_site.save(update_fields=["taken", "last_parsing"])
    except Exception as e:
        print("parsing_site" + str(e))
        parsing_site.taken = False
        parsing_site.save(update_fields=["taken"])


@app.task
def update_smi():
    parsing_site = ParsingSite.objects.filter(last_parsing__isnull=True, is_active=True, taken=False).first()
    if parsing_site is None:
        parsing_site = ParsingSite.objects.filter(last_parsing__isnull=False, is_active=True, taken=False).order_by(
            "-last_parsing").last()

    try:
        parsing_site.taken = True
        parsing_site.save(update_fields=["taken"])

        update_post = Post.objects.filter(display_link=parsing_site.url, parsing=0).order_by("created").last()
        if update_post is None:
            parsing_site.last_parsing = update_time_timezone(timezone.localtime()) + datetime.timedelta(minutes=3 * 60)
            parsing_site.taken = False
            parsing_site.save(update_fields=["taken", "last_parsing"])
        else:
            update_post.parsing = 1
            update_post.save(update_fields=["parsing"])

            text = parsing_smi_url(update_post.link)
            if text is not None and text.strip() != "":
                try:
                    PostContent.objects.create(
                        content=text,
                        cache_id=update_post.cache_id,
                        keyword_id=10000005,

                    )
                    update_post.parsing = 2
                    update_post.save(update_fields=["parsing"])
                except Exception:
                    update_post.parsing = 0
                    update_post.save(update_fields=["parsing"])
            else:
                update_post.parsing = 0
                update_post.save(update_fields=["parsing"])

            parsing_site.last_parsing = update_time_timezone(timezone.localtime())
            parsing_site.taken = False
            parsing_site.save(update_fields=["taken", "last_parsing"])
    except Exception:
        try:
            update_post.parsing = 0
            update_post.save(update_fields=["parsing"])
        except Exception:
            pass

        try:
            parsing_site.taken = False
            parsing_site.save(update_fields=["taken"])
        except Exception:
            pass


@app.task
def update_dp():
    i = 1
    for post in Post.objects.filter(display_link="https://www.dp.ru"):
        print("update_dp " + str(i))
        i += 1
        try:
            content_obj = PostContentGlobal.objects.get(cache_id=post.cache_id)
            content = content_obj.content
            content = content.replace(" <br> \n", "\r\n <br> ")
            content_obj.content = content
            content_obj.save(update_fields=["content"])
        except Exception as e:
            print("update_dp " + str(e))

            pass
    print("update_dp OK")


def reset_database_connection():
    from django import db
    db.close_connection()
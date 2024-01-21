import os
import datetime


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
            from core.models import GlobalSite
            from core.sites.utils import save_articles
            from core.sites.utils import update_time_timezone
            from core.sites.dp import parsing_dp, PAGE_URL as DP_URL
            from core.sites.gov_spb.pars_gov import start_parsing
            from core.sites.news_admin_petr import parsing_news_admin_petr
            from core.sites.news_spb import parsing_news_spb

            from core.sites.utils import update_proxy, stop_proxy, save_articles, update_time_timezone
            from core.sites.radio import parsing_radio, RADIO_URL
            from core.sites.radiozenit import parsing_radio_zenit, RADIO_URL as ZENIT_RADIO_URL
            from core.sites.spbdnevnik import parsing_spbdnevnik
            from core.sites.topspb import parsing_topspb
            from core.sites.metronews import parsing_metronews

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
                        elif site.url == ZENIT_RADIO_URL:
                            articles, proxy = parsing_radio_zenit(site.last_parsing, update_proxy(None), [])
                        elif site.url == "https://www.gov.spb.ru":
                            articles, proxy = start_parsing(site.last_parsing, update_proxy(None))
                        elif site.url == DP_URL:
                            articles, proxy = parsing_dp(site.last_parsing, update_proxy(None))
                        elif site.url == "http://xn--e1aqccgid7fsa.xn--p1ai/":
                            articles, proxy = parsing_news_admin_petr(site.last_parsing, update_proxy(None))
                            break
                        # htopspb
                        elif site.url == "https://tvspb.ru":
                            articles, proxy = parsing_topspb(site.last_parsing, update_proxy(None))
                        elif site.url == "https://spbdnevnik.ru":
                            articles, proxy = parsing_spbdnevnik(site.last_parsing, update_proxy(None))
                        elif site.url == "https://www.metronews.ru":
                            articles, proxy = parsing_metronews(site.last_parsing, update_proxy(None))

                        elif site.url in ['https://admnews.ru/',
                                        'https://krgv.ru/',
                                        'https://petrogradnews.ru/',
                                        'https://ksnews.ru/',
                                        'https://news-kron.ru/',
                                        'https://kurort-news.ru/',
                                        'https://mr-news.ru/',
                                        'https://nevnews.ru/',
                                        'https://pd-news.ru/',
                                        'https://primorsknews.ru/',
                                        'https://pushkin-news.ru/',
                                        'https://frunznews.ru/',
                                        'https://news-centre.ru/',
                                        'https://newskolpino.ru/',
                                        'https://kirnews.ru/',
                                        'https://kalininnews.ru/',
                                        'https://vybnews.ru/',
                                        'https://vonews.ru/'
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
        except Exception as e:
            print(f"Error {e}")
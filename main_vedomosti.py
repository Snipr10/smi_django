import threading
import multiprocessing
import time
import os
import random
import datetime
from datetime import timedelta


def new_process_vedomosti(i):
    for i in range(3):
        time.sleep(random.randint(1, 99))

        print(f"multiprocessing {i}")
        x = multiprocessing.Process(target=start_parsing_vedomosti, args=())
        x.start()


def start_parsing_vedomosti():
    print("start_parsing_account_source_while")
    while True:
        try:
            start_parsing_vedomosti_by_key()
        except Exception as e:
            print(e)
            time.sleep(5 * 60)


def start_parsing_vedomosti_by_key():
    from django.utils import timezone
    from core.models import SiteKeyword, Keyword
    from core.sites.vedomosti import parsing_vedomosti
    from core.sites.utils import save_articles
    from core.sites.utils import update_time_timezone

    site_keyword = SiteKeyword.objects.filter(taken=0, is_active=1, site_id=1813906118771286836).order_by("last_parsing").first()
    print(f"site_keyword {site_keyword.keyword_id}")
    site_keyword.taken = 1
    site_keyword.save(update_fields=['taken'])
    last_parsing = datetime.datetime(site_keyword.last_parsing.year, site_keyword.last_parsing.month, site_keyword.last_parsing.day) - timedelta(days=1)
    articles, proxy = parsing_vedomosti(Keyword.objects.get(id=site_keyword.keyword_id).keyword, last_parsing, None, [])
    save_articles(site_keyword.site_id, articles)
    site_keyword.taken = 0
    site_keyword.last_parsing = update_time_timezone(timezone.localtime())
    site_keyword.save(update_fields=["taken", "last_parsing"])
    print(f"site_keyword ok {site_keyword.keyword_id}")
    return


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument("-f", "--first",
                        action="store_true",
                        help="special mode")
    parser.add_argument("-s", "--second",
                        action="store_true",
                        help="special mode")
    parser.add_argument("-t", "--third",
                        action="store_true",
                        help="special mode")
    args = parser.parse_args()


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

    print(1)
    import django

    django.setup()

    while True:
        from django.utils import timezone
        from core.models import SiteKeyword, Keyword
        from core.sites.vedomosti import parsing_vedomosti
        from core.sites.utils import save_articles
        from core.sites.utils import update_time_timezone
        print("start")
        try:
            site_keywords = SiteKeyword.objects.filter(taken=0, is_active=1, site_id=1813906118771286836)
            site_keywords_len = len(site_keywords)
            active_keyword = Keyword.objects.filter(id__in=list(site_keywords.values_list('keyword_id', flat=True)),
                                                    network_id=1, disabled=0, enabled=1)

            if args.first:
                site_keywords = site_keywords[0:int(site_keywords_len/3) + 1]
            elif args.second:
                site_keywords = site_keywords[int(site_keywords_len/3)-1:int(site_keywords_len/3) +1]
            elif args.third:
                site_keywords = site_keywords[2+int(site_keywords_len/3) - 1:]

            for s in site_keywords:
                key = active_keyword.filter(id=s.keyword_id).last()
                if key is None:
                    continue
                s.taken = 1
                s.save(update_fields=['taken'])
                last_parsing = datetime.datetime(s.last_parsing.year, s.last_parsing.month,
                                                 s.last_parsing.day) - timedelta(days=1)
                articles, proxy = parsing_vedomosti(key.keyword,
                                                    last_parsing, None, [])
                save_articles(s.site_id, articles)
        except Exception as e:
            print(e)
        try:
            SiteKeyword.objects.filter(taken=1, site_id=1813906118771286836).update(taken=0)
        except Exception:
            pass
    # for i in range(2):
    #     time.sleep(10)
    #     print("thread new_process_vedomosti " + str(i))
    #     x = threading.Thread(target=new_process_vedomosti, args=(i,))
    #     x.start()

import os
import datetime
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
    import django.db
    from django.db.models import Q
    from pytz import UTC

    from django.utils import timezone
    from core.models import GlobalSite, SiteKeyword, Keyword, KeywordSource, Sources
    from core.sites.utils import save_articles
    from core.sites.utils import update_time_timezone
    from core.sites.dp import parsing_dp, PAGE_URL as DP_URL
    from core.sites.gov_spb.pars_gov import start_parsing
    from core.sites.news_admin_petr import parsing_news_admin_petr
    from core.sites.news_spb import parsing_news_spb

    from core.sites.utils import update_proxy, stop_proxy, save_articles, update_time_timezone
    from core.sites.radio import parsing_radio, RADIO_URL
    from core.sites.radiozenit import parsing_radio_zenit, RADIO_URL as ZENIT_RADIO_URL

    print(1)

    select_sources = Sources.objects.filter(
        Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
        status=1)
    print(2)

    key_source = KeywordSource.objects.filter(source_id__in=list(select_sources.values_list('id', flat=True)))
    print(3)

    key_words = Keyword.objects.filter()
    print(4)

    # site_key_words = SiteKeyword.objects.filter(site_id__in=[17097923825390536162, 14036259156137978615], taken=0, is_active=1,

    site_key_words = SiteKeyword.objects.filter(taken=0, is_active=1,
                                                # keyword_id__in=list(key_words.values_list('id', flat=True))
                                                ).exclude(site_id=1813906118771286836).order_by('last_parsing')
    print(5)

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

#
#     for k in [7881634854484899633,
# 1813906118771286836,
# 14576566779249943874,
# 7686074743359215703,
# 15938616575921065567,
# 14580193992243647856,
# 7878146650456123781,
# 148582668151048074,
# 819475629408721317,
# 3575266616937685158,
# 8361677330337893298,
# 14935787485712012734,
# 5409945336605195500,
# 11880147896115333104,
# 9223372036854775807]:
#         for w in [
# 295161,
# 2086362,
# 8793343,
# 8793348,
# 10536336,
# 10536337,
# 10537310,
# 10537315,
# 10538524,
# 10538529,
# 10538544,
# 10538545,
# 10538550,
# 10538551,
# 10550735,
# 10550735,
# 10550740,
# 10550740,
# 10550778,
# 10550779,
# 10550861,
# 10550862,
# 10550863,
# 10550864,
# 10550865,
# 10550866,
# 10550867,
# 10550868,
# 10550869,
# ]:
#             try:
#                 SiteKeyword.objects.create(site_id=k, keyword_id=w)
#             except Exception as e:
#                 print(e)

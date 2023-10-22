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
    import django.db

    from django.utils import timezone
    from core.models import GlobalSite, SiteKeyword
    from core.sites.utils import save_articles
    from core.sites.utils import update_time_timezone
    from core.sites.dp import parsing_dp, PAGE_URL as DP_URL
    from core.sites.gov_spb.pars_gov import start_parsing
    from core.sites.news_admin_petr import parsing_news_admin_petr
    from core.sites.news_spb import parsing_news_spb

    from core.sites.utils import update_proxy, stop_proxy, save_articles, update_time_timezone
    from core.sites.radio import parsing_radio, RADIO_URL
    from core.sites.radiozenit import parsing_radio_zenit, RADIO_URL as ZENIT_RADIO_URL

    for k in [7881634854484899633,
1813906118771286836,
14576566779249943874,
7686074743359215703,
15938616575921065567,
14580193992243647856,
7878146650456123781,
148582668151048074,
819475629408721317,
3575266616937685158,
8361677330337893298,
14935787485712012734,
5409945336605195500,
11880147896115333104,
9223372036854775807]:
        for w in [
295161,
2086362,
8793343,
8793348,
10536336,
10536337,
10537310,
10537315,
10538524,
10538529,
10538544,
10538545,
10538550,
10538551,
10550735,
10550735,
10550740,
10550740,
10550778,
10550779,
10550861,
10550862,
10550863,
10550864,
10550865,
10550866,
10550867,
10550868,
10550869,
]:
            try:
                SiteKeyword.objects.create(site_id=k, keyword_id=w)
            except Exception as e:
                print(e)

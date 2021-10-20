from datetime import datetime

from core.sites.gov_spb.government import parsing_gov_government
from core.sites.gov_spb.government_meeting import parsing_gov_government_meeting
from core.sites.gov_spb.governor import parsing_gov_governor
from core.sites.gov_spb.governor_agency import parsing_gov_agency
from core.sites.gov_spb.governor_announces import parsing_gov_announces
from core.sites.gov_spb.governor_disproof import parsing_governor_disproof


def start_parsing(limit_date, proxy):
    all_articles = []
    is_ok, articles, proxy = parsing_gov_government(limit_date, proxy)
    if not is_ok:
        print("can not parse parsing_gov_government")
        raise Exception("can not parse parsing_gov_government")
    all_articles.extend(articles)

    is_ok, articles, proxy = parsing_gov_governor(limit_date, proxy)
    if not is_ok:
        print("can not parse parsing_gov_governor")
        raise Exception("can not parse parsing_gov_governor")
    all_articles.extend(articles)

    is_ok, articles, proxy = parsing_gov_government_meeting(limit_date, proxy)
    if not is_ok:
        print("can not parse parsing_gov_government_meeting")
        raise Exception("can not parse parsing_gov_government_meeting")

    all_articles.extend(articles)

    is_ok, articles, proxy = parsing_gov_agency(limit_date, proxy)
    if not is_ok:
        print("can not parse parsing_gov_agency")
        raise Exception("can not parse parsing_gov_agency")

    all_articles.extend(articles)

    is_ok, articles, proxy = parsing_gov_announces(limit_date, proxy)
    if not is_ok:
        print("can not parse parsing_gov_announces")
        raise Exception("can not parse parsing_gov_announces")

    all_articles.extend(articles)

    is_ok, articles, proxy = parsing_governor_disproof(limit_date, proxy)
    if not is_ok:
        print("can not parse parsing_governor_disproof")
        raise Exception("can not parse parsing_governor_disproof")

    all_articles.extend(articles)
    print("gov parsing stop")
    return all_articles, proxy


if __name__ == '__main__':
    start_parsing(datetime.strptime("1/10/2021", "%d/%m/%Y"), None)
    print(1)
from datetime import datetime

from core.sites.gov_spb.government import parsing_gov_government
from core.sites.gov_spb.government_meeting import parsing_gov_government_meeting
from core.sites.gov_spb.governor import parsing_gov_governor
from core.sites.gov_spb.governor_agency import parsing_gov_agency
from core.sites.gov_spb.governor_announces import parsing_gov_announces
from core.sites.gov_spb.governor_disproof import parsing_governor_disproof
from core.sites.gov_spb.governor_ter import parsing_governor_ter


def start_parsing(limit_date, proxy):
    all_articles = []
    max_limit = 100

    limit = 0
    while limit < max_limit:
        is_ok, articles, proxy = parsing_governor_ter(limit_date, proxy)

        if is_ok:
            all_articles.extend(articles)
            limit = 2 * max_limit
        else:
            limit += 1
            if limit >= max_limit:
                print("can not parse parsing_governor_ter")
                raise Exception("can not parse parsing_governor_ter")

    limit = 0
    while limit < max_limit:
        is_ok, articles, proxy = parsing_gov_government(limit_date, proxy)
        if is_ok:
            all_articles.extend(articles)
            limit = 2 * max_limit
        else:
            limit += 1
            if limit >= max_limit:
                print("can not parse parsing_gov_government")
                raise Exception("can not parse parsing_gov_government")

    limit = 0
    while limit < max_limit:
        is_ok, articles, proxy = parsing_gov_governor(limit_date, proxy)

        if is_ok:
            all_articles.extend(articles)
            limit = 2 * max_limit
        else:
            limit += 1
            if limit >= max_limit:
                print("can not parse parsing_gov_governor")
                raise Exception("can not parse parsing_gov_governor")

    limit = 0
    while limit < max_limit:
        is_ok, articles, proxy = parsing_gov_government_meeting(limit_date, proxy)

        if is_ok:
            all_articles.extend(articles)
            limit = 2 * max_limit
        else:
            limit += 1
            if limit >= max_limit:
                print("can not parse parsing_gov_government_meeting")
                raise Exception("can not parse parsing_gov_government_meeting")

    limit = 0
    while limit < max_limit:
        is_ok, articles, proxy = parsing_gov_agency(limit_date, proxy)

        if is_ok:
            all_articles.extend(articles)
            limit = 2 * max_limit
        else:
            limit += 1
            if limit >= max_limit:
                print("can not parse parsing_gov_agency")
                raise Exception("can not parse parsing_gov_agency")

    limit = 0
    while limit < max_limit:
        is_ok, articles, proxy = parsing_gov_announces(limit_date, proxy)

        if is_ok:
            all_articles.extend(articles)
            limit = 2 * max_limit
        else:
            limit += 1
            if limit >= max_limit:
                print("can not parse parsing_gov_announces")
                raise Exception("can not parse parsing_gov_announces")

    limit = 0
    while limit < max_limit:
        is_ok, articles, proxy = parsing_governor_disproof(limit_date, proxy)

        if is_ok:
            all_articles.extend(articles)
            limit = 2 * max_limit
        else:
            limit += 1
            if limit >= max_limit:
                print("can not parse parsing_governor_disproof")
                raise Exception("can not parse parsing_governor_disproof")

    print("gov parsing stop")
    return all_articles, proxy


if __name__ == '__main__':
    start_parsing(datetime.strptime("20/08/2022", "%d/%m/%Y"), None)
    print(1)
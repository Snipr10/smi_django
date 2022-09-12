from core.sites.gov_spb.governor_ter import parsing_governor_region

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://www.gov.spb.ru/press/disproof/?page=%s"
PAGE_URL = "https://www.gov.spb.ru"

OTRSL = ['https://www.gov.spb.ru/gov/otrasl/archiv_kom/news/',
        'https://www.gov.spb.ru/gov/otrasl/gilfond/news/',
        'https://www.gov.spb.ru/gov/otrasl/fin_kontrol/news/',
        'https://www.gov.spb.ru/gov/otrasl/kio/news/',
        'https://www.gov.spb.ru/gov/otrasl/blago/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_foreign/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_zakonnost/news/',
        'https://www.gov.spb.ru/gov/otrasl/kgz/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_govcontrol/news/',
        'https://www.gov.spb.ru/gov/otrasl/architecture/news/',
        'https://www.gov.spb.ru/gov/otrasl/zags/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_health/news/',
        'https://www.gov.spb.ru/gov/otrasl/invest/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_information/news/',
        'https://www.gov.spb.ru/gov/otrasl/kki/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_culture/news/',
        'https://www.gov.spb.ru/gov/otrasl/kmormp/news/',
        'https://www.gov.spb.ru/gov/otrasl/kpmp/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_science/news/',
        'https://www.gov.spb.ru/gov/otrasl/educ/news/',
        'https://www.gov.spb.ru/gov/otrasl/press/news/',
        'https://www.gov.spb.ru/gov/otrasl/ecology/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_industrial_and_trade/news/',
        'https://www.gov.spb.ru/gov/otrasl/tr_infr_kom/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_tourism/news/',
        'https://www.gov.spb.ru/gov/otrasl/trud/news/',
        'https://www.gov.spb.ru/gov/otrasl/komstroy/news/',
        'https://www.gov.spb.ru/gov/otrasl/energ_kom/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_transport/news/',
        'https://www.gov.spb.ru/gov/otrasl/kom_zan/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_physic/news/',
        'https://www.gov.spb.ru/gov/otrasl/c_econom/news/',
        'https://www.gov.spb.ru/gov/otrasl/ingen/news/',
        'https://www.gov.spb.ru/gov/otrasl/arkt/news/',
        'https://www.gov.spb.ru/gov/otrasl/ktr/news/',
        'https://www.gov.spb.ru/gov/otrasl/finance/news/'
        'https://www.gov.spb.ru/gov/otrasl/socpit/news/',
        'https://www.gov.spb.ru/gov/otrasl/sadovod/news/',
        'https://www.gov.spb.ru/gov/otrasl/veter/news/',
        'https://www.gov.spb.ru/gov/otrasl/inspek/news/',
        'https://www.gov.spb.ru/gov/otrasl/slujba/news/',
        'https://www.gov.spb.ru/gov/otrasl/sl_nadzora/news/',
        'https://www.gov.spb.ru/gov/otrasl/inspekcija/news/',
]


def parsing_governor_otrsl(limit_date, proxy):
    all_articles = []
    is_oks = []
    for region in OTRSL:
        is_ok, articles, proxy = parsing_governor_region(region, limit_date, proxy)
        all_articles.extend(articles)
        is_oks.append(is_ok)
    return all(is_oks), all_articles, proxy

import dateparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from core.sites.utils import stop_proxy, update_proxy, DEFAULTS_TIMEOUT

SEARCH_PAGE_URL = "https://spbdnevnik.ru/finder"

HEADERS = {
    'authority': 'spbdnevnik.ru',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'dnt': '1',
    'referer': 'https://spbdnevnik.ru/finder',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36'
}

USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36'


def parsing_spbdnevnik(limit_date, proxy):
    print("spbdnevnik")
    print(limit_date)
    # first_request
    articles = []
    page = 0
    body = []
    is_parsing_url = True
    while page < 500 and is_parsing_url:
        is_parsing_url, body, proxy = get_urls(limit_date, proxy, body, page)
        page += 1
        print("spbdnevnik page" + str(page))

    i = 0
    for article in body:
        print("spbdnevnik " + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(limit_date, proxy, body, page, attempts=0):
    try:
        # ?SearchString=&skip=0&take=10&DateFrom=&DateTo=&IsInIssue=false&SortType=2&SortOrder=1"
        if attempts == 0:
            res = requests.get(SEARCH_PAGE_URL,
                               headers=HEADERS,
                               params={"page": page,
                                       "ajax": "",
                                       },
                               # proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
        else:
            res = requests.get(SEARCH_PAGE_URL,
                               headers=HEADERS,
                               params={"page": page,
                                       "ajax": "",
                                       },
                               proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
    except Exception as e:
        stop_proxy(proxy)
        # logger.info(str(e))
        if attempts < 10:
            return get_urls(limit_date, update_proxy(proxy), body, page, attempts + 1)
        return False, body, proxy
    if res.ok:

        for new in res.json().get("articles").get("data"):
            try:
                site_date = dateparser.parse(new.get("published_at"))
            except Exception:
                site_date = None
            print(site_date)

            body.append({
                "title": new['title'],
                "href": new['full_url'],
                "date": site_date,
                "text": new['text'] + "\r\n <br> "
            })
            if site_date and site_date.date() < limit_date.date():
                return False, body, proxy
        return True, body, proxy

    elif res.status_code == 404:
        return False, body, None, proxy
    return True, body, proxy


def get_page(articles, article_body, proxy, attempt=0):
    photos = []
    sounds = []
    videos = []
    try:
        url = article_body['href']
        if attempt == 0:

            res = requests.get(url, headers={
                "user-agent": USER_AGENT
            },
                               # proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
        else:
            res = requests.get(url, headers={
                "user-agent": USER_AGENT
            },
                               proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
        if res.ok:
            soup = BeautifulSoup(res.text)
            text = article_body['text']

            try:
                text = soup.find("div", {"class": "news-full--element-text"}).text.strip()
            except Exception:
                pass
            try:
                for img in soup.find("div", {"class": "news-full--element-image"}).find_all("img"):
                    photos.append(img.attrs.get("src", ""))
            except Exception:
                pass

            articles.append(
                {"date": article_body['date'],
                 "title": article_body['title'],
                 "text": text.strip(),
                 "photos": photos,
                 "href": url,
                 })

            return False, articles, proxy
        return False, articles, proxy
    except Exception as e:
        stop_proxy(proxy)
        if attempt > 2:
            return False, articles, proxy
        return get_page(articles, article_body, update_proxy(proxy), attempt + 1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    a, b = parsing_spbdnevnik(datetime.strptime("18/01/2024", "%d/%m/%Y"), None)
    print(a)

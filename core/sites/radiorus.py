from datetime import datetime

import requests
from bs4 import BeautifulSoup

from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://www.radiorus.ru/search/json"
PAGE_URL = "https://www.radiorus.ru/"


# logger = get_logger(__name__)


def parsing_radio_rus(keyword, limit_date, proxy, body):
    is_not_stopped, body, is_time, proxy = get_urls(keyword, limit_date, proxy, [], 0)
    articles = []
    for article in body:
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_page(articles, article_body, proxy, attempt=0):
    photos = []
    sounds = []
    videos = []
    try:
        res = requests.get(PAGE_URL + article_body['href'], headers={
            "user-agent": USER_AGENT
        },
            proxies=proxy.get(list(proxy.keys())[0]),
            timeout=DEFAULTS_TIMEOUT
        )
        if res.ok:
            soup = BeautifulSoup(res.text)
            text = soup.find("p", {"class": "anons"}).text
            text_body = soup.find("p", {"align": "justify"})

            if text_body is not None:
                text += "\n" + text_body.text

            try:
                for img in soup.find("div", {"class": "brand-episode__body"}).find_all("img"):
                    try:
                        photos.append(img.attrs["src"])
                    except Exception:
                        pass
            except Exception:
                pass
            articles.append({"date": article_body['date'], "title": article_body['title'], "text": text.replace(" ", " ").strip(),
                             "href": PAGE_URL + article_body['href'],
                             "photos": photos,
                             "sounds": sounds,
                             "videos": videos
                             })

            return False, articles, proxy
        return False, articles, proxy
    except Exception:
        if attempt > 2:
            return False, articles, proxy
        return get_page(articles, article_body, update_proxy(proxy), attempt+1)


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    try:
        res = requests.get(SEARCH_PAGE_URL,
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={"type": "episodes", "offset": page, "q": keyword},
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )

    except Exception as e:
        # logger.info(str(e))
        if attempts < 10:
            return get_urls(keyword, limit_date, update_proxy(proxy), body, page, attempts + 1)
        return False, body, False, proxy
    if res.ok:
        data = res.json().get("data", [])
        if len(data) == 0:
            return True, body, False, proxy
        for article in res.json().get("data", []):
            article_date = datetime.strptime(article.get("date"), "%d-%m-%Y %H:%M:%S")
            # if article_date.date() < limit_date.date():
            #     return True, body, True, proxy
            if page > 100:
                return True, body, True, proxy
            if article_date.date() >= limit_date.date():
                body.append(
                    {
                        "href": f"brand/{article.get('brands')[0].get('id')}/episode/{article.get('id')}",
                        "date": article_date,
                        "title": article.get("title")
                    }
                )
        return get_urls(keyword, limit_date, update_proxy(proxy), body, page + 1, attempts)
    elif res.status_code == 404:
        return False, body, False, proxy
    return False, body, False, proxy


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parsing_radio_rus("spb", datetime.strptime("01/01/2000", "%d/%m/%Y"), None, [])

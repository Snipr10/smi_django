from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://smotrim.ru/api/search-articles"
PAGE_URL = "https://smotrim.ru"


# logger = get_logger(__name__)


def parsing_radio_rus(keyword, limit_date, proxy, body):
    print("parsing_radio_rus")
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
            text = soup.find("div", {"class": "article__anons"}).text
            text_body = soup.find("div", {"align": "article__body"})

            if text_body is not None:
                text += "\r\n <br> " + text_body.text

            try:
                for img in soup.find("div", {"class": "media__picture"}).find_all("img"):
                    try:
                        photos.append(img.attrs["data-src"])
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                for v in soup.find("div", {"class": "media__video"}).find_all("iframe"):
                    try:
                        videos.append(v.attrs["src"])
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
    print(f"get_urls {page}")

    try:
        res = requests.get(SEARCH_PAGE_URL,
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={"page": page, "q": keyword},
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
            try:
                try:
                    article_date = parse(article.get("date"))
                except Exception as e:
                    article_date = datetime.today()

                # if article_date.date() < limit_date.date():
                #     return True, body, True, proxy
                if page > 100000:
                    return True, body, True, proxy
                if article_date.date() >= limit_date.date():
                    body.append(
                        {
                            "href": article['url'],
                            "date": article_date,
                            "title": article.get("title")
                        }
                    )
            except Exception:
                pass
        return get_urls(keyword, limit_date, proxy, body, page + 1, attempts)
    elif res.status_code == 404:
        return False, body, False, proxy
    return False, body, False, proxy


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parsing_radio_rus("москва", datetime.strptime("01/01/2000", "%d/%m/%Y"), None, [])

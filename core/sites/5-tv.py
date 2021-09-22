from datetime import datetime

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT



USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://www.5-tv.ru/search/"
PAGE_URL = ""


# logger = get_logger(__name__)


def parsing_5_tv(keyword, limit_date, proxy, body):
    is_not_stopped, body, is_time, proxy = get_urls(keyword, limit_date, proxy, [], 0)
    articles = []
    for article in body:
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_page(articles, article_body, proxy):
    photos = []
    sounds = []
    videos = []
    try:
        res = requests.get(article_body['href'], headers={
            "user-agent": USER_AGENT
        },
            proxies=proxy.get(list(proxy.keys())[0]),
            timeout=DEFAULTS_TIMEOUT
        )
        if res.ok:
            soup = BeautifulSoup(res.text)
            container = _get_class_container(soup)
            title = container.find("h1", {"class": "fsHeader1Alt"}).text
            text = container.find("p", {"class": "fsHeaderAlt"}).text
            p_text_body = container.find("div", {"class": "marginRightCol fsBig"}).find_all("p")

            for text_body in p_text_body:
                if "subscript" not in text_body.attrs.get('class', []):
                    text += "\n" + text_body.text

            try:
                for img in container.find_all("img", {"class": "displayBlock"}):
                    try:
                        photos.append(img.attrs["src"])
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                for video in container.find_all("video"):
                    try:
                        videos.append(video.attrs["poster"])
                    except Exception:
                        pass
            except Exception:
                pass
            articles.append({"date": article_body['date'], "title": title, "text": text.strip(),
                             "href": PAGE_URL + article_body['href'],
                             "photos": photos,
                             "sounds": sounds,
                             "videos": videos
                             })

            return False, articles, proxy
        return False, articles, proxy
    except Exception:
        return get_page(articles, article_body, update_proxy(proxy))


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    try:
        res = requests.get(SEARCH_PAGE_URL,
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={"n": 1, "q": keyword, "sort": "date", "page": page},
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )

    except Exception as e:
        # logger.info(str(e))
        if attempts < 10:
            return get_urls(keyword, limit_date, update_proxy(proxy), body, page, attempts + 1)
        return False, body, False, proxy
    if res.ok:
        soup = BeautifulSoup(res.text)
        article_col3 = _get_class_container(soup).find_all("div", {"class": "col3"})
        if len(article_col3) == 0:
            return True, body, False, proxy
        for article in article_col3:
            article_date = dateparser.parse(article.text.strip())
            if article_date.date() < limit_date.date():
                return True, body, True, proxy
            if page > 100:
                return True, body, True, proxy
            if article_date.date() >= limit_date.date():
                body.append(
                    {
                        "href": article.find("a").attrs.get("href"),
                        "date": article_date,
                    }
                )
        return get_urls(keyword, limit_date, update_proxy(proxy), body, page + 1, attempts)
    elif res.status_code == 404:
        return False, body, False, proxy
    return False, body, False, proxy


def _get_class_container(soup):
    return soup.find("main", {"class": "main"}).find("div", {"class": "container"})


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parsing_5_tv("spb", datetime.strptime("01/01/2000", "%d/%m/%Y"), None, [])

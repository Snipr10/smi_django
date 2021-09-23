# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# radio
import re
from datetime import datetime

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import update_proxy, parse_date, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://www.svoboda.org/s"
RADIO_URL = "https://www.svoboda.org"
RADIO_PAGE_URL = "https://www.svoboda.org/news?p=%s"


# logger = get_logger(__name__)


def parsing_svoboda_new(keyword, limit_date, proxy, body):
    is_not_stopped, body, is_time, proxy = get_urls(keyword, limit_date, proxy, [], 1)
    articles = []
    for article in body:
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_page(articles, article_body, proxy, attempt=0):
    text = ""
    videos = []
    photos = []
    sounds = []

    try:
        res = requests.get(RADIO_URL + article_body['href'], headers={
            "user-agent": USER_AGENT,
        },
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT)
        if res.ok:
            soup = BeautifulSoup(res.text)
            title = soup.find("h1", {"class": "title pg-title"}).text.strip()
            body_texts = soup.find("div", {"class": "body-container"}).find_all("p")
            for body_text in body_texts:
                text += body_text.text
            for cover_media in soup.find_all("div", {"class": "img-wrap"}):
                try:
                    photos.append(cover_media.find("img").attrs['src'])
                except Exception:
                    pass
            for cover_media in soup.find_all("div", {"class": "wsw__embed"}):
                try:
                    img = cover_media.find("img")
                    if img.get("class") is None:
                        photo = img.attrs['src']
                        if photo not in photos:
                            photos.append(photo)
                except Exception:
                    pass

            for video in soup.find_all(text=re.compile("renderExternalContent")):
                try:
                    videos.append(str(video).replace("renderExternalContent(\"", "").replace("\")", ""))
                except Exception:
                    pass
            articles.append({"date": article_body["date"], "title": title, "text": text, "videos": videos,
                             "href": RADIO_URL + article_body['href'],
                             "photos": photos,
                             "sounds": sounds
                             })
            return False, articles, proxy
        return True, articles, proxy
    except Exception as e:
        if attempt > 5:
            return False, articles, proxy
        return get_page(articles, article_body, update_proxy(proxy), attempt+1)


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    try:
        res = requests.get(SEARCH_PAGE_URL, headers={
            "user-agent": USER_AGENT
        },
                           params={
                               "k": keyword,
                               "tab": "all",
                               "pi": page,
                               "r": "all",
                               "pp": 50
                                   },

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
        tables = soup.find_all("div", {"class": "media-block"})
        if len(tables) == 0:
            return False, body, False, proxy
        for table in tables:
            article_date = dateparser.parse(table.find("span", {"class": re.compile("^date date")}).text)
            if article_date.date() < limit_date.date():
                return True, body, True, proxy
            if page > 100:
                return True, body, True, proxy
            if article_date.date() >= limit_date.date():
                body.append(
                    {
                        "href":  table.find("a", {"href": re.compile("^/a/")}).attrs["href"],
                        "date": article_date,
                    }
                )
        return get_urls(keyword, limit_date, update_proxy(proxy), body, page + 1, attempts)
    elif res.status_code == 404:
        return False, body, False, proxy
    return False, body, False, proxy


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_svoboda_new("sms", datetime.strptime("01/01/2021", "%d/%m/%Y"), update_proxy(None), [])
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

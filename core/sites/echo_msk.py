# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# radio
from datetime import datetime

import dateparser
import requests
from bs4 import BeautifulSoup, NavigableString

from core.sites.utils import update_proxy, parse_date, DEFAULTS_TIMEOUT


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://echo.msk.ru/search/"
RADIO_URL = "https://echo.msk.ru"


# logger = get_logger(__name__)


def parsing_echo_msk(keyword, limit_date, proxy, body):
    is_not_stopped, body, is_time, proxy = get_urls(keyword, limit_date, proxy, [], 1)
    articles = []
    for article in body:
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_page(articles, article_body, proxy):
    text = ""
    photos = []
    videos = []
    sounds = []
    try:
        res = requests.get(RADIO_URL + article_body['href'], headers={
            "user-agent": USER_AGENT
        },
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )
        if res.ok:
            soup = BeautifulSoup(res.text)
            if "/news/" in article_body['href']:
                title = soup.find("h1", {"itemprop": "headline"}).text.strip()
                for body_text in soup.find("div", {"itemprop": "articleBody"}).find_all("p"):
                    text += body_text.text.strip()
            else:
                try:
                    try:
                        title = soup.find("h1", {"itemprop": "headline"}).text.strip()
                    except Exception:
                        title = soup.find("a", {"class": "name_prog red"}).text.strip()
                    try:
                        text = soup.find("div", {"class": "typical"}).text.strip()
                    except Exception:
                        pass
                    try:
                        sounds.append(RADIO_URL + soup.find("a", {"class": "load iblock"}).attrs['href'])
                    except Exception:
                        pass
                except Exception:
                    return False, articles, proxy
            try:
                videos.append(soup.find("iframe", {
                    "allow": "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"}).attrs[
                                  'src'])
            except Exception:
                pass
            try:
                for img in soup.find("div", {"itemprop": "articleBody"}).find_all("img"):
                    photos.append("https:"+img.attrs.get("src", ""))
            except Exception:
                pass
            articles.append({"date": article_body['date'], "title": title, "text": text,
                             "href": RADIO_URL + article_body['href'],
                             "photos": photos,
                             "sounds": sounds,
                             "videos": videos
                             })
            return False, articles, proxy
        return True, articles, proxy
    except Exception:
        return get_page(articles, article_body, update_proxy(proxy))


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    try:
        res = requests.get(SEARCH_PAGE_URL,
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={
                               "search_cond[page]": "",
                               "search_cond[published]": "1",
                               "search_cond[query]": keyword,
                               "search_cond[type_string]": "news",
                               "search_cond[when]": "all",
                               "search_cond[search_elements]": "true",
                               "page": page
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
        try:
            results = soup.find("div", {"class": "search_result_list"}).find_all("div", {"class": "res_block"})
        except Exception:
            results = []
        if len(results) == 0:
            return True, body, False, proxy
        for article in results:
            article_date = dateparser.parse(article.find("span", {"class": "date"}).text.strip())
            if article_date.date() < limit_date.date():
                return True, body, True, proxy
            if page > 100:
                return True, body, True, proxy
            if article_date.date() >= limit_date.date():
                body.append(
                    {
                        "href": article.find("a", {"class": "black"}).attrs.get("href"),
                        "date": article_date,
                    }
                )
        return get_urls(keyword, limit_date, update_proxy(proxy), body, page + 1, attempts)
    elif res.status_code == 404:
        return False, body, False, proxy
    return False, body, False, proxy

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_echo_msk(datetime.strptime("21/07/2021", "%d/%m/%Y"), update_proxy(None))
    print(1)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

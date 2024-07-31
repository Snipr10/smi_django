import re
from datetime import datetime
import json

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import stop_proxy, update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://piter-news.net/all"
PAGE_URL = "https://www.dp.ru"


def parsing_news_myseldon(limit_date, proxy):
    print("parsing_news_myseldon")
    print(limit_date)
    # first_request
    articles = []
    page = 0
    body = []
    is_parsing_url = True

    while page < 1 and is_parsing_url:
        is_parsing_url, body, proxy = get_urls(limit_date, proxy, body, page)
        page += 1
        print("parsing_news_myseldon page" + str(page))

    i = 0
    for article in body:
        print("parsing_news_myseldon " + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(limit_date, proxy, body, page, attempts=0):
    try:
        if attempts == 0:
            res = requests.get(
                f"https://news.myseldon.com/api/Section?utf8=%E2%9C%93&rubricId=4&pageSize=18&pageIndex={page}&requestId=ce128805-9fdd-4678-b835-56c1a328be78&orderBy=1&inTitle=false&articles=false",
                headers={
                    "user-agent": USER_AGENT
                },
                timeout=DEFAULTS_TIMEOUT
                )
        else:
            res = requests.get(
                f"https://news.myseldon.com/api/Section?utf8=%E2%9C%93&rubricId=4&pageSize=18&pageIndex={page}&requestId=ce128805-9fdd-4678-b835-56c1a328be78&orderBy=1&inTitle=false&articles=false",
                headers={
                    "user-agent": USER_AGENT
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

        for new in res.json().get("news", []):
            site_date = None
            try:
                site_date = dateparser.parse(new.get("date"))
                body.append({
                    "title": new.get("title"),
                    "href": f"https://news.myseldon.com/ru/news/index/{new.get('''newsId''')}",
                    "date": site_date
                })
            except Exception:
                pass

            if site_date and site_date.date() < limit_date.date():
                return False, body, proxy
        return True, body, proxy

    elif res.status_code == 404:
        return False, body, proxy
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
            soup_all = BeautifulSoup(res.text)
            text = ""
            try:
                for d in soup_all.find("div", {"class": "article"}).find_all("div"):
                    text += d.text
                    text += "\r\n <br> "
            except Exception:
                text = soup_all.find("div", {"itemprop": "articleBody"}).text
            try:
                for img in soup_all.find("div", {"class": "article"}).find_all("img"):
                    try:
                        photos.append(img.get("src"))
                    except:
                        pass
            except Exception:
                pass

            articles.append(
                {"date": article_body['date'],
                 "title": article_body['title'],
                 "text": text,
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
    articles, proxy = parsing_news_myseldon(datetime.strptime("15/06/2024", "%d/%m/%Y"), None)
    print(1)

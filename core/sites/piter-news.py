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


def parsing_piter_news(limit_date, proxy):
    print("parsing_dp")
    print(limit_date)
    # first_request
    articles = []
    page = 0
    body = []
    is_parsing_url = True
    id_ = None
    while page < 50 and is_parsing_url:
        is_parsing_url, body, proxy, id_ = get_urls(limit_date, proxy, body, id_)
        page += 1
        print("parsing_dp page" + str(page))
        if id_ is None:
            break
    i = 0
    for article in body:
        print("parsing_dp " + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(limit_date, proxy, body, id_, attempts=0):
    try:
        if id_:
            if attempts == 0:
                res = requests.get("https://piter-news.net/api/cat",
                                   headers={
                                       "user-agent": USER_AGENT
                                   },
                                   params={"type": "all", "id": id_},
                                   timeout=DEFAULTS_TIMEOUT
                                   )
            else:
                res = requests.get("https://piter-news.net/api/cat",
                                   headers={
                                       "user-agent": USER_AGENT
                                   },
                                   params={"type": "all", "id": id_},
                                   proxies=proxy.get(list(proxy.keys())[0]),
                                   timeout=DEFAULTS_TIMEOUT
                                   )

        else:
            if attempts == 0:
                res = requests.get(SEARCH_PAGE_URL,
                                   headers={
                                       "user-agent": USER_AGENT
                                   },

                                   timeout=DEFAULTS_TIMEOUT
                                   )
            else:
                res = requests.get(SEARCH_PAGE_URL,
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
            return get_urls(limit_date, update_proxy(proxy), body, id_, attempts + 1)
        return False, body, proxy, id_
    if res.ok:
        soup_all = BeautifulSoup(res.text)
        try:
            id_ = soup_all.find("ul", {"data-name": "all"}).get("data-id")
        except:
            id_ = soup_all.text.split("=")[-1]

        for site in soup_all.find_all("div", {"class":"post-info"}):
            site_date = None
            try:
                title_div = site.find("div", {"class": "post_title"})
                site_date = dateparser.parse(site.find("noindex").text)
                body.append({
                    "title": title_div.text,
                    "href": title_div.find("a").get("href"),
                    "date": site_date
                })
            except Exception:
                pass

            if site_date and site_date.date() < limit_date.date():
                return False, body, proxy, id_
        return True, body, proxy, id_

    elif res.status_code == 404:
        return False, body, proxy, id_
    return True, body, proxy, id_


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

            soup = soup_all.find("div", {"itemprop": "articleBody"})

            try:
                for img in soup.find_all("div", {"itemprop": "image"}):
                    try:
                        photos.append(img.find("a").get("href"))
                    except:
                        pass
            except Exception:
                pass

            articles.append(
                {"date": article_body['date'],
                 "title": article_body['title'],
                 "text": soup.text.strip(),
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
    articles, proxy = parsing_piter_news(datetime.strptime("15/06/2024", "%d/%m/%Y"), None)
    print(1)

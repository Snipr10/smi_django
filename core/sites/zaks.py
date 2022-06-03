import re

import dateparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://www.zaks.ru/new/search.php"
PAGE_URL = "https://www.zaks.ru"


def parsing_zaks(keyword, limit_date, proxy, body):
    is_not_stopped, body, is_time, proxy = get_urls(keyword, limit_date, proxy, body, 1)
    articles = []
    i = 0
    print("parsing_zaks" + str(len(body)))
    for article in body:
        print("parsing_zaks " + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    start_body_len = len(body)

    try:
        res = requests.get(SEARCH_PAGE_URL,
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={"query": keyword,
                                   "p": page,
                                   "sort": "date"
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

        articles = soup.find_all("a", href=re.compile("new/archive/view"))

        if len(articles) == 0:
            return True, body, False, proxy
        for article in articles:
            try:
                article_date = dateparser.parse(article.parent.contents[2][1:].strip())
                href = PAGE_URL + article.attrs['href']
            except Exception as e:
                article_date = None
            if article_date:
                try:
                    if article_date >= limit_date:
                        body.append(
                            {
                                "href": href,
                                "date": article_date,
                            }
                        )
                except Exception as e:
                    body.append(
                        {
                            "href": href,
                            "date": article_date,
                        }
                    )
        if start_body_len == len(body):
            return True, body, True, proxy
        return get_urls(keyword, limit_date, proxy, body, page + 1, attempts)
    elif res.status_code == 404:
        return False, body, False, proxy
    return False, body, False, proxy


def get_page(articles, article_body, proxy, attempt=0):
    photos = []
    sounds = []
    videos = []
    try:
        url = article_body['href']
        res = requests.get(url, headers={
            "user-agent": USER_AGENT
        },
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )
        if res.ok:
            soup_all = BeautifulSoup(res.text)
            try:
                title = soup_all.find("h1", {"itemprop": "headline"}).text
                text = soup_all.find("div", {"itemprop": "articleBody"}).text.strip().replace("\n", "\nbr\n")

                articles.append({"date": article_body['date'],
                                 "title": title, "text": text.strip(),
                                 "href": url,
                                 "photos": photos,
                                 "sounds": sounds,
                                 "videos": videos
                                 })
            except Exception as e:
                print(e)

            return False, articles, proxy
        return False, articles, proxy
    except Exception as e:
        if attempt > 2:
            return False, articles, proxy
        return get_page(articles, article_body, update_proxy(proxy), attempt + 1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parsing_zaks("красота", datetime.strptime("01/01/2021", "%d/%m/%Y"), None, [])

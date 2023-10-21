import re
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta

import dateparser
import requests
from core.sites.utils import DEFAULTS_TIMEOUT, update_proxy

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
URL_MAIN = "http://xn--e1aqccgid7fsa.xn--p1ai"
URL_SEARCH_PAGE = f"{URL_MAIN}/news/?querystring_key=page&page="


def parsing_news_admin_petr(limit_date, proxy):
    print("parsing_news_admin_petr")
    print(limit_date)
    articles = []
    page = 1
    body = []
    is_ok = True
    len = -1
    while page < 100000 and is_ok and len < body.__len__():
        len = body.__len__()
        is_ok, body, proxy = get_urls(page, limit_date, proxy, body)
        page += 1
        print("parsing_news_admin_petr page" + str(page))
    i = 0
    for article in body:
        print("parsing_news_admin_petr " + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(page, limit_date, proxy, body, attempts=0):
    url = URL_SEARCH_PAGE + str(page)
    try:
        if attempts == 0:
            res = requests.get(url,
                               headers={
                                   "user-agent": USER_AGENT
                               },
                               timeout=DEFAULTS_TIMEOUT
                               )
        else:
            res = requests.get(url,
                               headers={
                                   "user-agent": USER_AGENT
                               },
                               proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
    except Exception as e:
        # logger.info(str(e))
        if attempts < 10:
            if attempts == 0:
                return get_urls(page, limit_date, proxy, body, attempts + 1)
            return get_urls(page, limit_date, update_proxy(proxy), body, attempts + 1)
        return False, body, proxy
    if res.ok:
        soup = BeautifulSoup(res.text)
        articles = soup.find_all("div", {"class": "item-inner"})
        if len(articles) == 0:
            return False, body, proxy
        for article in articles:

            try:
                parse_date = dateparser.parse(article.find("div", {"class": "time"}).text.strip())
                try:
                    date = parse_date + timedelta(days=1)
                    if date < datetime(limit_date.year, limit_date.month, limit_date.day):
                        continue
                except Exception as e:
                    print(e)
                title = article.find("h2").text
                url = URL_MAIN + article.find("a", href=re.compile("/news/\d+/")).get("href")
                print(url)

                body.append(
                    {
                        "href": url,
                        "title": title,
                        "date": parse_date
                    }
                )
            except Exception as e:
                print(e)

    elif res.status_code == 404:
        return True, [], proxy
    return True, body, proxy


def get_page(articles, article_body, proxy, attempt=0):
    photos = []
    try:
        url = article_body['href']
        if attempt == 0:
            res = requests.get(url, headers={
                "user-agent": USER_AGENT
            },
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

            soup = soup_all.find("article")

            title = article_body['title']

            try:
                for p in soup.find_all("p"):
                    text += p.text + "<br> \n"
            except Exception:
                pass
            try:
                photos.append(URL_MAIN+soup_all.find("div", {"class": "fotorama"}).find("img").get("src"))
            except Exception:
                pass
            article_date = article_body['date']

            articles.append(
                {"date": article_date,
                 "title": title,
                 "text": text.strip(),
                 "photos": photos,
                 "href": url
                 })

            return True, articles, proxy
        return True, articles, proxy
    except Exception as e:
        if attempt > 3:
            return False, articles, proxy
        if attempt == 0:
            return get_page(articles, article_body, proxy, attempt + 1)
        return get_page(articles, article_body, update_proxy(proxy), attempt + 1)


if __name__ == '__main__':
    articles, proxy = parsing_news_admin_petr(datetime.strptime("01/08/2022", "%d/%m/%Y"), None)
    print(1)
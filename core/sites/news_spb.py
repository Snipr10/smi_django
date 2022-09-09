import re
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta

import dateparser
import requests
from core.sites.utils import DEFAULTS_TIMEOUT, update_proxy

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"

REGS = ["http://www.admnews.ru/",
        "http://www.krgv.ru/",
        "http://www.petrogradnews.ru/",
        "http://www.ksnews.ru/",
        "http://www.news-kron.ru/",
        "http://www.kurort-news.ru/",
        "http://www.mr-news.ru/",
        "http://www.nevnews.ru/",
        # "http://xn--e1aqccgid7fsa.xn--p1ai/",
        "http://www.pd-news.ru/",
        "http://www.primorsknews.ru/",
        "http://www.pushkin-news.ru/",
        "http://www.frunznews.ru/",
        "http://www.news-centre.ru/",
        "http://www.newskolpino.ru/",
        "http://www.kirnews.ru/",
        "http://www.kalininnews.ru/",
        "http://www.vybnews.ru/",
        "http://www.vonews.ru/",

        ]


def parsing_news_spb_ter(limit_date, proxy):
    all_articles = []
    is_oks = []
    for region in REGS:
        is_ok, articles, proxy = parsing_news_spb(region, limit_date, proxy)
        all_articles.append(articles)
        is_oks.append(is_ok)
    return all(is_ok), all_articles, proxy


def parsing_news_spb(region, limit_date, proxy):
    articles = []
    i = 0
    is_not_stopped, body, proxy = get_urls(region, limit_date, proxy)
    if not is_not_stopped:
        return articles, proxy

    if len(body) == 0:
        return articles, proxy

    for article in body:
        print(f"parsing_news_spb {region}" + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass
    print("finish parsing_news_spb")
    return articles, proxy


def get_urls(region_url, limit_date, proxy, attempts=0):
    body = []

    try:
        if attempts == 0:
            res = requests.get(region_url,
                               headers={
                                   "user-agent": USER_AGENT
                               },
                               timeout=DEFAULTS_TIMEOUT
                               )
        else:
            res = requests.get(region_url,
                               headers={
                                   "user-agent": USER_AGENT
                               },
                               proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
    except Exception as e:
        print(e)
        # logger.info(str(e))
        if attempts < 10:
            if attempts == 0:
                return get_urls(region_url, limit_date, proxy, attempts + 1)
            return get_urls(region_url, limit_date, update_proxy(proxy), attempts + 1)
        return False, [], proxy
    print(f"{region_url}: {res.status_code}")
    if res.ok:
        soup = BeautifulSoup(res.text)
        articles = []
        for article in soup.find_all("li"):
            if article.find("a", href=re.compile("/news/")):
                articles.append(article)
        print(f"articles {region_url}: {len(articles)}")
        if len(articles) == 0:
            return False, [], proxy
        for article in articles:
            try:
                article_href = article.find("a")
                try:
                    date = dateparser.parse(article_href.get("href").split("/")[2], settings={'DATE_ORDER': 'YMD'}) + timedelta(days=1)
                    if date < datetime(limit_date.year, limit_date.month, limit_date.day):
                        continue
                except Exception as e:
                    print(e)
                try:
                    href = article_href.find("img").get("title").encode('ISO-8859-1').decode("windows-1251")
                except  Exception:
                    href = article_href.contents[-1].encode('ISO-8859-1').decode("windows-1251")
                body.append(
                    {
                        "href": region_url[:-1] + article_href.get("href"),
                        "title": href,
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
            res.encoding = 'windows-1251'
            soup_all = BeautifulSoup(res.text)
            text = ""

            soup = soup_all.find("div", {"class": "news-content"})

            title = article_body['title']

            try:
                for p in soup.find_all("p"):
                    text += p.text + "<br> \n"
            except Exception:
                pass
            try:
                photos.append(url.split("/news/")[0] + soup_all.find("div", {"class": "img big"}).find("img").get("src"))
            except Exception:
                pass
            article_date = dateparser.parse(soup_all.find("div", {"class":"date-time"}).text.encode('ISO-8859-1').decode("windows-1251"))

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
    articles, proxy = parsing_news_spb("http://www.petrogradnews.ru/", datetime.strptime("04/09/2022", "%d/%m/%Y"), None)
    print(1)
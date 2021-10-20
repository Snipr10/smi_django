from datetime import datetime

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import update_proxy, parse_date, DEFAULTS_TIMEOUT


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
RADIO_PAGE_URL = "https://www.radiozenit.ru/news/page/%s"
RADIO_URL = "https://www.radiozenit.ru/"


def parsing_radio_zenit(limit_date, proxy, body=[]):
    is_not_stopped = True
    page = 1
    body = []
    while is_not_stopped:
        try:
            is_not_stopped, body, is_time, proxy = get_urls(page, limit_date, proxy, body)
            page += 1
            print(f"page {page}")
            if page > 100:
                break
        except Exception:
            is_not_stopped = False
    articles = []
    for article in body:
        print(article['date'])
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(page, limit_date, proxy, body):
    try:
        res = requests.get(RADIO_PAGE_URL % page, headers={
            "user-agent": USER_AGENT
        },
            proxies=proxy.get(list(proxy.keys())[0]),
            timeout=DEFAULTS_TIMEOUT
        )
    except Exception:
        return get_urls(page, limit_date, update_proxy(proxy), body)
    if res.ok:
        soup = BeautifulSoup(res.text)
        tables = soup.find_all("div", {"class": "news-preview labelable"})
        if len(tables) == 0:
            return False, body, False, proxy
        for table in tables:
            article_date = dateparser.parse(table.find("p", {"class": "news-preview__publish-time"}).text)
            if article_date.date() >= limit_date.date():

                href = table.find("a", {"class": "news-preview__link"}).attrs.get("href")
                body.append({"date": article_date, "href": href})
            else:
                return False, body, True, proxy
        return True, body, False, proxy
    else:
        return get_urls(page, limit_date, update_proxy(proxy), body)


def get_page(articles, article_body, proxy, attempt=0):
    text = ""
    photos = []
    sounds = []
    videos = []
    try:
        res = requests.get(RADIO_URL + article_body['href'], headers={
            "user-agent": USER_AGENT
        },
            proxies=proxy.get(list(proxy.keys())[0]),
            timeout=DEFAULTS_TIMEOUT
        )
        if res.ok:
            soup = BeautifulSoup(res.text)
            article = soup.find("article", {"class": "article article__news"})
            title = article.find("h1", {"class": "title title_s_reduced article__title"}).text
            for p in article.find("div", {"class": "article__inner"}).find_all("p"):
                text += p.text
                try:
                    text += f" ({p.contents[0].attrs['href']}) "
                except Exception:
                    pass
                text += "<br> \n"
            try:
                for img in article.find("div", {"class": "article__inner"}).find_all("img"):
                    try:
                        photos.append(img.attrs["src"])
                    except Exception:
                        pass
            except Exception:
                pass
            articles.append({"date": article_body['date'], "title": title, "text": text.replace(" ", " ").strip(),
                             "href": RADIO_URL + article_body['href'],
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_radio_zenit(datetime.strptime("1/04/2021", "%d/%m/%Y"), update_proxy(None), [])
    print(1)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

from datetime import datetime

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://vecherkaspb.ru/page/%s/"


def parsing_vecherkaspb(keyword, limit_date, proxy, body):
    is_not_stopped, body, is_time, proxy = get_urls(keyword, limit_date, proxy, body, 1)
    articles = []
    for article in body:
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    try:
        res = requests.get(SEARCH_PAGE_URL % page,
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={
                               "s": keyword,
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
        articles = []
        try:
            articles = soup.find("main").find_all("article")
        except Exception:
            pass
        if len(articles) == 0:
            return True, body, False, proxy
        for article in articles:
            article_date = dateparser.parse(article.find("time").text)
            if page > 100:
                return True, body, True, proxy
            article_title = article.find("h2", class_="entry-title").find("a", rel="bookmark")

            body.append(
                            {
                                "href": article_title.attrs.get("href"),
                                "date": article_date,
                                "title": article_title.text
                            }
                        )
        return get_urls(keyword, limit_date, update_proxy(proxy), body, page + 1, attempts)
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
            soup = BeautifulSoup(res.text)

            article_section = soup.find("div", class_="entry-content")
            text = ""
            for p in article_section.find_all("p"):
                text += p.text + "<br> \n"

            try:
                photos.append(soup.find("div", class_="entry-img").find("img").attrs.get("src"))
            except Exception:
                pass
            try:
                for img in article_section.find_all("img"):
                    try:
                        photos.append(img.attrs.get("src"))
                    except Exception:
                        pass
            except Exception:
                pass

            articles.append({"date": article_body['date'], "title": article_body['title'], "text": text.strip(),
                             "href": url,
                             "photos": photos,
                             "sounds": sounds,
                             "videos": videos
                             })

            return False, articles, proxy
        return False, articles, proxy
    except Exception as e:
        if attempt > 2:
            return False, articles, proxy
        return get_page(articles, article_body, update_proxy(proxy), attempt + 1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_vecherkaspb("красота", datetime.strptime("01/09/2021", "%d/%m/%Y"), None, [])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

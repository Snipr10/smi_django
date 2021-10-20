from datetime import datetime, date

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "http://novayagazeta.spb.ru/search/"
PAGE_URL = "http://novayagazeta.spb.ru"


def parsing_novayagazeta(keyword, limit_date, proxy, body):
    is_not_stopped, body, is_time, proxy = get_urls(keyword, limit_date, proxy, body, 1)
    articles = []
    for article in body:
        if article['date'].date() >= limit_date.date():
            try:
                is_time, articles, proxy = get_page(articles, article, proxy)
            except Exception:
                pass

    return articles, proxy


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    try:
        res = requests.get(SEARCH_PAGE_URL,
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={"q": keyword,
                                   "sdate": limit_date.date().strftime("%Y-%m-%d"),
                                   "edate": date.today().strftime("%Y-%m-%d"),
                                   "offset": page,
                                   "sort": "cdate",
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
        articles = []
        try:
            articles = soup.find("ul", class_="articles-list article-preview").find_all("li")
        except Exception:
            pass
        if len(articles) == 0:
            return True, body, False, proxy
        for article in articles:
            try:
                article_date = dateparser.parse(str(article.find("span", class_="tools").contents[0]).strip().replace("/", ""))
                if page > 100:
                    return True, body, True, proxy
                article_title = article.find("h2").find("a")

                body.append(
                                {
                                    "href": article_title.attrs.get('href'),
                                    "date": article_date,
                                    "title": article_title.text
                                }
                            )
            except Exception as e:
                pass
        return get_urls(keyword, limit_date, proxy, body, page + 1, attempts)
    elif res.status_code == 404:
        return False, body, False, proxy
    return False, body, False, proxy


def get_page(articles, article_body, proxy, attempt=0):
    photos = []
    sounds = []
    videos = []
    try:
        url = PAGE_URL + article_body['href']
        res = requests.get(url, headers={
            "user-agent": USER_AGENT
        },
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )
        if res.ok:
            soup = BeautifulSoup(res.text)

            article_section = soup.find("article", class_="article-view")

            try:
                text = article_section.find("b").text + "<br> \n"
            except Exception:
                text = ""

            for p in article_section.find_all("p"):
                text += p.text.strip() + "<br> \n"

            try:
                photos.append(article_section.find("figure").find("img").attrs.get("src"))
            except Exception:
                pass
            try:
                for img in article_section.find_all("span", class_="article-photo"):
                    try:
                        photos.append(img.find("a").attrs.get("href"))
                    except Exception:
                        pass
            except Exception:
                pass

            articles.append({"date": article_body['date'],
                             "title": article_body['title'],
                             "text": text.strip(),
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
    parsing_novayagazeta("материалы", datetime.strptime("01/09/2021", "%d/%m/%Y"), None, [])

from datetime import datetime, date

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://www.interfax.ru/search/news/?sw="
PAGE_URL = "https://www.interfax.ru"


def parsing_interfax(keyword, limit_date, proxy, body):
    is_not_stopped, body, is_time, proxy = get_urls(keyword, limit_date, proxy, [], body, 1)
    articles = []
    i = 0
    print(limit_date)
    for article in body:
        print("parsing_interfax " + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(keyword, limit_date, proxy, body, urls, page, attempts=0):
    try:
        print("interfax url  " + str(SEARCH_PAGE_URL + requests.utils.quote(keyword.encode('windows-1251'))))
        res = requests.get(SEARCH_PAGE_URL + requests.utils.quote(keyword.encode('windows-1251')),
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={"sec": 0,
                                   "df": limit_date.date().strftime("%d.%m.%Y"),
                                   "dt": date.today().strftime("%d.%m.%Y"),
                                   "sort": "date",
                                   "p": "page_" + str(page)
                                   },
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )

    except Exception as e:
        # logger.info(str(e))
        if attempts < 10:
            return get_urls(keyword, limit_date, update_proxy(proxy), body, urls, page, attempts + 1)
        return False, body, False, proxy
    if res.ok:
        soup = BeautifulSoup(res.content.decode("windows-1251"))
        articles = []
        try:
            divs = soup.find("div", {"class": "sPageResult"}).find_all("div")
            for div in divs:
                for d in div.find_all("div"):
                    if len(d.find_all("a")) > 1:
                        articles.append(d)
        except Exception:
            pass
        if len(articles) == 0:
            return True, body, False, proxy
        repeat = 0
        for article in articles:
            article_date = dateparser.parse(article.find("time").attrs.get("datetime"))
            if article_date.date() < limit_date.date():
                return True, body, True, proxy
            if page > 100:
                return True, body, True, proxy

            href_data = article.find_all("a")[-1]
            href = href_data.attrs.get("href")
            if href in urls:
                repeat += 1
                if repeat == len(articles):
                    return True, body, False, proxy
            else:
                if article_date.date() >= limit_date.date():

                    body.append(
                        {
                            "href": href,
                            "date": article_date,
                            "title": href_data.text
                        }
                    )
                urls.append(href)
        return get_urls(keyword, limit_date, update_proxy(proxy), body, urls, page + 1, attempts)
    elif res.status_code == 404:
        return False, body, False, proxy
    return False, body, False, proxy


def get_page(articles, article_body, proxy, attempt=0):
    text = ""
    photos = []
    sounds = []
    videos = []
    try:
        url = PAGE_URL + article_body['href']
        res = requests.get(url, headers={
            "user-agent": USER_AGENT
        },
                           # proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )
        if res.ok:
            soup = BeautifulSoup(res.content.decode("windows-1251"))
            article = soup.find("article", {"itemprop": "articleBody"})
            for p in article.find_all("p"):
                text += p.text
                text += "\n"
            try:
                for img in article.find_all("figure", {"class": "inner"}):
                    try:
                        photos.append(img.find("img").attrs.get("src"))
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
    except Exception:
        if attempt > 2:
            return False, articles, proxy
        return get_page(articles, article_body, update_proxy(proxy), attempt + 1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parsing_interfax("красота", datetime.strptime("01/09/2021", "%d/%m/%Y"), update_proxy(None), [])

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import DEFAULTS_TIMEOUT, update_proxy

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://www.gov.spb.ru/press/disproof/?page=%s"
PAGE_URL = "https://www.gov.spb.ru"


def parsing_governor_disproof(limit_date, proxy):
    articles = []
    page = 1
    i = 0
    is_ok = True
    while page < 250:
        body = []
        is_not_stopped, body, proxy = get_urls(limit_date, proxy, body, page)
        is_ok = is_not_stopped
        page += 1
        if not is_not_stopped:
            break
        if len(body) == 0:
            break
        for article in body:
            print("parsing_governor_disproof " + str(i))
            i += 1
            try:
                is_time, articles, proxy = get_page(articles, article, proxy)
            except Exception:
                pass
        if len(articles) == 0 or articles[-1]['date'].date() < limit_date.date():
            break

    return is_ok, articles, proxy


def get_urls(limit_date, proxy, body, page, attempts=0):
    try:
        if attempts == 0:
            res = requests.get(SEARCH_PAGE_URL % page,
                               headers={
                                   "user-agent": USER_AGENT
                               },
                               timeout=DEFAULTS_TIMEOUT
                               )
        else:
            res = requests.get(SEARCH_PAGE_URL % page,
                               headers={
                                   "user-agent": USER_AGENT
                               },
                               proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
    except Exception as e:
        # logger.info(str(e))
        if attempts < 10:
            return get_urls(limit_date, update_proxy(proxy), body, page, attempts + 1)
        return False, body, proxy
    if res.ok:
        soup = BeautifulSoup(res.text)

        articles = soup.find_all("li", {"class": "object-list__item"})

        if len(articles) == 0:
            return False, body, proxy
        for article in articles:
            article_href = article.find("a")
            body.append(
                {
                    "href": article_href.attrs.get("href"),
                    "title": article_href.text.strip(),
                }
            )

    elif res.status_code == 404:
        return True, body, proxy
    return True, body, proxy


def get_page(articles, article_body, proxy, attempt=0):
    photos = []
    try:
        url = PAGE_URL + article_body['href']
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

            soup = soup_all.find("div", {"class": "block content"})

            try:
                title = soup.find("h2", {"class": "block__title"}).text
            except Exception:
                title = article_body['title']

            try:
                for p in soup.find_all("p"):
                    text += p.text + "<br> \n"
            except Exception:
                pass
            try:
                for img in soup.find_all("img"):
                    photos.append(PAGE_URL + img.attrs.get("src", ""))
            except Exception:
                pass
            article_date = dateparser.parse(soup.find("div", {"class": "source__date"}).text.strip().split(":")[-1].strip())

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
        if attempt > 2:
            return False, articles, proxy
        return get_page(articles, article_body, update_proxy(proxy), attempt + 1)


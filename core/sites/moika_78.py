import re
from datetime import datetime

import dateparser
import requests
from bs4 import BeautifulSoup, Tag

from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://moika78.ru/page/%s/"


def parsing_moika78(keyword, limit_date, proxy, body):
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
            sections = soup.find_all("section")
            for section in sections:
                try:
                    for section_div in section.find_all("div", {"class": "container"}):
                        for div_row in section_div.find_all("div", {"class": "row"}):
                            for row in div_row.find_all("div", {"class": "row"}):
                                articles = row.find_all("div", class_=re.compile("sol-xs-"))
                except Exception:
                    pass
        except Exception:
            pass
        if len(articles) == 0:
            return True, body, False, proxy
        for article in articles:
            if not isinstance(article, Tag):
                continue
            article_date = dateparser.parse(article.find("time").attrs.get("datetime"))
            if page > 2:
                if article_date.date() < limit_date.date():
                    return True, body, True, proxy
            if page > 100:
                return True, body, True, proxy
            body.append(
                        {
                            "href": article.find("a", class_="thumbnail_narrow").attrs.get("href"),
                            "date": article_date,
                            "title": article.find("span", itemprop="headline").text
                        }
                    )
        return get_urls(keyword, limit_date, proxy, body, page + 1, attempts)
    elif res.status_code == 404:
        return False, body, False, proxy
    return False, body, False, proxy


def get_page(articles, article_body, proxy, attempt=0):
    text = ""
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
            article = soup.find("section", {"class": "single-body"})
            main_article = article.find("div", {"class": "post-content article"})
            for p in main_article.contents:
                try:
                    p_text = p.text.strip()
                    if p_text:
                        text += p.text + "\r\n <br> "
                except Exception:
                    pass
            try:
                for img in article.find_all("div", {"class": "image-box"}):
                    try:
                        photos.append(img.find("img").attrs.get("src"))
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                for img in main_article.find_all("img"):
                    try:
                        photos.append(img.attrs.get("data-src"))
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
    parsing_moika78("красота", datetime.strptime("01/09/2021", "%d/%m/%Y"), update_proxy(None), [])

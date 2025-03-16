from datetime import datetime
import dateparser
import requests
from bs4 import BeautifulSoup
from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://spbformat.ru/page/"
PAGE_URL = "https://spbformat.ru"


def parsing_spbformat(keyword, limit_date, proxy, body):
    for p in range(1, 100):
        is_not_stopped, body, is_time, proxy = get_urls(keyword, limit_date, proxy, body, p)
        if is_not_stopped:
            break
    articles = []
    for article in body:
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    try:
        url = SEARCH_PAGE_URL + str(page)
        res = requests.get(url,
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={"s": keyword},
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
            articles = soup.find("div", class_="archive content-container").find_all("div", class_='cntent-container')
        except Exception:
            pass
        if len(articles) == 0:
            return True, body, False, proxy
        for article in articles:
            try:
                article_date = dateparser.parse(article.find("span", class_='entry-date').text)

                body.append(
                    {
                        "href": article.find("h4", class_='entry-title').find("a").get("href"),
                        "date": article_date,
                        "title": article.find("h4", class_='entry-title').text
                    }
                )
            except Exception as e:
                pass
        if article_date.date() < limit_date.date():
            return True, body, True, proxy
        return False, body, True, proxy
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

            'user-agent': USER_AGENT
        },
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )
        if res.ok:
            soup = BeautifulSoup(res.text)
            content_part = soup.find("div", class_="entry-content")
            try:
                for i in content_part.find_all("img"):
                    photos.append(i.attrs.get("src"))
            except Exception:
                pass

            date_ = article_body['date']
            text = ""
            for p in content_part.find_all("p"):
                try:
                    text += p.text + "\r\n <br> "
                except Exception:
                    pass
            articles.append({"date": date_,
                             "title": article_body['title'],
                             "text": text,
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
    parsing_spbformat("тест", datetime.strptime("01/03/2025", "%d/%m/%Y"), None, [])

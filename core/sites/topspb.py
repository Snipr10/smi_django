import dateparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from core.sites.utils import stop_proxy, update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://tvspb.ru/news/"


def parsing_topspb(limit_date, proxy):
    print("parsing_topspb")
    print(limit_date)
    # first_request
    articles = []
    page = 1
    body = []
    is_parsing_url = True
    while page < 500 and is_parsing_url:
        is_parsing_url, body, proxy = get_urls(limit_date, proxy, body, page)
        page += 1
        print("parsing_topspb page" + str(page))

    i = 0
    for article in body:
        print("parsing_dp " + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(limit_date, proxy, body, page, attempts=0):
    try:
        # ?SearchString=&skip=0&take=10&DateFrom=&DateTo=&IsInIssue=false&SortType=2&SortOrder=1"
        if attempts == 0:
            res = requests.get(f"{SEARCH_PAGE_URL}{page}",
                               headers={
                                   "user-agent": USER_AGENT
                               },

                               # proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
        else:
            res = requests.get(f"{SEARCH_PAGE_URL}/{page}",
                               headers={
                                   "user-agent": USER_AGENT
                               },

                               proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
    except Exception as e:
        stop_proxy(proxy)
        # logger.info(str(e))
        if attempts < 10:
            return get_urls(limit_date, update_proxy(proxy), body, page, attempts + 1)
        return False, body, proxy
    if res.ok:
        soup = BeautifulSoup(res.text)

        for site in soup.find("div", {"class": "block-news-wrap block-news__img-top"}).find_all("a", {"class":"img-top__news-item mb30"}):
            try:
                site_date = dateparser.parse(site.find("div", {"class":"img-top__date"}).text)
            except Exception:
                site_date = None
            print(site_date)

            body.append({
                "title": site.find("div", {"class": "img-top__title"}).text,
                "href": site.attrs['href'],
                "date": site_date
            })
            if site_date and site_date.date() < limit_date.date():
                return False, body, proxy
        return True, body, proxy

    elif res.status_code == 404:
        return False, body, None, proxy
    return True, body, proxy


def get_page(articles, article_body, proxy, attempt=0):
    photos = []
    sounds = []
    videos = []
    try:
        url = article_body['href']
        if attempt == 0:

            res = requests.get(url, headers={
                "user-agent": USER_AGENT
            },
                               # proxies=proxy.get(list(proxy.keys())[0]),
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
            soup = BeautifulSoup(res.text)
            text = ""

            try:
                text = soup.find("div", {"class": "post-content"}).text.strip()
            except Exception:
                pass
            try:
                for img in soup.find("div", {"class":"post-news-block__img"}).find_all("img"):
                    photos.append(img.attrs.get("src", ""))
            except Exception:
                pass
            try:
                videos.append(soup.find("figure", {"class": "block-video"}).find("video").find("source").get("src"))
            except Exception:
                pass
            articles.append(
                {"date": article_body['date'],
                 "title": article_body['title'],
                 "text": text.strip(),
                 "photos": photos,
                 "href": url,
                 "videos": videos
                 })

            return False, articles, proxy
        return False, articles, proxy
    except Exception as e:
        stop_proxy(proxy)
        if attempt > 2:
            return False, articles, proxy
        return get_page(articles, article_body, update_proxy(proxy), attempt + 1)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    a, b = parsing_topspb(datetime.strptime("10/01/2024", "%d/%m/%Y"), None)
    print(a)

from datetime import datetime
import json

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import stop_proxy, update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://www.dp.ru/api/v1.0/Articles/FindArticles"
PAGE_URL = "https://www.dp.ru"


def parsing_dp(limit_date, proxy):
    print("parsing_dp")
    print(limit_date)
    # first_request
    articles = []
    page = 0
    body = []
    is_parsing_url = True
    while page < 500 and is_parsing_url:
        is_parsing_url, body, proxy = get_urls(limit_date, proxy, body, page)
        page += 1
        print("parsing_dp page" + str(page))

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
            res = requests.get(SEARCH_PAGE_URL,
                               headers={
                                   "user-agent": USER_AGENT
                               },
                               params={"SearchString": "",
                                       "skip": 50 * page,
                                       "take": 50,
                                       "DateFrom": "",
                                       "DateTo": "",
                                       "IsInIssue": "false",
                                       "SortType": 2,
                                       "SortOrder": 1
                                       },
                               # proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
        else:
            res = requests.get(SEARCH_PAGE_URL,
                               headers={
                                   "user-agent": USER_AGENT
                               },
                               params={"SearchString": "",
                                       "skip": 50 * page,
                                       "take": 50,
                                       "DateFrom": "",
                                       "DateTo": "",
                                       "IsInIssue": "false",
                                       "SortType": 2,
                                       "SortOrder": 1
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

        json_res = json.loads(res.text)
        print("json_res")

        articles = json_res['List']
        print("articles")

        if len(articles) == 0:
            return False, body, proxy
        for site in articles:
            try:
                site_date = dateparser.parse(str(site['PublicationDate']).split("T")[0])
            except Exception :
                site_date = None
            print(site_date)
            if site_date and site_date.date() < limit_date.date():
                return False, body, proxy
            else:
                body.append({
                        "title": site['Headline'],
                        "href": PAGE_URL + "/" + site['ShortUrl'],
                        "date": site_date
                    })
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
            soup_all = BeautifulSoup(res.text)
            text = ""

            soup = soup_all.find("div", {"class": "d-flex flex-row"})

            try:
                for p in soup.find_all("div", {"class": "paragraph paragraph-text"}):
                    text += p.text + "\r\n <br> "
            except Exception:
                pass
            try:
                for img in soup.find_all("img"):
                    if "data:image/png;base64" not in img.attrs.get("src", ""):
                        photos.append(img.attrs.get("src", ""))
            except Exception:
                pass

            articles.append(
                {"date": article_body['date'],
                 "title": article_body['title'],
                 "text": text.strip(),
                 "photos": photos,
                 "href": url,
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
    articles, proxy = parsing_dp(datetime.strptime("15/08/2022", "%d/%m/%Y"), None)
    print(1)

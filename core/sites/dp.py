from datetime import datetime
import json

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import update_proxy, stop_proxy

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
FIRST_SEARCH = "https://www.dp.ru/search"
SEARCH_PAGE_URL = "https://www.dp.ru/Search/LoadSearchPage"
PAGE_URL = "https://www.dp.ru"


def parsing_dp(limit_date, proxy):
    # first_request
    is_parsing_url, body, next_json, proxy = parsing_first_search(limit_date, proxy, attempts=0)
    articles = []
    page = 1

    while page < 1000 and is_parsing_url and next_json is not None:
        is_parsing_url, body, next_json, proxy = get_urls(limit_date, proxy, body, next_json)
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


def parsing_first_search(limit_date, proxy, attempts=0):
    body = []
    try:
        res = requests.get(FIRST_SEARCH,
                           headers={
                               "user-agent": USER_AGENT
                           },

                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )
        if not res.ok:
            raise Exception(res.text)
        soup = BeautifulSoup(res.text)
        next_search_div = soup.select('div[ng-loading*=""]')
        next_json_data = next_search_div[0].attrs['ng-loading']
        next_json = json.loads(
            next_json_data.replace("'", '"').replace("{ ", '{"').replace(", ", ', "').replace(": ", '": '))
        for site in soup.find_all("a", {"class": "b-inline-article__preview"}):
            href = site.attrs['href']
            href_split = href.split("/")
            site_date = datetime(int(href_split[2]), int(href_split[3]), int(href_split[4]))

            if site_date.date() >= limit_date.date():
                body.append({"title": site.text.strip(), "href": href})
            else:
                return False, body, next_json, proxy
        return True, body, next_json, proxy
    except Exception as e:
        stop_proxy(proxy)
        # logger.info(str(e))
        if attempts < 10:
            return parsing_first_search(limit_date, update_proxy(proxy), attempts + 1)
        return False, [], None, proxy


def get_urls(limit_date, proxy, body, next_json, attempts=0):
    try:
        res = requests.get(SEARCH_PAGE_URL,
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={"query": "",
                                   "page": next_json['page'],
                                   "lastId": next_json['lastId'],
                                   "lastDate": next_json['lastDate'],
                                   },
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )
    except Exception as e:
        stop_proxy(proxy)
        # logger.info(str(e))
        if attempts < 10:
            return get_urls(limit_date, update_proxy(proxy), body, next_json, attempts + 1)
        return False, body, proxy
    if res.ok:
        json_res = json.loads(res.text)

        articles = BeautifulSoup(
            json_res["strToCompile"]).find_all("a", {"class": "b-inline-article__preview"})

        if len(articles) == 0:
            return False, body, json_res, proxy
        for site in articles:
            href = site.attrs['href']
            href_split = href.split("/")
            site_date = datetime(int(href_split[2]), int(href_split[3]), int(href_split[4]))

            if site_date.date() >= limit_date.date():
                body.append({"title": site.text.strip(), "href": href})
            else:
                return False, body, next_json, proxy
        return True, body, json_res, proxy

    elif res.status_code == 404:
        return False, body, None, proxy
    return True, body, None, proxy


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
            soup_all = BeautifulSoup(res.text)
            text = ""

            soup = soup_all.find("div", {"class": "b-article-grid-layout-left-column__inner b-article__content"})

            try:
                for p in soup.find_all("p"):
                    text += p.text + "\n"
            except Exception:
                pass
            try:
                for img in soup.find_all("img"):
                    if "data:image/png;base64" not in img.attrs.get("src", ""):
                        photos.append("https:" + img.attrs.get("src", ""))
            except Exception:
                pass
            article_date = dateparser.parse(soup_all.find("span", {"class": "b-article-header-signature__date"}).text.strip())

            articles.append(
                {"date": article_date,
                 "title": article_body['title'],
                 "text": text.strip(),
                 "photos": photos,
                 })

            return False, articles, proxy
        return False, articles, proxy
    except Exception as e:
        stop_proxy(proxy)
        if attempt > 2:
            return False, articles, proxy
        return get_page(articles, article_body, update_proxy(proxy), attempt + 1)





DEFAULTS_TIMEOUT = 100

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_dp(datetime.strptime("21/08/2021", "%d/%m/%Y"), update_proxy(None))
    print(1)


from datetime import datetime, date, timedelta

import dateparser
import requests
from bs4 import BeautifulSoup, Tag, NavigableString

from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

SEARCH_PAGE_URL = "https://thecity.m24.ru/sphinx"
URL = "https://thecity.m24.ru"
HEADERS = {
    'authority': 'thecity.m24.ru',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
}


def parsing_thecitym24(keyword, limit_date, proxy, body):
    limit_date = date(limit_date.year, limit_date.month, limit_date.day) - timedelta(days=1)
    is_not_stopped = False
    page = 1
    while not is_not_stopped:
        try:
            body, is_time, proxy, is_error = get_urls(keyword, limit_date, proxy, body, page)

            is_not_stopped = is_error or is_time
            page += 1
            print(f"page {page}")
            if page > 100:
                break
            if is_error:
                break
        except Exception as e:
            is_not_stopped = True
    return body, proxy


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    try:
        params = {
            "criteria": keyword,
            "page": page,
        }
        res = requests.get(SEARCH_PAGE_URL,
                           params=params,
                           timeout=DEFAULTS_TIMEOUT,
                           headers=HEADERS,
                           proxies=proxy.get(list(proxy.keys())[0]),
                           )
        # try:
        #     res = requests.get(SEARCH_PAGE_URL,
        #                        params=params,
        #                        timeout=DEFAULTS_TIMEOUT,
        #                        headers=HEADERS,
        #                        # proxies=proxy,
        #                        )
        #     if not res.ok:
        #         raise Exception("error")
        # except Exception as e:
        #     res = requests.get(SEARCH_PAGE_URL,
        #                        params=params,
        #                        timeout=DEFAULTS_TIMEOUT,
        #                        headers=HEADERS,
        #                        proxies=proxy.get(list(proxy.keys())[0]),
        #                        )
    except Exception as e:
        if attempts < 10:
            return get_urls(keyword, limit_date, update_proxy(proxy), body, page, attempts + 1)
        return body, False, proxy, True
    if res.ok:
        bs_result = BeautifulSoup(res.text)
        materials_article = bs_result.find("div", {"class": "b-materials-list g-clearfix"})
        for article in materials_article.find_all("li"):
            try:
                url = URL + article.find("a").get("href")
                is_new = True
                for b in body:
                    if b.get("href") == url:
                        is_new = False
                        break
                if not is_new:
                    return body, False, proxy, True
                article, is_new, proxy = get_page(url, materials_article.find_all("li")[0].find("span").text.strip(), proxy,
                                           limit_date, attempt=0)
                if not is_new:
                    return body, False, proxy, True
                body.append(
                    article
                )
            except Exception:
                pass
        return body, False, proxy, False

    return body, False, proxy, True


def get_page(url, title, proxy, limit_date, attempt=0):
    photos = []
    sounds = []
    videos = []
    print(url)
    url = "https://thecity.m24.ru/news/6256"
    try:
        res = requests.get(url,
                           timeout=DEFAULTS_TIMEOUT,
                           headers=HEADERS,
                           proxies=proxy.get(list(proxy.keys())[0]),
                           )
        # try:
        #     res = requests.get(url,
        #                        timeout=DEFAULTS_TIMEOUT,
        #                        headers=HEADERS,
        #                        # proxies=proxy,
        #                        )
        #     if not res.ok:
        #         raise Exception("error")
        # except Exception as e:
        #     res = requests.get(url,
        #                        timeout=DEFAULTS_TIMEOUT,
        #                        headers=HEADERS,
        #                        proxies=proxy.get(list(proxy.keys())[0]),
        #                        )
        if res.ok:
            res_data = BeautifulSoup(res.text)
            body_article = res_data.find("div", {"class": "b-material-body"})
            text = ""

            for c in body_article.children:
                try:
                    if c.attrs['class'][0] == "caption":
                        break
                except Exception:
                    pass
                if isinstance(c, Tag):
                    text += c.text.strip() + "\r\n <br> "
                elif isinstance(c, NavigableString):
                    text += str(c).strip() + "\r\n <br> "
            text = text.strip()
            try:
                photos.append(
                    URL + res_data.find("div", {"class": "b-material-before-body__media"}).find("img").get("src"))
            except Exception:
                pass
            for p in res_data.find_all("img"):
                try:
                    if "/b/d/" in p.get("src"):
                        photos.append(URL + p.get("src"))
                except Exception:
                    pass
            for v in res_data.find_all("video"):
                try:
                    videos.append(URL + v.get("src"))
                except Exception:
                    pass
            date = dateparser.parse(res_data.find("p", {"class": "b-material__date"}).text)
            return {
                       "date": date,
                       "title": title,
                       "text": text.strip(),
                       "href": url,
                       "photos": photos,
                       "sounds": sounds,
                       "videos": videos
                   }, date.date() >= limit_date, proxy

        return None, True, proxy
    except Exception as e:
        if attempt > 2:
            return None, True, proxy
        return get_page(url, title, update_proxy(proxy), limit_date, attempt + 1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_thecitym24("Москва", datetime.strptime("21/05/2022", "%d/%m/%Y"), None, [])
    print(1)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# This is a sample Python script.
import json
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# radio
from datetime import datetime, date, timedelta

import requests
from bs4 import BeautifulSoup

from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

SEARCH_PAGE_URL = "https://tass.ru/tbp/api/v1/search"
URL = "https://tass.ru"
MEDIA_URL = "https://cdn-storage-tass.cdnvideo.ru/"

HEADERS = {
    # 'authority': 'tass.ru',
    # 'accept': 'application/json, text/plain, */*',
    # 'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'cache-control': 'no-cache',
    # 'dnt': '1',
    # 'pragma': 'no-cache',
    # 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    # 'sec-ch-ua-mobile': '?0',
    # 'sec-ch-ua-platform': '"Linux"',
    # 'sec-fetch-dest': 'empty',
    # 'sec-fetch-mode': 'cors',
    # 'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',

}

POST_HEADER = headers = {
    'authority': 'tass.ru',
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    'x-nextjs-data': '1'
}

COOKIE = "__jhash_=26; __hash_=9919349849e67f6ad9248a280c884142;"


# logger = get_logger(__name__)


def parsing_tass(keyword, limit_date, proxy, body):
    limit_date = date(limit_date.year, limit_date.month, limit_date.day) - timedelta(days=1)
    is_not_stopped = False
    page = 0
    while not is_not_stopped:
        try:
            body, is_time, proxy, is_error = get_urls(keyword, limit_date, proxy, body, page)
            is_not_stopped = is_error or is_time
            page += 1
            print(f"page {page}")
            if page > 100000:
                break
            if is_error:
                break
        except Exception as e:

            is_not_stopped = True
    articles = []

    for post in body:
        try:
            articles, proxy = get_page(articles, post, proxy)
        except Exception as e:
            pass

    return articles, proxy


def request(params, proxy, url=SEARCH_PAGE_URL, headers=HEADERS):
    res_json = None
    headers_cookie = headers.copy()
    headers_cookie["cookie"] = COOKIE
    if not res_json:
        try:
            res = requests.get(url,
                               params=params,
                               headers=headers,
                               timeout=DEFAULTS_TIMEOUT,
                               proxies=proxy.get(list(proxy.keys())[0]),
                               )
            res_json = get_json(res)
        except Exception as e:
            pass
    if not res_json:
        try:
            res = requests.get(url,
                               params=params,
                               headers=headers_cookie,
                               timeout=DEFAULTS_TIMEOUT,
                               proxies=proxy.get(list(proxy.keys())[0]),
                               )
            res_json = get_json(res)
        except Exception as e:
            pass
    return res_json


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    try:
        limit = 20
        params = {
            "lang": "ru",
            "search": keyword,
            "limit": limit,
            "offset": limit * page,
        }
        res_json = request(params, proxy)
        if not res_json:
            raise Exception("restart")
    except Exception as e:
        if attempts < 10:
            return get_urls(keyword, limit_date, update_proxy(proxy), body, page, attempts + 1)
        return body, False, proxy, True
    if res_json:
        if not res_json.get("result"):
            return body, True, proxy, True

        for r in res_json.get("result") or []:
            pub_date = datetime.strptime(r['published_dt'], '%Y-%m-%dT%H:%M:%S')
            if pub_date.date() < limit_date:
                return body, True, proxy, False
            body.append(
                {
                    "href": URL + r.get("url"),
                    "date": pub_date,
                    "title": r.get("title")
                }
            )
        return body, False, proxy, False

    return body, False, proxy, True


def get_page(articles, article_body, proxy, attempt=0):
    photos = []
    sounds = []
    videos = []
    try:
        url = article_body['href']
        res_json = request({}, proxy, url=url, headers=POST_HEADER)

        if res_json:
            res_data = res_json['props']['pageProps']['data']
            text = res_data['subtitle'] + "<br> \n" + res_data['lead']
            try:
                photos.append(MEDIA_URL + res_data['main_media']['image']['url'])
            except Exception:
                pass

            for content in res_data.get('content_blocks') or {}:
                try:
                    photos.append(MEDIA_URL + content['image']['url'])
                except Exception:
                    pass
                content_text = content.get('text') or ""
                if content_text:
                    text += "<br> \n" + content_text
                content_url = content.get('url') or ""
                if "media" in content_url:
                    photos.append(MEDIA_URL + content_url)
                for item in content.get('items') or {}:
                    content_text = item.get('text') or ""
                    if content_text:
                        text += "<br> \n" + content_text
            articles.append(
                {
                    "date": article_body['date'],
                    "title": article_body['title'],
                    "text": text.strip(),
                    "href": url,
                    "photos": photos,
                    "sounds": sounds,
                    "videos": videos
                }
            )

            return articles, proxy
        return articles, proxy
    except Exception as e:
        if attempt > 2:
            return articles, proxy
        return get_page(articles, article_body, update_proxy(proxy), attempt + 1)


def get_json(res):
    res_json = None
    try:
        res_json = res.json()
    except Exception:
        try:
            res_json = json.loads(BeautifulSoup(res.text).find(id="__NEXT_DATA__").string)
        except Exception:
            pass
    return res_json


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_tass("единая россия", datetime.strptime("21/05/2022", "%d/%m/%Y"), update_proxy(None), [])
    print(1)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

from datetime import datetime

import dateparser
import requests

from core.sites.utils import DEFAULTS_TIMEOUT, update_proxy

X_ACCESS_TOKEN = '436301d248649442f5f5fa5f26b9f2daefa68f5c'
SEARCH_PAGE_URL = "https://api.vedomosti.ru/v2/documents/search"
headers = {
    'authority': 'api.vedomosti.ru',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU,ru;q=0.9',
    'cache-control': 'no-cache',
    'dnt': '1',
    'origin': 'https://www.vedomosti.ru',
    'pragma': 'no-cache',
    'referer': 'https://www.vedomosti.ru/',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Mobile Safari/537.36',
    'x-access-token': X_ACCESS_TOKEN,
}


def parsing_vedomosti(keyword, limit_date, proxy, articles):
    page = 0
    is_not_stopped = True
    is_error = False
    while is_not_stopped:
        try:
            is_not_stopped, articles, is_time, proxy, is_error = get_urls(keyword, limit_date, proxy, articles, page)
            page += 1
            print(f"page {page}")
            if page > 100:
                break
            if is_error:
                break
        except Exception:
            is_not_stopped = False

    if is_error:
        raise Exception("Error")
    return articles, proxy


def get_urls(keyword, limit_date, proxy, articles, page, attempts=0):
    try:
        if attempts == 0 and proxy == None:
            res = requests.get(SEARCH_PAGE_URL,
                               headers=headers,
                               params={"query": keyword,
                                       "p": page,
                                       "sort": "date",
                                       "date_from": limit_date.date().strftime("%Y-%m-%d"),
                                       "date_to": datetime.now().strftime("%Y-%m-%d"),
                                       "limit": 20,
                                       "from": page*20
                                       },
                               timeout=DEFAULTS_TIMEOUT
                               )
        else:
            res = requests.get(SEARCH_PAGE_URL,
                               headers=headers,
                               params={"query": keyword,
                                       "p": page,
                                       "sort": "date",
                                       "date_from": limit_date.date().strftime("%Y-%m-%d"),
                                       "date_to": datetime.now().strftime("%Y-%m-%d"),
                                       "limit": 20,
                                       "from": page * 20
                                       },
                               proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
    except Exception as e:
        # logger.info(str(e))
        if attempts < 10:
            return get_urls(keyword, limit_date, update_proxy(proxy), articles, page, attempts + 1)
        return False, articles, False, proxy, True
    try:
        if res.ok:
            json_res = res.json()

            for res in (json_res.get('found') or []):
                photos = []
                res_article = res.get('source', {})

                try:
                    photos.append("https://cdn5.vedomosti.ru" + res_article['image']['normal']['url'])
                except Exception:
                    pass
                articles.append(
                    {
                        "date": dateparser.parse(res_article['published_at']),
                        "title": res_article['title'],
                        "text": res_article['boxes'],
                        "href": "https://" + res_article['url'],
                                "photos": photos,
                                "sounds": [],
                                "videos": []
                                })
            if json_res['stat']['total'] > page * 20 + 20:
                return True, articles, False, proxy, False
            else:
                return False, articles, False, proxy, False
    except Exception:
        pass
    if attempts < 10:
        return get_urls(keyword, limit_date, update_proxy(proxy), articles, page, attempts + 1)
    return False, articles, False, proxy, True



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parsing_vedomosti("энерго", datetime.strptime("01/06/2022", "%d/%m/%Y"), None, [])

import re
from datetime import datetime
import json

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import stop_proxy, update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"

SEARCH_URL = "https://xn--80asmdh4e.xn--p1ai/api/graphql"
PAGE_URL = "https://районы.рф/"

def parsing_raioni(limit_date, proxy):
    print("parsing_raioni")
    print(limit_date)
    # first_request
    articles = []
    page = 0
    body = []
    is_parsing_url = True

    while page < 100 and is_parsing_url:
        is_parsing_url, body, proxy = get_urls(limit_date, proxy, body, page)
        page += 1
        print("parsing_raioni page" + str(page))

    i = 0
    for article in body:
        print("parsing_raioni " + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(limit_date, proxy, body, page, attempts=0):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://xn--80asmdh4e.xn--p1ai/catalog',
        'content-type': 'application/json',
        'Origin': 'https://xn--80asmdh4e.xn--p1ai',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=4'
    }
    payload = json.dumps({
        "operationName": "publicationsShortCardGet",
        "variables": {
            "limit": 50,
            "offset": page*50,
            "publishedAt": "DESC",
            "pressRelease": False,
            "districtIds": [
                "1"
            ]
        },
        "query": "query publicationsShortCardGet($authorId: ID, $categoryIds: [ID!], $categoryUrl: String, $districtIds: [ID!], $districtPublication: Boolean, $ids: [ID!], $limit: Int, $mainline: Boolean, $offset: Int, $pressRelease: Boolean, $publishedAt: OrderDirection, $publishedAtGt: ISO8601Date, $publishedAtLt: ISO8601Date, $title: String, $urgent: Boolean, $url: String) {\n  publicationsGet(\n    authorId: $authorId\n    categoryIds: $categoryIds\n    categoryUrl: $categoryUrl\n    districtIds: $districtIds\n    districtPublication: $districtPublication\n    ids: $ids\n    limit: $limit\n    mainline: $mainline\n    offset: $offset\n    pressRelease: $pressRelease\n    publishedAt: $publishedAt\n    publishedAtGt: $publishedAtGt\n    publishedAtLt: $publishedAtLt\n    title: $title\n    urgent: $urgent\n    url: $url\n  ) {\n    ...PublicationShortCard\n    __typename\n  }\n}\n\nfragment PublicationShortCard on Publication {\n  authorId\n  categories {\n    id\n    name\n    __typename\n  }\n  cover {\n    filename\n    id\n    thumbnailVariantUrl\n    thumbnailWebpVariantUrl\n    __typename\n  }\n  description\n  districtIds\n  id\n  pressRelease\n  publishedAt\n  title\n  urgent\n  url\n  __typename\n}"
    })
    try:
        if attempts == 0:
            res = requests.post(
                SEARCH_URL,
                data=payload,
                headers=headers,
                timeout=DEFAULTS_TIMEOUT,
            )
        else:
            res = requests.post(
                SEARCH_URL,
                data=payload,
                headers=headers,
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

        for new in res.json().get("data", {}).get("publicationsGet", []):
            site_date = None
            try:
                site_date = dateparser.parse(new.get("publishedAt"))
                body.append({
                    "title": new.get("title"),
                    "href":  new['url'],
                    "date": site_date
                })
            except Exception:
                pass

            if site_date and site_date.date() < limit_date.date():
                return False, body, proxy
        return True, body, proxy

    elif res.status_code == 404:
        return False, body, proxy
    return True, body, proxy


def get_page(articles, article_body, proxy, attempt=0):
    photos = []
    sounds = []
    videos = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0',
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Referer': 'https://xn--80asmdh4e.xn--p1ai/2024/08/22/pomnim-proshloe-chtim-geroev-v-muzee-istorii-religii',
            'content-type': 'application/json',
            'Origin': 'https://xn--80asmdh4e.xn--p1ai',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=4'
        }
        payload = json.dumps({
            "operationName": "publicationsGet",
            "variables": {
                "url": article_body['href']
            },
            "query": "query publicationsGet($authorId: ID, $categoryIds: [ID!], $categoryUrl: String, $districtIds: [ID!], $districtPublication: Boolean, $ids: [ID!], $limit: Int, $mainline: Boolean, $offset: Int, $pressRelease: Boolean, $publishedAt: OrderDirection, $publishedAtGt: ISO8601Date, $publishedAtLt: ISO8601Date, $title: String, $urgent: Boolean, $url: String) {\n  publicationsGet(\n    authorId: $authorId\n    categoryIds: $categoryIds\n    categoryUrl: $categoryUrl\n    districtIds: $districtIds\n    districtPublication: $districtPublication\n    ids: $ids\n    limit: $limit\n    mainline: $mainline\n    offset: $offset\n    pressRelease: $pressRelease\n    publishedAt: $publishedAt\n    publishedAtGt: $publishedAtGt\n    publishedAtLt: $publishedAtLt\n    title: $title\n    urgent: $urgent\n    url: $url\n  ) {\n    ...Publication\n    __typename\n  }\n}\n\nfragment Publication on Publication {\n  author {\n    ...Author\n    __typename\n  }\n  authorId\n  categories {\n    ...Category\n    __typename\n  }\n  categoryIds\n  content\n  contentAttachmentIds\n  contentAttachments {\n    ...Attachment\n    __typename\n  }\n  cover {\n    ...Attachment\n    __typename\n  }\n  coverId\n  coverTitle\n  createdAt\n  description\n  districtIds\n  districtPublication\n  editorVersion\n  id\n  mainline\n  pressRelease\n  published\n  publishedAt\n  rssShow\n  title\n  updatedAt\n  urgent\n  url\n  __typename\n}\n\nfragment Author on Author {\n  fio\n  id\n  __typename\n}\n\nfragment Category on Category {\n  cover {\n    ...Attachment\n    __typename\n  }\n  coverId\n  createdAt\n  description\n  id\n  main\n  menu\n  name\n  position\n  shortName\n  subtitle\n  updatedAt\n  url\n  viewType\n  __typename\n}\n\nfragment Attachment on Attachment {\n  byteSize\n  contentType\n  createdAt\n  filename\n  id\n  mainVariantUrl\n  mainWebpVariantUrl\n  thumbnailVariantUrl\n  thumbnailWebpVariantUrl\n  url\n  __typename\n}"
        })
        if attempt == 0:

            res = requests.post(SEARCH_URL, headers=headers, data=payload,
                                # proxies=proxy.get(list(proxy.keys())[0]),
                                timeout=DEFAULTS_TIMEOUT
                                )
        else:
            res = requests.post(SEARCH_URL, headers=headers, data=payload,
                                proxies=proxy.get(list(proxy.keys())[0]),
                                timeout=DEFAULTS_TIMEOUT
                                )
        if res.ok:
            res_json = res.json()
            text = ""
            try:
                for d in res_json['data']['publicationsGet'][0]['content']:
                    for t in d.get('children'):
                        text += t['text']
                        text += "\r\n <br> "
            except Exception:
                pass
            try:
                try:
                    photos.append(PAGE_URL + res_json['data']['publicationsGet'][0]['cover']['url'])
                except:
                    pass
            except Exception:
                pass

            articles.append(
                {"date": article_body['date'],
                 "title": article_body['title'],
                 "text": text,
                 "photos": photos,
                 "href": PAGE_URL + article_body['href'],

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
    articles, proxy = parsing_raioni(datetime.strptime("21/08/2024", "%d/%m/%Y"), None)
    print(1)

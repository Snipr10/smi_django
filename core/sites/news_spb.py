import json
from datetime import datetime

import dateparser
import requests

from core.sites.utils import DEFAULTS_TIMEOUT, update_proxy

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"

REGS = {"https://admnews.ru/": "2",
        "https://krgv.ru/": "8",
        "https://petrogradnews.ru/": "14",
        "https://ksnews.ru/": "9",
        "https://news-kron.ru/": "10",
        "https://kurort-news.ru/": "11",
        "https://mr-news.ru/": "12",
        "https://nevnews.ru/": "13",
        # "http://xn--e1aqccgid7fsa.xn--p1ai/":"",
        "https://pd-news.ru/": "15",
        "https://primorsknews.ru/": "16",
        "https://pushkin-news.ru/": "17",
        "https://frunznews.ru/": "18",
        "https://news-centre.ru/": "19",
        "https://newskolpino.ru/": "7",
        "https://kirnews.ru/": "6",
        "https://kalininnews.ru/": "5",
        "https://vybnews.ru/": "4",
        "https://vonews.ru/": "3",
        }


def parsing_news_spb_ter(limit_date, proxy):
    all_articles = []
    is_oks = []
    for region in REGS:
        is_ok, articles, proxy = parsing_news_spb(region, limit_date, proxy)
        all_articles.append(articles)
        is_oks.append(is_ok)
    return all(is_ok), all_articles, proxy


def parsing_news_spb(region, limit_date, proxy):
    articles = []
    i = 0
    is_not_stopped, body, proxy = get_urls(region, limit_date, proxy)
    # if not is_not_stopped:
    #     return articles, proxy

    if len(body) == 0:
        return articles, proxy

    for article in body:
        print(f"parsing_news_spb {region}" + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(region, articles, article, proxy)
        except Exception:
            pass
    print("finish parsing_news_spb")
    return articles, proxy


def get_urls(region_url, limit_date, proxy, attempts=0):
    body = []
    region_url_graph = region_url +"api/graphql"
    headers = {
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/json',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"'
    }
    payload = json.dumps({"operationName": "publicationsShortGet",
                          "variables": {"limit": 100, "offset": 0, "publishedAt": "DESC", "districtIds": [REGS.get(region_url)],
                                        "pressRelease": False},
                          "query": "query publicationsShortGet($authorId: ID, $categoryIds: [ID!], $categoryUrl: String, $districtIds: [ID!], $ids: [ID!], $limit: Int, $mainline: Boolean, $offset: Int, $pressRelease: Boolean, $publishedAt: OrderDirection, $publishedAtGt: ISO8601Date, $publishedAtLt: ISO8601Date, $title: String, $url: String) {\n  publicationsGet(\n    authorId: $authorId\n    categoryIds: $categoryIds\n    categoryUrl: $categoryUrl\n    districtIds: $districtIds\n    ids: $ids\n    limit: $limit\n    mainline: $mainline\n    offset: $offset\n    pressRelease: $pressRelease\n    publishedAt: $publishedAt\n    publishedAtGt: $publishedAtGt\n    publishedAtLt: $publishedAtLt\n    title: $title\n    url: $url\n  ) {\n    ...PublicationShort\n    __typename\n  }\n}\n\nfragment PublicationShort on Publication {\n  authorId\n  categories {\n    cover {\n      url\n      __typename\n    }\n    id\n    name\n    __typename\n  }\n  cover {\n    url\n    __typename\n  }\n  description\n  districtIds\n  id\n  pressRelease\n  publishedAt\n  title\n  urgent\n  url\n  __typename\n}"})
    try:
        if attempts == 0:
            res = requests.post(region_url_graph,
                                headers=headers,
                                data=payload,
                                timeout=DEFAULTS_TIMEOUT
                                )
        else:
            res = requests.post(region_url_graph,
                                headers=headers,
                                data=payload,

                                proxies=proxy.get(list(proxy.keys())[0]),
                                timeout=DEFAULTS_TIMEOUT
                                )
    except Exception as e:
        print(f"attempt {attempts}, {e}, {proxy}")
        # logger.info(str(e))
        if attempts < 10:
            if attempts == 0:
                print("proxy")
                return get_urls(region_url, limit_date, proxy, attempts + 1)
            print("update_proxy")
            return get_urls(region_url, limit_date, update_proxy(proxy), attempts + 1)
        return False, [], proxy
    print(f"{region_url}: {res.status_code}")
    if res.ok:
        for article in (res.json().get("data") or {}).get('publicationsGet') or []:
            try:
                try:
                    date = dateparser.parse(article['publishedAt'])
                    if date < datetime(limit_date.year, limit_date.month, limit_date.day) and len(body) > 0:
                        continue
                except Exception as e:
                    print(e)

                body.append(
                    {
                        "href": article['url'],
                        "title": article['title'],
                    }
                )
            except Exception as e:
                print(e)

    elif res.status_code == 404:
        return True, [], proxy
    elif res.status_code == 502:
        if attempts < 10:
            return get_urls(region_url, limit_date, update_proxy(proxy), attempts + 1)
    return True, body, proxy


def get_page(region_url, articles, article_body, proxy, attempt=0):
    photos = []
    try:
        url = region_url +"api/graphql"
        headers = {
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36',
            'accept': '*/*',
            'content-type': 'application/json',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"'
        }
        payload = json.dumps({
            "operationName": "publicationsGet",
            "variables": {
                "url": article_body['href']
            },
            "query": "query publicationsGet($authorId: ID, $categoryIds: [ID!], $categoryUrl: String, $districtIds: [ID!], $ids: [ID!], $limit: Int, $mainline: Boolean, $offset: Int, $pressRelease: Boolean, $publishedAt: OrderDirection, $publishedAtGt: ISO8601Date, $publishedAtLt: ISO8601Date, $title: String, $url: String) {\n  publicationsGet(\n    authorId: $authorId\n    categoryIds: $categoryIds\n    categoryUrl: $categoryUrl\n    districtIds: $districtIds\n    ids: $ids\n    limit: $limit\n    mainline: $mainline\n    offset: $offset\n    pressRelease: $pressRelease\n    publishedAt: $publishedAt\n    publishedAtGt: $publishedAtGt\n    publishedAtLt: $publishedAtLt\n    title: $title\n    url: $url\n  ) {\n    ...Publication\n    __typename\n  }\n}\n\nfragment Publication on Publication {\n  author {\n    ...Author\n    __typename\n  }\n  authorId\n  categories {\n    ...Category\n    __typename\n  }\n  categoryIds\n  content\n  contentAttachmentIds\n  contentAttachments {\n    ...Attachment\n    __typename\n  }\n  cover {\n    ...Attachment\n    __typename\n  }\n  coverId\n  coverTitle\n  createdAt\n  description\n  districtIds\n  editorVersion\n  id\n  mainline\n  pressRelease\n  published\n  publishedAt\n  title\n  updatedAt\n  urgent\n  url\n  __typename\n}\n\nfragment Author on Author {\n  fio\n  id\n  __typename\n}\n\nfragment Category on Category {\n  cover {\n    ...Attachment\n    __typename\n  }\n  coverId\n  createdAt\n  description\n  id\n  main\n  menu\n  name\n  position\n  shortName\n  subtitle\n  updatedAt\n  url\n  viewType\n  __typename\n}\n\nfragment Attachment on Attachment {\n  byteSize\n  contentType\n  createdAt\n  filename\n  id\n  url\n  __typename\n}"
        })

        if attempt == 0:
            res = requests.post(url, headers=headers,
                                timeout=DEFAULTS_TIMEOUT, data=payload
                                )
        else:
            res = requests.post(url, headers=headers,
                                proxies=proxy.get(list(proxy.keys())[0]),
                                timeout=DEFAULTS_TIMEOUT, data=payload
                                )
        if res.ok:

            res_json = res.json()
            try:
                photos.append(region_url+res_json['data']['publicationsGet'][0]['cover']['url'])
            except Exception:
                pass
            try:
                text = res_json['data']['publicationsGet'][0]['description'] + "<br> \n"
            except Exception:
                text = ""
            for c in res_json['data']['publicationsGet'][0]['content']:
                text += c['children'][0]['text'] + "<br> \n"

            articles.append(
                {"date": dateparser.parse(res_json['data']['publicationsGet'][0]['createdAt']),
                 "title": res_json['data']['publicationsGet'][0]['title'],
                 "text": text.strip(),
                 "photos": photos,
                 "href": region_url + res_json['data']['publicationsGet'][0]['url']
                 })

            return True, articles, proxy
        return True, articles, proxy
    except Exception as e:
        if attempt > 3:
            return False, articles, proxy
        if attempt == 0:
            return get_page(region_url, articles, article_body, proxy, attempt + 1)
        return get_page(region_url, articles, article_body, update_proxy(proxy), attempt + 1)


if __name__ == '__main__':
    articles, proxy = parsing_news_spb("https://news-centre.ru/", datetime.strptime("04/12/2022", "%d/%m/%Y"), None)
    print(1)
from datetime import datetime
import dateparser
import requests
from bs4 import BeautifulSoup
from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://www.livejournal.com/tools/endpoints/rsearch"
PAGE_URL = "https://forpost-sz.ru"
SIZE = 100


def parsing_livejournal(keyword, limit_date, proxy, body):
    for p in range(20):
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
        res = requests.get(SEARCH_PAGE_URL,
                           headers={
                               'Accept': 'application/json, text/plain, */*',
                               'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                               'Connection': 'keep-alive',
                               'DNT': '1',
                               'Sec-Fetch-Dest': 'empty',
                               'Sec-Fetch-Mode': 'cors',
                               'Sec-Fetch-Site': 'same-origin',
                               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                               'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                               'sec-ch-ua-mobile': '?0',
                               'sec-ch-ua-platform': '"Linux"',
                           },
                           params={
                               "query": keyword,
                               "adult": 0,
                               "sort": "published",
                               "type": "post",
                               "size": SIZE,
                               "from": SIZE * page,
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
        articles = res.json().get("matches")
        for article in articles:
            try:
                article_date = datetime.utcfromtimestamp(article['published'])

                body.append(
                    {
                        "href": article['url'],
                        "date": article_date,
                        "title": article['subject']
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
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
        },
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )
        if res.ok:
            soup = BeautifulSoup(res.text)

            artice_content = soup.find("div", class_="aentry-post__content")
            if not artice_content:
                artice_content = soup.find("div", class_="entry-content")
                if not artice_content:
                    artice_content = soup.find("div", class_="b-singlepost-bodywrapper")
            if not artice_content:
                artice_content = soup
            for i in artice_content.find_all("img"):
                photos.append(i.get("src"))
            articles.append({"date": article_body['date'],
                             "title": article_body['title'],
                             "text": artice_content.text.strip() + "\r\n <br> ",
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
    parsing_livejournal("тест", datetime.strptime("01/03/2025", "%d/%m/%Y"), None, [])

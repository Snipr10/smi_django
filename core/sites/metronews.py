import dateparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from core.sites.utils import stop_proxy, update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://www.metronews.ru/ajax/materials/"

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.metronews.ru/novosti/',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'TE': 'trailers'
}

GET_PAGE_HEADERS = {
    'authority': 'metronews.ru',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'dnt': '1',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36'
}


def parsing_metronews(limit_date, proxy):
    print("parsing_metronews")
    print(limit_date)
    # first_request
    articles = []
    page = 1
    body = []
    is_parsing_url = True
    while page < 100 and is_parsing_url:
        try:
            time_stamp = int(body[-1]['date'].timestamp())
        except Exception:
            time_stamp = int((datetime.now() + timedelta(hours=4)).timestamp())

        is_parsing_url, body, proxy = get_urls(limit_date, proxy, body, time_stamp)
        page += 1
        print("parsing_metronews page" + str(page))

    i = 0
    for article in body:
        print("parsing_metronews " + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(limit_date, proxy, body, time_stamp, attempts=0):
    try:
        # ?SearchString=&skip=0&take=10&DateFrom=&DateTo=&IsInIssue=false&SortType=2&SortOrder=1"
        if attempts == 0:
            res = requests.get(SEARCH_PAGE_URL,
                               headers={
                                   "user-agent": USER_AGENT
                               },
                               params={"rubricId": 4142, "dateFrom": time_stamp},
                               # proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
        else:
            res = requests.get(SEARCH_PAGE_URL,
                               headers={
                                   "user-agent": USER_AGENT
                               },
                               params={"rubricId": 4142, "dateFrom": time_stamp},
                               proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
    except Exception as e:
        stop_proxy(proxy)
        # logger.info(str(e))
        if attempts < 10:
            return get_urls(limit_date, update_proxy(proxy), body, time_stamp, attempts + 1)
        return False, body, proxy
    if res.ok:
        soup = BeautifulSoup(res.text)

        for site in soup.find_all("div", {"class": "material_item"}):
            try:
                site_date = dateparser.parse(site.attrs['timestamp'])
            except Exception:
                site_date = None
            try:
                text = soup.find("div", {"class": "text"}).text.strip()
            except Exception:
                text = ''
            body.append({
                "title": site.find("h4").text.strip(),
                "href": site.find("a").get("href").replace("https://m.metronews.ru/", "https://metronews.ru/"),
                "date": site_date,
                "text": text,
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

            res = requests.get(url, headers=GET_PAGE_HEADERS,
                               # proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
        else:
            res = requests.get(url, headers=GET_PAGE_HEADERS,
                               proxies=proxy.get(list(proxy.keys())[0]),
                               timeout=DEFAULTS_TIMEOUT
                               )
        if res.ok:
            soup = BeautifulSoup(res.text)
            text = article_body['text']

            try:
                text += soup.find("div", {"id": "body-text-comp"}).text.strip()
            except Exception:
                pass
            try:
                for img in soup.find("div", {"class": "article-header main"}).find_all("img"):
                    photos.append(img.attrs.get("src", ""))
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
    a, b = parsing_metronews(datetime.strptime("18/01/2024", "%d/%m/%Y"), None)
    print(a)

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# radio
from datetime import datetime

import requests
from bs4 import BeautifulSoup, NavigableString

from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
RADIO_PAGE_URL = "https://www.rtr.spb.ru/radio/Default.asp?page=%s"
NEW_PAGE_URL = "news_detail.asp?id="
RADIO_URL = "https://www.rtr.spb.ru/radio/"


def parsing_radio_url(page, limit_date, proxy, body):
    try:
        res = requests.get(RADIO_PAGE_URL % page, headers={
            "user-agent": USER_AGENT
        },
            proxies=proxy.get(list(proxy.keys())[0]),
            timeout=DEFAULTS_TIMEOUT
        )
    except Exception:
        return parsing_radio_url(page, limit_date, update_proxy(proxy), body)
    print(res.status_code)

    if res.ok:
        new_datas = False
        soup = BeautifulSoup(res.text)
        tables = soup.find("p", {"align": "center"}).find_all("table", {"id": "AutoNumber5"})
        print("tables" + str(len(tables)))
        if len(tables) == 0:
            return False, body, False, proxy
        for table in tables:

            article_date = datetime.strptime(table.find("font", {"size": 1}).text, "%d-%m-%Y")
            print(article_date)
            print(limit_date)
            if article_date.date() >= limit_date.date():
                print(str(article_date) + str(limit_date))

                href = table.find("a", {"class": "base"}).attrs.get("href")
                body.append({"date": article_date, "href": href})
            else:
                new_datas = True
        if new_datas:
            return False, body, False, proxy

        return True, body, False, proxy
    else:
        return parsing_radio_url(page, limit_date, update_proxy(proxy), body)


def get_page(articles, url, limit_date, proxy, attempt=0):
    title = ""
    text = ""
    date = None
    photos = []
    videos = []
    sounds = []
    try:
        res = requests.get(RADIO_URL + url, headers={
            "user-agent": USER_AGENT
        },
            proxies=proxy.get(list(proxy.keys())[0]),
            timeout=DEFAULTS_TIMEOUT
        )
        if res.ok:
            print("res.status_code" + str(res.status_code))
            soup = BeautifulSoup(res.text)
            for face in soup.find_all("font", {"face": "Arial"}):
                if len(face.find_all("font", {"size": 1})) > 0:
                    date = datetime.strptime(face.find_all("font", {"size": 1})[-1].text, "%d-%m-%Y")
                    if date and date.date() >= limit_date.date():
                        title = face.find_all("font", {"size": 3})[-1].text.encode('ISO-8859-1').decode("windows-1251")
                        text = ''
                        for justify in face.find_all("p", {"align": "justify"}):
                            try:
                                for content in justify.contents:
                                    if isinstance(content, NavigableString):
                                        text += str(content).encode('ISO-8859-1').decode("windows-1251")
                            except Exception:
                                pass
                        articles.append({"date": date, "title": title, "text": text, "href": RADIO_URL + url,
                                         "photos": photos,
                                         "sounds": sounds,
                                         "videos": videos
                                         })
                        return False, articles, proxy
                    else:
                        return True, articles, proxy



            # res.text
            return False, articles, proxy
        return True, articles, proxy
    except Exception as e:
        if attempt > 2:
            return False, articles, proxy
        print(e)
        return get_page(articles, url, limit_date, update_proxy(proxy), attempt+1)


def parsing_radio(limit_date, proxy):
    is_not_stopped = True
    page = 1
    body = []
    last_page = None
    is_time = False
    while is_not_stopped:
        try:
            print(limit_date)
            is_not_stopped, body, is_time, proxy = parsing_radio_url(page, limit_date, proxy, body)
            page += 1
        except Exception:
            is_not_stopped = False
    articles = []
    print("articles" + str(len(body)))
    for article in body:
        try:
            is_time, articles, proxy = get_page(articles, article['href'], limit_date, proxy)
            # print(article)
            last_page = int(article['href'].split("id=")[-1])
        except Exception:
            pass
    if last_page is not None:
        try:
            last_page -= 1
            search_page = 0
            while not is_time and search_page < 10_000:
                is_time, articles, proxy = get_page(articles, NEW_PAGE_URL + str(last_page), limit_date, proxy)
                search_page += 1
                last_page -= 1
        except Exception:
            pass
    return articles, proxy

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_radio(datetime.strptime("21/12/2020", "%d/%m/%Y"), update_proxy(None))
    print(1)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# radio
from datetime import datetime

import requests
from bs4 import BeautifulSoup, NavigableString

from core.sites.utils import update_proxy, parse_date, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
RADIO_PAGE_URL = "https://echo.msk.ru/tags/3540/archive/%s/"
RADIO_URL = "https://echo.msk.ru"


def parsing_radio_url(page, limit_date, proxy, body):
    try:
        res = requests.get(RADIO_PAGE_URL % page, headers={
            "user-agent": USER_AGENT
        }, proxies=proxy.get(list(proxy.keys())[0]),
           timeout=DEFAULTS_TIMEOUT
        )
    except Exception:
        return parsing_radio_url(page, limit_date, update_proxy(proxy), body)
    if res.ok:
        soup = BeautifulSoup(res.text)
        this_page_time = parse_date(soup.find("div", {"class": "time_title"}).find("h2").text, "%d %m %Y")
        tables_rel = soup.find_all("div", {"class": "rel"})
        tables = []
        for table_rel in tables_rel:
            try:
                if len(table_rel.attrs['class']) == 1:
                    tables = table_rel.find_all("div", {"class": "preview newsblock iblock"})
                    tables += table_rel.find_all("div", {"class": "prevcontent"})

            except Exception:
                pass
        if len(tables) == 0:
            return False, body, False, proxy
        for table in tables:
            try:
                tabel_datetime = table.find("span", {"class": "datetime"}).attrs["title"]
            except Exception:
                tabel_datetime = table.find("span", {"class": "datetime"}).text
            if len(tabel_datetime.split(",")) < 2:
                article_date = datetime.strptime(
                    f"{this_page_time.day} {this_page_time.month} {this_page_time.year}, {tabel_datetime}",
                    "%d %m %Y, %H:%M")
            else:
                article_date = parse_date(tabel_datetime, "%d %m %Y, %H:%M")

            if article_date >= limit_date:
                try:
                    href = table.find("a", {"class": "view"}).attrs.get("href")
                except Exception:
                    href = table.find("a").attrs.get("href")
                body.append({"date": article_date, "href": href})
            else:
                return False, body, True, proxy
        return True, body, False, proxy
    else:
        return parsing_radio_url(page, limit_date, update_proxy(proxy), body)


def get_page(articles, article_body, limit_date, proxy):
    title = ""
    text = ""
    date = None
    photos = []
    videos = []
    sounds = []
    try:
        res = requests.get(RADIO_URL + article_body['href'], headers={
            "user-agent": USER_AGENT
        },
            proxies=proxy.get(list(proxy.keys())[0]),
            timeout=DEFAULTS_TIMEOUT
        )
        if res.ok:
            soup = BeautifulSoup(res.text)
            if "/news/" in article_body['href']:
                try:
                    date_class = soup.find("div", {"class": "date"})
                    article_date = parse_date(
                        f'{date_class.find("span").text.strip()}, {date_class.find("strong").text.strip()}',
                        "%d %m %Y, %H:%M")
                except Exception:
                    article_date = article_body["date"]
                title = soup.find("h1", {"itemprop": "headline"}).text.strip()
                for body_text in soup.find("div", {"itemprop": "articleBody"}).find_all("p"):
                    text += body_text.text.strip()
            else:
                try:
                    try:
                        date_class = soup.find("div", {"class": "date"})
                        article_date = parse_date(
                            f'{date_class.find("span").text.strip()}, {date_class.find("strong").text.strip()}',
                            "%d %m %Y, %H:%M")
                    except Exception:
                        article_date = article_body["date"]
                    try:
                        title = soup.find("h1", {"itemprop": "headline"}).text.strip()
                    except Exception:
                        title = soup.find("a", {"class": "name_prog red"}).text.strip()
                    try:
                        text = soup.find("div", {"class": "typical"}).text.strip()
                    except Exception:
                        pass
                    try:
                        sounds.append(RADIO_URL + soup.find("a", {"class": "load iblock"}).attrs['href'])
                    except Exception:
                        pass
                except Exception:
                    return False, articles, proxy
            try:
                videos.append(soup.find("iframe", {
                    "allow": "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"}).attrs[
                                  'src'])
            except Exception:
                pass
            articles.append({"date": article_date, "title": title, "text": text,
                             "href": RADIO_URL + article_body['href'],
                             "photos": photos,
                             "sounds": sounds,
                             "videos": videos
                             })
            return False, articles, proxy
        return True, articles, proxy
    except Exception:
        return get_page(articles, article_body, limit_date, update_proxy(proxy))


def parsing_radio_echo(limit_date, proxy):
    is_not_stopped = True
    page = 1
    body = []
    last_page = None
    is_time = False
    while is_not_stopped:
        try:
            is_not_stopped, body, is_time, proxy = parsing_radio_url(page, limit_date, proxy, body)
            page += 1
        except Exception:
            is_not_stopped = False
    articles = []
    for article in body:
        try:
            is_time, articles, proxy = get_page(articles, article, limit_date, proxy)
            # print(article)
        except Exception:
            pass
    return articles, proxy


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_radio_echo(datetime.strptime("21/07/2021", "%d/%m/%Y"), update_proxy(None))
    print(1)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import dateparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://www.fontanka.ru/cgi-bin/search.scgi"
PAGE_URL = "https://www.fontanka.ru"


def parsing_fontanka(keyword, limit_date, proxy, body):
    is_not_stopped, body, is_time, proxy = get_urls(keyword, limit_date, proxy, body, 1)
    articles = []
    i = 0
    print("parsing_fontanka" + str(len(body)))
    for article in body:
        print("parsing_fontanka " + str(i))
        i += 1
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    start_body_len = len(body)

    try:
        res = requests.get(SEARCH_PAGE_URL,
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={"query": keyword,
                                   "fdate": limit_date.date().strftime("%Y-%m-%d"),
                                   "tdate": date.today().strftime("%Y-%m-%d"),
                                   "offset": page,
                                   "sortt": "date"
                                   },
                           # proxies=proxy.get(list(proxy.keys())[0]),
                           # timeout=DEFAULTS_TIMEOUT
                           )
    except Exception as e:
        # logger.info(str(e))
        if attempts < 10:
            return get_urls(keyword, limit_date, update_proxy(proxy), body, page, attempts + 1)
        return False, body, False, proxy
    if res.ok:
        soup = BeautifulSoup(res.text)

        articles = soup.find_all("li")

        if len(articles) == 0:
            return True, body, False, proxy
        for article in articles:
            try:
                article_date = dateparser.parse(article.find("time").text)
                if page > 100:
                    return True, body, True, proxy
                for a in article.find_all("a"):
                    article_title_attrs = a.attrs

                    href = article_title_attrs.get("href")
                    # check url
                    try:
                        int(href.replace("/", ""))
                        if "https" in href:
                            print(article_title_attrs.get("href"))
                        else:
                            body.append(
                                {
                                    "href": article_title_attrs.get("href"),
                                    "date": article_date,
                                    "title": article_title_attrs.get("title")
                                }
                            )
                    except Exception:
                        pass
            except Exception:
                pass
        if start_body_len == len(body):
            return True, body, True, proxy
        return get_urls(keyword, limit_date, proxy, body, page + 1, attempts)
    elif res.status_code == 404:
        return False, body, False, proxy
    return False, body, False, proxy


def get_page(articles, article_body, proxy, attempt=0):
    photos = []
    sounds = []
    videos = []
    try:
        url = PAGE_URL + article_body['href']
        res = requests.get(url, headers={
            "user-agent": USER_AGENT
        },
                           # proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )
        if res.ok:
            soup_all = BeautifulSoup(res.text)
            text = ""
            # try:
            #     text = soup.find("div", {"class": "DFqb"}).contents[-1].text + "\n"
            # except Exception:
            #     pass
            soup = soup_all.find("article", {"itemscope": "itemscope"})

            try:
                title = soup.find("p", {"itemprop": "http://schema.org/headline"}).text
            except Exception:
                title = article_body['title']
            try:
                text += soup.select('div[class*="-"]')[0].find("p").text + "\r\n <br> "
            except Exception:
                pass
            try:
                for p in soup.find("section", {"itemprop": "articleBody"}).find_all("p"):
                    text += p.text + "\r\n <br> "
            except Exception:
                pass
            article_section = soup.find("section", {"itemprop": "articleBody"})
            for p in article_section.find_all("p"):
                text += p.text + "<br> \n"

            try:
                for img in article_section.find_all("picture"):
                    try:
                        photo = img.attrs['data-flickity-lazyload']
                        if photo not in photos:
                            photos.append(photo)
                    except Exception:
                        pass
            except Exception:
                pass
            if 'https://www.fontanka.ru/2021/09/13/70132682/' == url:
                print(url)
            if len(articles) > 14:
                print(url)

            try:
                for iframe in article_section.find_all("div"):
                    try:
                        iframe_data = iframe.find("iframe").attrs.get("src")
                        if iframe_data not in photos:
                            photos.append(iframe_data)
                    except Exception:
                        try:
                            iframe_data = iframe.find("a").attrs.get("href")
                            if iframe_data not in photos:
                                photos.append(iframe_data)
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                for video_ in article_section.find_all("video"):
                    try:
                        video_src = video_.find("source").attrs.get("src")
                        if video_src not in videos:
                            videos.append(video_src)
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                article_date = dateparser.parse(soup.find("span", {"itemprop": "datePublished"}).text)
            except Exception:
                article_date = article_body['date']
            articles.append({"date": article_date, "title": title, "text": text.strip(),
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
    parsing_fontanka("красота", datetime.strptime("01/10/2021", "%d/%m/%Y"), None, [])

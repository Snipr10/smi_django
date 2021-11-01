from datetime import datetime
import dateparser
import requests
from bs4 import BeautifulSoup
from core.sites.utils import update_proxy, DEFAULTS_TIMEOUT

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
SEARCH_PAGE_URL = "https://expertnw.com/search/"
PAGE_URL = "https://expertnw.com"


def parsing_expertnw(keyword, limit_date, proxy, body):
    is_not_stopped, body, is_time, proxy = get_urls(keyword, limit_date, proxy, body, 1)
    articles = []
    for article in body:
        if article["date"].date() >= limit_date.date():
            try:
                is_time, articles, proxy = get_page(articles, article, proxy)
            except Exception:
                pass

    return articles, proxy


def get_urls(keyword, limit_date, proxy, body, page, attempts=0):
    try:
        res = requests.get(SEARCH_PAGE_URL,
                           headers={
                               "user-agent": USER_AGENT
                           },
                           params={"q": keyword},
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )
    except Exception as e:
        # logger.info(str(e))
        if attempts < 10:
            return get_urls(keyword, limit_date, update_proxy(proxy), body, page, attempts + 1)
        return False, body, False, proxy
    if res.ok:
        soup = BeautifulSoup(res.text)
        articles = []
        try:
            articles = soup.find("div", class_="search-list").find_all("div", class_="search-item")
        except Exception:
            pass
        if len(articles) == 0:
            return True, body, False, proxy
        for article in articles:
            try:
                article_date = None
                for content in article.find("div", class_="search-item-type").contents:
                    try:
                        article_date_parse = dateparser.parse(str(content))
                        if article_date_parse is not None:
                            article_date = article_date_parse
                            break
                    except Exception:
                        pass
                article_title = article.find("a", class_="search-item-title")
                article_href_all = article_title.attrs.get('href')

                body.append(
                                {
                                    "href": article_href_all[:article_href_all.find('?sphrase_id')],
                                    "date": article_date,
                                    "title": article_title.text
                                }
                            )
            except Exception as e:
                pass
        return False, body, True, proxy
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
                           proxies=proxy.get(list(proxy.keys())[0]),
                           timeout=DEFAULTS_TIMEOUT
                           )
        if res.ok:
            soup = BeautifulSoup(res.text)

            try:
                article_image = soup.find("div", class_="article-main-img").find("img").attrs.get("src")
                if article_image:
                    photos.append(PAGE_URL + article_image)
            except Exception:
                pass

            article_section = soup.find("div", class_="section-main-box").find("div", class_="plain-text")

            try:
                text = article_section.find("div", class_="previews-text").text.replace(" ", "").strip() + "\r\n <br> "
            except Exception:
                text = ""

            for p in article_section.find_all("p"):
                text += p.text.replace(" ", "").strip() + "\r\n <br> "

            for image_block in article_section.find_all("div", class_="img-block"):
                try:
                    photos.append(PAGE_URL + image_block.find("img").attrs.get("src"))
                except Exception:
                    pass

            articles.append({"date": article_body['date'],
                             "title": article_body['title'],
                             "text": text.strip(),
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
    parsing_expertnw("спбгу", datetime.strptime("01/09/2020", "%d/%m/%Y"), None, [])

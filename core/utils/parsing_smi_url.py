import re

import requests
from bs4 import BeautifulSoup
from newspaper import Article
from newspaper.configuration import Configuration

from core.sites.utils import update_proxy, stop_proxy


URL_DICT = {
    "https://infoneva.ru/": {"title": ["title", {}], "text": ["div", {"class": "text-content"}]},
    "https://www.ntv.ru/": {"title": ["h1", {"itemprop": "headline"}], "text": ["div", {"class": "inpagebody"}]},
    "https://peterburg2.ru/": {"title": ["h1", {}], "text": ["span", {"class": "article-content"}],
                               "meta": ["p", {"class": "article-content"}]},
    # "https://lenta.ru/": {"title": ["h1", {}], "text": ["div", {"class": "topic-body"}],
    #                            "meta": ["div", {"class*=topic-header__title-yandex"}]},
    # "https://bloknot.ru/": {"title": ["h1", {}], "text": ["div", {"class": "article__content"}]}
    "https://spb.dixinews.ru/": {"title": ["h1", {}], "text": ["div", {"class": "entry-content"}], "wholetext": True},
    "https://ria.ru/": {"title": ["div", {"class": "article__title"}], "text": ["div", {"class": "article__body"}],
                        "meta": ["h1", {"class": "article__second-title"}]},
    "https://vedomosti-spb.ru/": {"title": ["h1", {"class": "article-headline__title"}],
                                  "text": ["div", {"class": "article-boxes-list article__boxes"}],
                                  "meta": ["div", {"class": "article-authors__info"}]},
    "https://live24.ru/": {"title": ["h1", {}],
                           "text": ["div", {
                               "class": "uk-panel uk-text-large uk-dropcap maintext uk-margin uk-width-2xlarge uk-margin-auto"}],
                           },
    "https://www.sobaka.ru/": {"title": ["h1", {"itemprop": "headline name"}],
                               "text": ["div", {"itemprop": "articleBody"}],
                               },
    "https://www.flashnord.com/": {"title": ["h1", {"class": "entry-title"}],
                                   "text": ["div", {"class": "entry-content"}],
                                   },
    "https://www.interfax-russia.ru/": {"title": ["div", {"itemprop": "headline"}],
                                        "text": ["div", {"itemprop": "articleBody"}],
                                        },
    "https://www.fontanka.ru/": {"title": ["h1", {}],
                                        "text": ["section", {"itemprop": "articleBody"}],
                                        },

}


def _get_page_data(url, attempts=0):
    proxy = None
    for k in URL_DICT.keys():
        if k in url:
            if attempts < 1:
                post = requests.get(url)
            else:
                proxy = update_proxy(proxy)
                post = requests.get(url, proxies=proxy.get(list(proxy.keys())[0]))
                stop_proxy(proxy, error=0, banned=0)

            soup = BeautifulSoup(post.text, 'html.parser')
            article_title = soup.find(name=URL_DICT.get(k).get("title")[0], attrs=URL_DICT.get(k).get("title")[1]).text
            text = ""
            try:
                if "meta" in URL_DICT.get(k).keys():
                    for c in soup.find(name=URL_DICT.get(k).get("meta")[0],
                                       attrs=URL_DICT.get(k).get("meta")[1]).contents:
                        try:
                            if c.text and c.text.strip():
                                text += c.text + "\r\n <br> "
                        except Exception:
                            pass
            except Exception:
                pass
            if URL_DICT.get(k).get("wholetext"):
                text += soup.find(name=URL_DICT.get(k).get("text")[0], attrs=URL_DICT.get(k).get("text")[1]).text
            else:
                for c in soup.find(name=URL_DICT.get(k).get("text")[0], attrs=URL_DICT.get(k).get("text")[1]).contents:
                    try:
                        if c.text and c.text.strip():
                            text += re.sub("\n+", "\n", c.text.strip()) + "\r\n <br> "
                    except Exception:
                        pass
            return article_title, text
    return "", ""


def parsing_smi_url(url, attempts=0):
    try:
        proxy = None
        h, text = _get_page_data(url, attempts=0)
        if h != "" and text != "":
            return text
        try:
            if attempts > 1:
                proxy = update_proxy(None)
                PROXIES = proxy.get(list(proxy.keys())[0])
                config = Configuration()
                config.proxies = PROXIES
                article = Article(url, config=config)
            else:
                article = Article(url)
            article.download()
            article.parse()
            title = article.title
            text = article.text or ""
            text_first_part = text[:len(title) * 3]
            if title in text_first_part:
                if len(text_first_part.replace(title + "\n", "")) != len(text_first_part):
                    text = text.replace(title + "\n", "", 1)
                else:
                    try:
                        first_par = text.split('\n')[0]
                        first_par_without_par = first_par.replace(title, "")
                        if "." not in first_par_without_par and "!" not in first_par_without_par and "?" not in first_par_without_par:
                            text = text.replace(title, "", 1)
                    except Exception:
                        pass
            text = re.sub("\n\n+", "\r\n <br> ", text)
            if article.meta_description.strip() not in text:
                text = article.meta_description.strip() + "\r\n <br> " + text
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
        text = ""
    if proxy is not None:
        stop_proxy(proxy, error=0, banned=0)

    if text == "" and attempts < 5:
        attempts += 1
        text = parsing_smi_url(url, attempts=attempts)
    return update_text(url, text)


def update_text(url, text):
    try:
        if 'https://www.kommersant.ru' in url:
            first = text.split("\n")[0].replace(" ", "")
            for d in '1234567890':
                first = first.replace(d, '')
            if first.strip() == "мин....":
                text = "\n\r".join(text.split("\n")[1:])
        return text
    except Exception:
        return text

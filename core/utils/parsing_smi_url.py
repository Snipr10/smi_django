import re

import requests
from bs4 import BeautifulSoup, NavigableString
from newspaper import Article
from newspaper.configuration import Configuration

from core.sites.utils import update_proxy, stop_proxy

URL_WITHOUT_META = ["https://lenta.ru"]

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
                               "class": re.compile('.*panel uk-text-large maintext.*')}],
                           "is_last": True
                           },
    # "https://www.sobaka.ru/": {"title": ["h1", {"itemprop": "headline name"}],
    #                            "text": ["div", {"itemprop": "articleBody"}],
    #                            },
    "https://www.flashnord.com/": {"title": ["h1", {"class": "entry-title"}],
                                   "text": ["div", {"class": "entry-content"}],
                                   },
    "https://www.interfax-russia.ru/": {"title": ["div", {"itemprop": "headline"}],
                                        "text": ["div", {"itemprop": "articleBody"}],
                                        },
    "https://www.fontanka.ru/": {"title": ["h1", {}],
                                 "text": ["section", {"itemprop": "articleBody"}],
                                 },
    "https://www.rtr.spb.ru/": {"title": ["font", {"class": "base"}],
                                "text": ["p", {"align": "justify"}],
                                "decoder": "windows-1251", "manual": True
                                },
    "https://spb.aif.ru/": {"title": ["h1", {}], "text": ["div", {"class": "article_text"}], "p": True, "next": True
                            },
    "https://galernayas.ru/": {"title": ["h2", {}], "text": ["div", {"style": "text-align:justify"}], "p": True,
                               },
    "https://novayagazeta.spb.ru/": {"title": ["h1", {}], "text": ["div", {"class": "article"}],
                               },
    "https://www.interessant.ru/": {"title": ["h1", {}], "text": ["div", {"class": "text"}],
                       "meta": ["h2", {}], "is_last": True},
    "https://www.lenpravda.ru/": {"title": ["div", {"class":"razdeltitle1"}], "text": ["div", {"class": "bodytext"}],
                                  "is_last": True},
    "https://info24.ru/": {"title": ["h1", {}], "meta": ["h3", {}], "text": ["div", {"class": "material-body"}],
                           "is_last": True},
    "http://www.assembly.spb.ru/": {"title": ["h2", {}], "text": ["article", {}],
                           "is_last": True},
    "https://govoritmoskva.ru/": {"title": ["h1", {}], "text": ["div", {"class": "textContent"}],
                                    "is_last": True},
    "https://smotrim.ru/": {"title": ["header", {"class":"article-main-item__header"}], "text": ["div", {"class": "article-main-item__body"}],
                                  "meta":["div", {"class":"article-main-item__anons"}],
                                  "is_last": True},
    "https://hudoznikov.ru/": {"title": ["h2", {}], "text": ["div", {"style": "text-align:justify"}],
                                  "is_last": True},
    "https://dorinfo.ru/": {"title": ["h1", {}],
                            "text": ["div", {"class": "fulltext"}],
                            "is_last": True},
    "https://www.flashnord.com/": {"title": ["h1", {}],
                            "text": ["div", {"class": "entry-content"}],
                            "is_last": True},
    "https://www.vedomosti.ru/": {"title": ["h1", {}],
                            "text": ["div", {"class": "article-boxes-list article__boxes"}],
                            "meta": ["em", {}],},
    # "https://novayagazeta.ru/": {"title": ["h1", {}],
    #                               "text": ["div", {"id": "materialBlock_0"}],
    #                             },
    "https://mir24.tv/": {"title": ["h1", {}],
                                 "text": ["div", {"class": "article-content"}], "p": True, "next": True
                                 },
    "https://mos.news/": {"title": ["h1", {}],
                          "text": ["div", {"class": "detail_text_container"}],  "decoder": "windows-1251",  "next": True
                          },
    "https://delta.news/": {"title": ["h5", {"class":"white-text grey darken-2"}],
                          "text": ["article", {"class": "card"}], "next": True,
                            "delete_title": True
                          },
    "https://spb.octagon.media/": {"title": ["h1", {}],
                            "text": ["article", {}], "p": True,
                            "delete_title": True
                            },
    "https://bloknot.ru/": {"title": ["h1", {}],
                                   "text": ["div", {"class":"article__content"}], "p": True,
                                   "delete_title": True, "next": True
                                   },
    "https://www.sobaka.ru/": {"title": ["h1", {}],
                                   "text": ["div", {"class":"b-post-blocks"}], "p": True,
                                   }
}


def _get_page_data(url, attempts=0):
    proxy = None
    for k in URL_DICT.keys():
        if k in url:
            if attempts < 1:
                try:
                    post = requests.get(url)
                except Exception:
                    post = requests.get(url, headers={
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
                    })
            else:
                proxy = update_proxy(proxy)
                try:
                    post = requests.get(url, proxies=proxy.get(list(proxy.keys())[0]))
                except Exception:
                    post = requests.get(url, proxies=proxy.get(list(proxy.keys())[0]),  headers={
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
                    })

                stop_proxy(proxy, error=0, banned=0)

            if URL_DICT.get(k).get("decoder"):
                soup = BeautifulSoup(post.content.decode(URL_DICT.get(k).get("decoder")))
            else:
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
                soup_all = soup.find_all(name=URL_DICT.get(k).get("text")[0], attrs=URL_DICT.get(k).get("text")[1])
                if URL_DICT.get(k).get("is_last", False):
                    soup_cont = soup_all[-1]
                else:
                    soup_cont = soup_all[0]
                text = ""

                if URL_DICT.get(k).get("manual", False):
                    for c in soup_cont.contents[0].contents:
                        if isinstance(c, NavigableString) or len(c.attrs) == 0:
                            text += str(c)
                        else:
                            break
                else:
                    if URL_DICT.get(k).get("p", False):
                        for c in soup_cont.find_all("p"):
                            try:
                                if URL_DICT.get(k).get("next", False):
                                    if c.next and c.next.strip():
                                        text += re.sub("\n+", "\n", c.next.strip()) + "\r\n <br> "
                                else:
                                    if c.text and c.text.strip():
                                        text += re.sub("\n+", "\n", c.text.strip()) + "\r\n <br> "
                            except Exception:
                                pass
                    else:
                        for c in soup_cont.contents:
                            try:
                                if c.text and c.text.strip():
                                    text += re.sub("\n+", "\n", c.text.strip()) + "\r\n <br> "
                            except Exception:
                                pass
            if URL_DICT.get(k).get("delete_title", False):
                try:
                    text = text.replace(article_title.strip(), "").strip()
                except Exception:
                    pass
            return article_title, text
    return "", ""


def parsing_smi_url(url, attempts=0):
    if "https://glasnarod.ru/" in url:
        return None
    if "https://vz.ru/" in url:
        return None
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
            if len([s for s in URL_WITHOUT_META if s in url]) == 0 and article.meta_description.strip() not in text:
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

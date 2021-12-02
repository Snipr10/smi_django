import re
from newspaper import Article
from newspaper.configuration import Configuration

from core.sites.utils import update_proxy, stop_proxy


def parsing_smi_url(url, attempts =0):
    try:
        proxy = None
        text = ""
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

    if text == "" and attempts < 10:
        attempts += 1
        text = parsing_smi_url(url, attempts=attempts)
    return text


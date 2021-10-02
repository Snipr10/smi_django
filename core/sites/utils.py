import time
import random
import hashlib
import django.db
import datetime

from django.db.models import Q
from django.utils import timezone
import datetime

from core import models

batch_size = 1000
first_date = "01/01/2021"
DEFAULTS_TIMEOUT = 100


def update_proxy(proxy):
    try:
        stop_proxy(list(proxy.keys())[0], error=1)
    except Exception:
        pass
    return get_proxy()


def get_md5_text(text):
    if text is None:
        text = ''
    m = hashlib.md5()
    m.update(text.encode())
    return str(m.hexdigest())


def get_sphinx_id(url):
    m = hashlib.md5()
    m.update(url.encode())
    return int(str(int(m.hexdigest()[:16], 16))[:16])


def parse_date(s_date, format):
    splint_date = s_date.split(" ")
    splint_date[1] = month_from_ru_to_eng(splint_date[1])
    str_date = ""
    for d in splint_date:
        str_date += " " + d
    str_date = str_date.strip()

    return datetime.datetime.strptime(str_date, format)


def month_from_ru_to_eng(month):
    out = month
    if 'дек' in month:
        out = '12'
    elif 'янв' in month:
        out = '1'
    elif 'фев' in month:
        out = '2'
    elif 'мар' in month:
        out = '3'
    elif 'апр' in month:
        out = '4'
    elif 'ма' in month:
        out = '5'
    elif 'июн' in month:
        out = '6'
    elif 'июл' in month:
        out = '7'
    elif 'авг' in month:
        out = '8'
    elif 'сент' in month:
        out = '9'
    elif 'окт' in month:
        out = '10'
    elif 'ноя' in month:
        out = '11'
    return out


def get_or_create_author(display_link):
    usernames = {
        "https://www.svoboda.org": "Радио Свобода",
        "https://www.radiozenit.ru/": "Радио Зенит",
        "https://www.rtr.spb.ru/radio/": "Радио России - Санкт-Петербург",
        "https://echo.msk.ru": "Радио Эхо Москвы",

    }
    images = {
        "https://www.svoboda.org": "https://www.svoboda.org/Content/responsive/RFE/ru-RU/img/logo.svg",
        "https://www.radiozenit.ru/": "https://www.radiozenit.ru/design/images/new-site--tmp/logo.svg",
        "https://www.rtr.spb.ru/radio/": "https://www.rtr.spb.ru/images/vesti/lognew/vesti_sin.jpg",
        "https://echo.msk.ru": "https://echomsk.static-storage.net/Eg4gT0209/a47fd3HZi/37pnEFqk3f5_xqthoMRiXuoEeTmMzAZs7nqlRf0AaH0LvdWhk7O_LJ_fpYVU10_ih7t_JQyRkTlMwB2hxyQaH7eyfoWamBlmQ-dTSTxlljKzdMxFRKSewIKmbQnZ-LAV70mx1R9z0ym7H_m1hOMjQmeLZ0EYhR2peGBZND9UPiq3ogJNp7h90lN3Sx3IOfKaj5gMxUSMIgCe1o2FAdz46VNZiVnziw-lj4uhUUA38_7P-_OlLD25yZAk-UC31D5mK0bOtbscnRrjE1cRYM3Guuvw_M3QSC5gwpZ1BR2gtK3jhc3x3-9X1UN7vQ14I8-mg1-PfeTFCUX8SHHUw1jiqt8eBqFT-M2ut0cfgfztslor3EhFDGjifC52sQVtuCzhO4k5DQOr_93jO0XVrKPvbpPLq2A",

    }

    author = models.PostAuthor.objects.filter(url=display_link).first()
    if author is not None:
        return author
    author = models.PostAuthor.objects.filter(id=display_link).first()
    if author is not None:
        return author
    author = models.PostAuthor.objects.create(
        profile_id=get_sphinx_id(display_link),
        url=display_link,
        username=usernames.get(display_link),
        federal=0,
        image=images.get(display_link),
        followers=0
    )
    return author


def save_articles(display_link, articles):
    posts = []
    posts_content = []
    # photos_content = []
    # videos_content = []
    # sounds_content = []
    django.db.close_old_connections()

    for article in articles:
        print(article.get('href'))
        author = get_or_create_author(display_link)
        text = article.get('text')
        image = ""
        for photo in article['photos']:
            image = photo
            text += "\n" + photo
        for video in article['videos']:
            text += "\n" + video
        for sound in article['sounds']:
            text += "\n" + sound
        cache_id = get_sphinx_id(article.get('href'))

        posts.append(models.Post(
            cache_id=cache_id,
            owner_sphinx_id=author.profile_id,
            created=article.get('date'),
            display_link=display_link,
            owner=author.username,
            title=article.get('title'),
            link=article.get('href'),
            image=image,
            keyword_id=0,
            trust=0
        ))

        posts_content.append(models.PostContent(
            content=text,
            cache_id=cache_id,
            keyword_id=10000002,

        ))

    models.Post.objects.bulk_create(posts, batch_size=batch_size, ignore_conflicts=True)
    models.PostContent.objects.bulk_create(posts_content, batch_size=batch_size, ignore_conflicts=True)


def get_late_date(display_link):
    last_post = models.Post.objects.filter(display_link=display_link).order_by("-created").first()
    if last_post is None:
        min_date = datetime.datetime.strptime(first_date, "%d/%m/%Y")
    else:
        min_date = last_post.created
    return min_date


def get_proxy():
    try:
        time.sleep(random.randint(0, 10) / 10)
        added_proxy_list = list(models.Proxy.objects.all().values_list('id', flat=True))

        proxy = models.AllProxy.objects.filter(~Q(id__in=added_proxy_list), ~Q(port=0), ip__isnull=False,
                                               login__isnull=False).last()

        if proxy is not None:
            new_proxy = models.Proxy.objects.create(id=proxy.id)
            proxies = get_proxies(new_proxy)
            return {new_proxy: proxies}

        used_proxy = models.Proxy.objects.filter(banned=False,
                                                 last_used__lte=update_time_timezone(
                                                     timezone.localtime()
                                                 ) - datetime.timedelta(minutes=5)).order_by('taken',
                                                                                             'last_used').first()

        if used_proxy is None:
            used_proxy = models.Proxy.objects.filter(
                last_used__lte=update_time_timezone(
                    timezone.localtime()
                ) - datetime.timedelta(minutes=5)).order_by('taken', 'last_used').first()
        if used_proxy is not None:
            used_proxy.taken = True
            used_proxy.save(update_fields=['taken'])
            proxies = get_proxies(used_proxy)
            if proxies is None:
                used_proxy.banned = True
                used_proxy.save(update_fields=['banned'])
                return get_proxy()
            else:
                return {used_proxy: proxies}
        return {None: None}
    except Exception as e:
        print(e)
        return get_proxy()


def stop_proxy(proxy, error=0, banned=0):
    proxy = list(proxy.keys())[0]
    try:
        if error:
            proxy.errors = proxy.errors + 1

        proxy.taken = 0
        proxy.banned = banned
        proxy.last_used = update_time_timezone(timezone.localtime())
        proxy.save()
    except Exception as e:
        print("stop_proxy" + str(e))


def get_proxies(proxy):
    proxy_info = models.AllProxy.objects.filter(id=proxy.id).first()
    if proxy_info is not None:
        return format_proxies(proxy_info)
    return None


def format_proxies(proxy_info):
    return {'http': 'http://{}:{}@{}:{}'.format(proxy_info.login, proxy_info.proxy_password, proxy_info.ip,
                                                str(proxy_info.port)),
            'https': 'http://{}:{}@{}:{}'.format(proxy_info.login, proxy_info.proxy_password, proxy_info.ip,
                                                 str(proxy_info.port))
            }


def add_error(proxy):
    proxy.errors = proxy.errors + 1
    if proxy.errors > 10:
        proxy.banned = True
    proxy.taken = False
    proxy.last_used = update_time_timezone(timezone.localtime())
    proxy.save()


def update_time_timezone(my_time):
    return my_time + datetime.timedelta(hours=3)

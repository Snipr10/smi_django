import hashlib
import django.db

from datetime import datetime
from core import models

batch_size = 1000
first_date = "01/01/2021"


def update_proxy(proxy):
    return proxy


def stop_proxy(proxy):
    return proxy


def get_md5_text(text):
    if text is None:
        text = ''
    m = hashlib.md5()
    m.update(text.encode())
    return str(m.hexdigest())


def get_sphinx_id(url):
    m = hashlib.md5()
    m.update(url.encode())
    return int(str(int(m.hexdigest(), 16))[:16])


def parse_date(s_date, format):
    splint_date = s_date.split(" ")
    splint_date[1] = month_from_ru_to_eng(splint_date[1])
    str_date = ""
    for d in splint_date:
        str_date += " " + d
    str_date = str_date.strip()

    return datetime.strptime(str_date, format)


def month_from_ru_to_eng(month):
    out = month
    if 'дек' in month: out = '12'
    elif 'янв' in month: out = '1'
    elif 'фев' in month: out = '2'
    elif 'мар' in month: out = '3'
    elif 'апр' in month: out = '4'
    elif 'ма' in month: out = '5'
    elif 'июн' in month: out = '6'
    elif 'июл' in month: out = '7'
    elif 'авг' in month: out = '8'
    elif 'сент' in month: out = '9'
    elif 'окт' in month: out = '10'
    elif 'ноя' in month: out = '11'
    return out


def save_articles(display_link, articles):
    posts = []
    posts_content = []
    photos_content = []
    videos_content = []
    sounds_content = []
    django.db.close_old_connections()

    for article in articles:
        text = article.get('text')
        cache_id = get_sphinx_id(article.get('href'))
        posts.append(models.Post(
            created_date=article.get('date'),
            url=article.get('href'),
            display_link=display_link,
            title=article.get('title'),
            content_hash=get_md5_text(text),
            cache_id=cache_id
        ))
        posts_content.append(models.PostContent(
            content=text,
            cache_id=cache_id
        ))
        for photo in article['photos']:
            photos_content.append(models.PostPhoto(
                photo_url=photo,
                cache_id=cache_id
            ))
        for video in article['videos']:
            videos_content.append(models.PostVideo(
                video_url=video,
                cache_id=cache_id
            ))
        for sound in article['sounds']:
            sounds_content.append(models.PostSound(
                sound_url=sound,
                cache_id=cache_id
            ))
    models.Post.objects.bulk_create(posts, batch_size=batch_size, ignore_conflicts=True)
    models.PostContent.objects.bulk_create(posts_content, batch_size=batch_size, ignore_conflicts=True)
    models.PostPhoto.objects.bulk_create(photos_content, batch_size=batch_size, ignore_conflicts=True)
    models.PostVideo.objects.bulk_create(videos_content, batch_size=batch_size, ignore_conflicts=True)
    models.PostSound.objects.bulk_create(sounds_content, batch_size=batch_size, ignore_conflicts=True)


def get_late_date(display_link):
    last_post = models.Post.objects.filter(display_link=display_link).order_by("-created_date").first()
    if last_post is None:
        min_date = datetime.strptime(first_date, "%d/%m/%Y")
    else:
        min_date = last_post.created_date
    return min_date

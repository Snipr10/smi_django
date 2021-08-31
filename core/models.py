import pytz

from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

# Create your models here.


class AllProxy(models.Model):
    ip = models.CharField(max_length=256)
    port = models.IntegerField()
    login = models.CharField(max_length=256)
    proxy_password = models.CharField(max_length=256)
    # last_used = models.DateTimeField(null=True, blank=True)
    # last_used_y = models.DateTimeField(null=True, blank=True)
    failed = models.IntegerField()
    errors = models.IntegerField()
    foregin = models.IntegerField()
    banned_fb = models.IntegerField()
    banned_y =models.IntegerField()
    banned_tw = models.IntegerField()
    # valid_untill = models.DateTimeField(default=datetime.now()+timedelta(days=5))
    timezone = models.CharField(max_length=256)
    v6 = models.IntegerField()
    # last_modified = models.DateTimeField(null=True, blank=True)
    checking = models.BooleanField()

    class Meta:
        db_table = 'prsr_parser_proxy'


class Proxy(models.Model):
    id = models.IntegerField(primary_key=True)
    taken = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    errors = models.IntegerField(default=0)
    banned = models.BooleanField(default=False)

    class Meta:
        db_table = 'prsr_parser_proxy_smi'


class PostAuthor(models.Model):
    profile_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    federal = models.IntegerField()
    followers = models.IntegerField()

    class Meta:
        db_table = 'prsr_parser_global_authors'


class Post(models.Model):
    cache_id = models.IntegerField(primary_key=True)
    owner_sphinx_id = models.IntegerField()
    created_date = models.DateTimeField(null=True, blank=True)
    display_link = models.CharField(max_length=255, null=True, blank=True)
    owner = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    keyword_id = models.IntegerField(default=0)
    trust = models.IntegerField(default=0)
    update = models.DateTimeField(auto_now_add=True)
    found_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'prsr_parser_global_posts'


class PostContent(models.Model):
    cache_id = models.IntegerField(primary_key=True)
    content = models.CharField(max_length=4096, null=True, blank=True)
    keyword_id = models.IntegerField(default=0)

    class Meta:
        db_table = 'prsr_parser_global_post_kw_content'


# class Post(models.Model):
#     cache_id = models.IntegerField(primary_key=True)
#     created_date = models.DateTimeField(null=True, blank=True)
#     found_date = models.DateField(auto_now_add=True)
#     last_modified = models.DateTimeField(default=datetime(1, 1, 1, 0, 0, tzinfo=pytz.UTC), null=True, blank=True)
#     content_hash = models.CharField(max_length=255, null=True, blank=True)
#     url = models.CharField(max_length=255, null=True, blank=True)
#     display_link = models.CharField(max_length=255, null=True, blank=True)
#     title = models.CharField(max_length=255, null=True, blank=True)
#
#     class Meta:
#         db_table = 'prsr_parser_smi_posts'
#
#
# class PostContent(models.Model):
#     cache_id = models.IntegerField(primary_key=True)
#     content = models.CharField(max_length=4096, null=True, blank=True)
#
#     class Meta:
#         db_table = 'prsr_parser_smi_content'
#
#
# class PostPhoto(models.Model):
#     cache_id = models.IntegerField(primary_key=True)
#     photo_url = models.CharField(max_length=255, null=True, blank=True)
#
#     class Meta:
#         db_table = 'prsr_parser_smi_photo'
#
#
# class PostVideo(models.Model):
#     cache_id = models.IntegerField(primary_key=True)
#     video_url = models.CharField(max_length=255, null=True, blank=True)
#
#     class Meta:
#         db_table = 'prsr_parser_smi_video'
#
#
# class PostSound(models.Model):
#     cache_id = models.IntegerField(primary_key=True)
#     sound_url = models.CharField(max_length=255, null=True, blank=True)
#
#     class Meta:
#         db_table = 'prsr_parser_smi_sound'

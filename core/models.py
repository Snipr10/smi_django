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
    created = models.DateTimeField(null=True, blank=True)
    display_link = models.CharField(max_length=255, null=True, blank=True)
    owner = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    keyword_id = models.IntegerField(default=0)
    trust = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now_add=True)
    found_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'prsr_parser_global_posts'


class GlobalSite(models.Model):
    site_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    is_keyword = models.IntegerField()
    last_parsing = models.DateTimeField(auto_now_add=True)
    taken = models.IntegerField()

    class Meta:
        db_table = 'prsr_parser_global_sites'


class PostContent(models.Model):
    cache_id = models.IntegerField(primary_key=True)
    content = models.CharField(max_length=4096, null=True, blank=True)
    keyword_id = models.IntegerField(default=10000002)

    class Meta:
        db_table = 'prsr_parser_global_post_kw_content'


class Keyword(models.Model):
    id = models.IntegerField(primary_key=True)
    network_id = models.IntegerField(default=0)
    keyword = models.CharField(default='nexta_live', max_length=4096)
    enabled = models.IntegerField(default=0)
    depth = models.DateField(null=True, blank=True)
    taken = models.BooleanField(default=0)
    reindexing = models.BooleanField(default=0)
    forced = models.BooleanField(default=0)
    disabled = models.BooleanField(default=0)

    class Meta:
        db_table = 'prsr_parser_keywords'


# class SiteKeyword(models.Model):
#     site_id = models.IntegerField()
#     keyword_id = models.IntegerField()
#     last_parsing = models.DateTimeField(default=datetime(2000, 1, 1, 0, 0, tzinfo=pytz.UTC))
#     taken = models.BooleanField(default=0)
#     is_active = models.BooleanField(default=1)
#
#     class Meta:
#         db_table = 'prsr_parser_global_sites_keyword'


class SiteKeywordNew(models.Model):
    class Meta:
        unique_together = (('keyword_id', 'site_id'),)
        db_table = 'prsr_parser_global_sites_keyword_1'
    site_id = models.IntegerField()
    keyword_id = models.IntegerField(primary_key=True)
    last_parsing = models.DateTimeField(default=datetime(2000, 1, 1, 0, 0, tzinfo=pytz.UTC))
    taken = models.BooleanField(default=0)
    is_active = models.BooleanField(default=1)


class KeywordSource(models.Model):
    keyword_id = models.IntegerField(primary_key=True)
    source_id = models.IntegerField()

    class Meta:
        db_table = 'prsr_parser_source_keywords'


class Sources(models.Model):
    uid = models.IntegerField(default=0)
    published = models.IntegerField(default=1)
    status = models.BooleanField(default=0)
    type = models.CharField(default="profiles", max_length=4096)
    retro = models.DateField(null=True, blank=True)
    retro_max = models.DateField(null=True, blank=True)
    networks = models.IntegerField(default=0)
    # last_modify = models.DateTimeField(null=True, blank=True)
    # links_modify = models.DateTimeField(null=True, blank=True)
    # n2_modify = models.DateTimeField(null=True, blank=True)
    taken = models.BooleanField(default=1)
    linking = models.BooleanField(default=0)
    sources = models.IntegerField(default=15)
    profiles = models.IntegerField(default=15)
    stats_params = models.CharField(null=True, blank=True, max_length=4096)

    class Meta:
        db_table = 'prsr_parser_sources'



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

# Generated by Django 3.1.4 on 2021-08-29 06:37

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AllProxy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=256)),
                ('port', models.IntegerField()),
                ('login', models.CharField(max_length=256)),
                ('proxy_password', models.CharField(max_length=256)),
                ('failed', models.IntegerField()),
                ('errors', models.IntegerField()),
                ('foregin', models.IntegerField()),
                ('banned_fb', models.IntegerField()),
                ('banned_y', models.IntegerField()),
                ('banned_tw', models.IntegerField()),
                ('timezone', models.CharField(max_length=256)),
                ('v6', models.IntegerField()),
                ('checking', models.BooleanField()),
            ],
            options={
                'db_table': 'prsr_parser_proxy',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('cache_id', models.IntegerField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('found_date', models.DateField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(blank=True, default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=utc), null=True)),
                ('content_hash', models.CharField(blank=True, max_length=32, null=True)),
                ('url', models.CharField(blank=True, max_length=255, null=True)),
                ('display_link', models.CharField(blank=True, max_length=255, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'prsr_parser_smi_posts',
            },
        ),
        migrations.CreateModel(
            name='PostContent',
            fields=[
                ('cache_id', models.IntegerField(primary_key=True, serialize=False)),
                ('content', models.CharField(blank=True, max_length=4096, null=True)),
            ],
            options={
                'db_table': 'prsr_parser_smi_content',
            },
        ),
        migrations.CreateModel(
            name='PostPhoto',
            fields=[
                ('cache_id', models.IntegerField(primary_key=True, serialize=False)),
                ('photo_url', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'prsr_parser_smi_photo',
            },
        ),
        migrations.CreateModel(
            name='PostSound',
            fields=[
                ('cache_id', models.IntegerField(primary_key=True, serialize=False)),
                ('sound_url', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'prsr_parser_smi_sound',
            },
        ),
        migrations.CreateModel(
            name='PostVideo',
            fields=[
                ('cache_id', models.IntegerField(primary_key=True, serialize=False)),
                ('photo_url', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'prsr_parser_smi_video',
            },
        ),
        migrations.CreateModel(
            name='Proxy',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('taken', models.BooleanField(default=True)),
                ('last_used', models.DateTimeField(blank=True, null=True)),
                ('errors', models.IntegerField(default=0)),
                ('banned', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'prsr_parser_proxy_smi',
            },
        ),
    ]
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiActions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('desc', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=50)),
                ('params', models.TextField(null=True, blank=True)),
                ('max_requests', models.IntegerField(null=True, blank=True)),
                ('recover_interval', models.IntegerField(null=True, blank=True)),
                ('recover_count', models.IntegerField(null=True, blank=True)),
                ('request_remain', models.IntegerField(null=True, blank=True)),
                ('last_request', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ApiCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('desc', models.CharField(max_length=20)),
                ('uri', models.CharField(max_length=100)),
                ('version', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('cn', models.CharField(max_length=10)),
                ('en', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='MarketAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.CharField(max_length=50)),
                ('auth_token', models.CharField(max_length=15)),
                ('access_key_id', models.CharField(max_length=25)),
                ('secret_key', models.CharField(max_length=50)),
                ('market_id', models.CharField(max_length=20)),
                ('country', models.ForeignKey(to='amazon_services.Market')),
            ],
        ),
        migrations.CreateModel(
            name='RequestRecords',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.CharField(max_length=100)),
                ('action_name', models.CharField(max_length=50, null=True, blank=True)),
                ('params', models.TextField(null=True, blank=True)),
                ('create_time', models.DateTimeField()),
                ('sent_time', models.DateTimeField(null=True, blank=True)),
                ('result', models.IntegerField(default=0)),
                ('action', models.ForeignKey(related_name='records', to='amazon_services.ApiActions')),
                ('market', models.ForeignKey(to='amazon_services.MarketAccount')),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='apiactions',
            name='category',
            field=models.ForeignKey(related_name='actions', to='amazon_services.ApiCategory'),
        ),
    ]

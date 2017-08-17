# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20170727_2311'),
    ]

    operations = [
        migrations.AddField(
            model_name='inboundshipment',
            name='settlement_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='outboundshipment',
            name='settlement_id',
            field=models.IntegerField(default=0),
        ),
    ]

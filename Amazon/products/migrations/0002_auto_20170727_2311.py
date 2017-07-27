# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outboundshipment',
            name='unit_freight',
        ),
        migrations.RemoveField(
            model_name='outboundshipmentitem',
            name='QuantityInCase',
        ),
        migrations.RemoveField(
            model_name='outboundshipmentitem',
            name='QuantityReceived',
        ),
        migrations.RemoveField(
            model_name='outboundshipmentitem',
            name='logistics_company',
        ),
        migrations.RemoveField(
            model_name='outboundshipmentitem',
            name='logistics_id',
        ),
        migrations.RemoveField(
            model_name='outboundshipmentitem',
            name='package_height',
        ),
        migrations.RemoveField(
            model_name='outboundshipmentitem',
            name='package_length',
        ),
        migrations.RemoveField(
            model_name='outboundshipmentitem',
            name='package_weight',
        ),
        migrations.RemoveField(
            model_name='outboundshipmentitem',
            name='package_width',
        ),
        migrations.AddField(
            model_name='outboundshipment',
            name='auto_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='outboundshipment',
            name='duty',
            field=models.FloatField(null=True, verbose_name='\u603b\u5173\u7a0e', blank=True),
        ),
        migrations.AddField(
            model_name='outboundshipment',
            name='logistics_company',
            field=models.CharField(max_length=100, null=True, verbose_name='\u7269\u6d41\u516c\u53f8\u540d\u79f0', blank=True),
        ),
        migrations.AddField(
            model_name='outboundshipment',
            name='logistics_id',
            field=models.CharField(max_length=100, null=True, verbose_name='\u7269\u6d41\u8fd0\u5355\u53f7', blank=True),
        ),
        migrations.AddField(
            model_name='outboundshipmentitem',
            name='height',
            field=models.FloatField(null=True, verbose_name='\u5546\u54c1\u9ad8\u5ea6', blank=True),
        ),
        migrations.AddField(
            model_name='outboundshipmentitem',
            name='length',
            field=models.FloatField(null=True, verbose_name='\u5546\u54c1\u957f\u5ea6', blank=True),
        ),
        migrations.AddField(
            model_name='outboundshipmentitem',
            name='unit_price',
            field=models.FloatField(null=True, verbose_name='\u5546\u54c1\u5355\u4ef7', blank=True),
        ),
        migrations.AddField(
            model_name='outboundshipmentitem',
            name='unit_weight',
            field=models.FloatField(null=True, verbose_name='\u4f53\u79ef\u53c2\u6570', blank=True),
        ),
        migrations.AddField(
            model_name='outboundshipmentitem',
            name='weight',
            field=models.FloatField(null=True, verbose_name='\u5546\u54c1\u91cd\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='outboundshipmentitem',
            name='width',
            field=models.FloatField(null=True, verbose_name='\u5546\u54c1\u5bbd\u5ea6', blank=True),
        ),
        migrations.AlterField(
            model_name='outboundshipment',
            name='comment',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]

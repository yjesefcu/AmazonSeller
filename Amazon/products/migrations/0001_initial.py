# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('OrderType', models.CharField(max_length=50)),
                ('PurchaseDate', models.DateTimeField(verbose_name='\u8d2d\u4e70\u65f6\u95f4')),
                ('AmazonOrderId', models.CharField(max_length=50, verbose_name='\u8ba2\u5355\u7f16\u53f7')),
                ('SellerOrderId', models.CharField(max_length=50, verbose_name='\u5356\u5bb6\u8ba2\u5355\u53f7')),
                ('Amount', models.FloatField(null=True, verbose_name='\u552e\u4ef7', blank=True)),
                ('CurrencyCode', models.CharField(max_length=10, verbose_name='\u8d27\u5e01\u5355\u4f4d')),
                ('LastUpdateDate', models.DateTimeField(null=True, blank=True)),
                ('LatestShipDate', models.DateTimeField(null=True, blank=True)),
                ('IsReplacementOrder', models.BooleanField(default=False)),
                ('ShipServiceLevel', models.CharField(max_length=50, null=True, blank=True)),
                ('OrderStatus', models.CharField(max_length=50, null=True, blank=True)),
                ('SalesChannel', models.CharField(max_length=100, null=True, blank=True)),
                ('NumberOfItemsUnshipped', models.IntegerField(default=0)),
                ('PaymentMethod', models.CharField(max_length=50, null=True, blank=True)),
                ('PaymentMethodDetail', models.CharField(max_length=50, null=True, verbose_name='\u4ed8\u6b3e\u65b9\u5f0f', blank=True)),
                ('FulfillmentChannel', models.CharField(max_length=30, null=True, blank=True)),
                ('IsPrime', models.BooleanField(default=True)),
                ('subscription_fee', models.FloatField(null=True, verbose_name='\u8ba2\u9605\u8d39', blank=True)),
                ('cost', models.FloatField(default=0, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('SKU', models.CharField(max_length=20, verbose_name=b'SKU', db_index=True)),
                ('ASIN', models.CharField(db_index=True, max_length=20, null=True, verbose_name=b'Asin', blank=True)),
                ('FNSKU', models.CharField(max_length=20, null=True, verbose_name=b'FNSKU', blank=True)),
                ('Brand', models.CharField(max_length=100, null=True, verbose_name='\u54c1\u724c', blank=True)),
                ('Color', models.CharField(max_length=50, null=True, verbose_name='\u989c\u8272', blank=True)),
                ('Amount', models.FloatField(null=True, verbose_name='\u552e\u4ef7', blank=True)),
                ('CurrencyCode', models.CharField(max_length=10, verbose_name='\u8d27\u5e01\u5355\u4f4d')),
                ('Image', models.URLField(null=True, verbose_name='\u56fe\u6807', blank=True)),
                ('ImageHeight', models.IntegerField(null=True, blank=True)),
                ('ImageWidth', models.IntegerField(null=True, blank=True)),
                ('Title', models.TextField(null=True, verbose_name='\u4e9a\u9a6c\u900a\u63cf\u8ff0', blank=True)),
                ('TitleCn', models.TextField(null=True, verbose_name='\u4e2d\u6587\u63cf\u8ff0', blank=True)),
                ('ProductGroup', models.CharField(max_length=50, null=True, blank=True)),
                ('ProductTypeName', models.CharField(max_length=50, null=True, verbose_name='\u5546\u54c1\u6240\u5728\u5206\u7ec4', blank=True)),
                ('width', models.FloatField(null=True, verbose_name='\u5bbd\u5ea6', blank=True)),
                ('height', models.FloatField(null=True, verbose_name='\u9ad8\u5ea6', blank=True)),
                ('length', models.FloatField(null=True, verbose_name='\u957f\u5ea6', blank=True)),
                ('weight', models.FloatField(null=True, verbose_name='\u91cd\u91cf', blank=True)),
                ('package_width', models.FloatField(null=True, verbose_name='\u5305\u88c5\u5bbd\u5ea6', blank=True)),
                ('package_height', models.FloatField(null=True, verbose_name='\u5305\u88c5\u9ad8\u5ea6', blank=True)),
                ('package_length', models.FloatField(null=True, verbose_name='\u5305\u88c5\u957f\u5ea6', blank=True)),
                ('package_weight', models.FloatField(null=True, verbose_name='\u5305\u88c5\u91cd\u91cf', blank=True)),
                ('PackageDimensions', models.CharField(max_length=100, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Settlement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('start_date', models.DateField(verbose_name='\u7ed3\u7b97\u5f00\u59cb\u65e5\u671f')),
                ('end_date', models.DateField(verbose_name='\u7ed3\u7b97\u7ed3\u675f\u65e5\u671f')),
                ('advertising_fee', models.FloatField(null=True, verbose_name='\u5e7f\u544a\u8d39', blank=True)),
                ('storage_fee', models.FloatField(null=True, verbose_name='\u4ed3\u50a8\u8d39', blank=True)),
                ('total_returns', models.FloatField(null=True, verbose_name='\u603b\u6536\u5165', blank=True)),
                ('sold_account', models.IntegerField(null=True, verbose_name='\u9500\u552e\u6570\u91cf', blank=True)),
                ('total_cost', models.FloatField(null=True, verbose_name='\u603b\u6210\u672c', blank=True)),
                ('profit', models.FloatField(null=True, verbose_name='\u5229\u6da6', blank=True)),
                ('profit_rate', models.FloatField(null=True, verbose_name='\u5229\u6da6\u7387', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ShipOverseaItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('count', models.IntegerField(verbose_name='\u6570\u91cf')),
                ('unit_freight', models.FloatField(null=True, verbose_name='\u8fd0\u8d39\u5355\u4ef7', blank=True)),
                ('fuel_tax', models.FloatField(null=True, verbose_name='\u71c3\u6cb9\u9644\u52a0\u7a0e', blank=True)),
                ('logistics_company', models.CharField(max_length=100, null=True, verbose_name='\u7269\u6d41\u516c\u53f8\u540d\u79f0', blank=True)),
                ('logistics_id', models.CharField(max_length=100, null=True, verbose_name='\u7269\u6d41\u8fd0\u5355\u53f7', blank=True)),
                ('package_width', models.FloatField(null=True, verbose_name='\u5916\u5305\u88c5\u5bbd\u5ea6', blank=True)),
                ('package_height', models.FloatField(null=True, verbose_name='\u5916\u5305\u88c5\u9ad8\u5ea6', blank=True)),
                ('package_length', models.FloatField(null=True, verbose_name='\u5916\u5305\u88c5\u957f\u5ea6', blank=True)),
                ('package_weight', models.FloatField(null=True, verbose_name='\u5916\u5305\u88c5\u91cd\u91cf', blank=True)),
                ('total_freight', models.FloatField(null=True, verbose_name='\u603b\u8fd0\u8d39', blank=True)),
                ('product', models.ForeignKey(related_name='shipsOversea', to='products.Product')),
            ],
        ),
        migrations.CreateModel(
            name='ShipsIn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(verbose_name='\u6570\u91cf')),
                ('remain_count', models.IntegerField(verbose_name='\u5269\u4f59\u6570\u91cf')),
                ('unit_price', models.FloatField(verbose_name='\u5355\u4ef7')),
                ('total_freight', models.FloatField(verbose_name='\u603b\u8fd0\u8d39')),
                ('charges', models.FloatField(null=True, verbose_name='\u6742\u8d39', blank=True)),
                ('charges_comment', models.TextField(null=True, verbose_name='\u6742\u8d39\u5907\u6ce8', blank=True)),
                ('ship_date', models.DateTimeField(null=True, verbose_name='\u5230\u8d27\u65e5\u671f', blank=True)),
                ('insert_time', models.DateTimeField(null=True, blank=True)),
                ('product', models.ForeignKey(related_name='shipsIn', to='products.Product')),
            ],
        ),
        migrations.CreateModel(
            name='ShipsOversea',
            fields=[
                ('id', models.CharField(max_length=30, serialize=False, verbose_name='\u8d27\u4ef6\u53f7', primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('ship_date', models.DateField(null=True, verbose_name='\u53d1\u8d27\u65f6\u95f4', blank=True)),
                ('total_freight', models.FloatField(null=True, verbose_name='\u603b\u8fd0\u8d39', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='shipoverseaitem',
            name='shipment',
            field=models.ForeignKey(related_name='products', to='products.ShipsOversea'),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together=set([('MarketplaceId', 'SKU')]),
        ),
        migrations.AddField(
            model_name='orders',
            name='product',
            field=models.ForeignKey(related_name='orders', to='products.Product'),
        ),
    ]
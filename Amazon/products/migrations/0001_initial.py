# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdvertisingProductItems',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('StartDate', models.DateTimeField(null=True, blank=True)),
                ('EndDate', models.DateTimeField(null=True, blank=True)),
                ('SellerSKU', models.CharField(max_length=50, null=True, blank=True)),
                ('TotalSpend', models.FloatField(null=True, blank=True)),
                ('cost', models.FloatField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='AdvertisingTransactionDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('InvoiceId', models.CharField(max_length=100, verbose_name='\u53d1\u7968ID')),
                ('TransactionType', models.CharField(max_length=50, null=True, verbose_name='\u670d\u52a1\u8d39\u7c7b\u578b', blank=True)),
                ('PostedDate', models.DateTimeField(null=True, verbose_name='\u63d0\u4ea4\u65f6\u95f4', blank=True)),
                ('BaseAmount', models.FloatField(null=True, blank=True)),
                ('TransactionAmount', models.FloatField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='InboundShipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('count', models.IntegerField(null=True, verbose_name='\u6570\u91cf', blank=True)),
                ('inventory', models.IntegerField(default=0, null=True, verbose_name='\u5e93\u5b58', blank=True)),
                ('real_inventory', models.IntegerField(null=True, blank=True)),
                ('unit_price', models.FloatField(null=True, verbose_name='\u5546\u54c1\u5355\u4ef7', blank=True)),
                ('total_freight', models.FloatField(null=True, verbose_name='\u603b\u8fd0\u8d39', blank=True)),
                ('charges', models.FloatField(null=True, verbose_name='\u6742\u8d39', blank=True)),
                ('charges_comment', models.TextField(null=True, verbose_name='\u6742\u8d39\u5907\u6ce8', blank=True)),
                ('ship_date', models.DateField(null=True, verbose_name='\u5230\u8d27\u65e5\u671f', blank=True)),
                ('insert_time', models.DateTimeField(null=True, blank=True)),
                ('unit_cost', models.FloatField(null=True, verbose_name='\u5355\u4f4d\u6210\u672c', blank=True)),
                ('ShipmentName', models.CharField(max_length=50, null=True, blank=True)),
                ('settlement_id', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('-ship_date',),
            },
        ),
        migrations.CreateModel(
            name='OtherTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('TransactionID', models.CharField(max_length=50)),
                ('AmazonOrderId', models.CharField(max_length=50, null=True, blank=True)),
                ('TransactionType', models.CharField(max_length=50, null=True, verbose_name='\u670d\u52a1\u8d39\u7c7b\u578b', blank=True)),
                ('PostedDate', models.DateTimeField(null=True, verbose_name='\u63d0\u4ea4\u65f6\u95f4', blank=True)),
                ('Amount', models.FloatField(null=True, verbose_name='\u603b\u8ba1', blank=True)),
                ('SellerSKU', models.CharField(max_length=50, null=True, blank=True)),
            ],
            options={
                'ordering': ['-PostedDate'],
            },
        ),
        migrations.CreateModel(
            name='OtherTransactionFee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('TransactionID', models.CharField(max_length=50)),
                ('AmazonOrderId', models.CharField(max_length=50, null=True, blank=True)),
                ('TransactionType', models.CharField(max_length=50, null=True, verbose_name='\u670d\u52a1\u8d39\u7c7b\u578b', blank=True)),
                ('PostedDate', models.DateTimeField(null=True, verbose_name='\u63d0\u4ea4\u65f6\u95f4', blank=True)),
                ('Type', models.CharField(max_length=50, null=True, verbose_name='\u4ed8\u6b3e\u8be6\u60c5', blank=True)),
                ('Amount', models.FloatField(null=True, verbose_name='\u603b\u8ba1', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='OtherTransactionItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('TransactionID', models.CharField(max_length=50, null=True, blank=True)),
                ('AmazonOrderId', models.CharField(max_length=50, null=True, blank=True)),
                ('TransactionType', models.CharField(max_length=50, null=True, verbose_name='\u670d\u52a1\u8d39\u7c7b\u578b', blank=True)),
                ('PostedDate', models.DateTimeField(null=True, verbose_name='\u63d0\u4ea4\u65f6\u95f4', blank=True)),
                ('SellerSKU', models.CharField(max_length=50, null=True, blank=True)),
                ('Quantity', models.IntegerField(null=True, blank=True)),
                ('UnitPrice', models.FloatField(null=True, verbose_name='\u5546\u54c1\u9500\u552e\u5355\u4ef7', blank=True)),
                ('Amount', models.FloatField(null=True, verbose_name='\u8d54\u507f\u4ef7\u683c', blank=True)),
                ('cost', models.FloatField(null=True, verbose_name='\u5355\u4f4d\u6210\u672c', blank=True)),
                ('income', models.FloatField(null=True, blank=True)),
                ('total_cost', models.FloatField(null=True, verbose_name='\u603b\u6210\u672c', blank=True)),
                ('profit', models.FloatField(null=True, blank=True)),
                ('profit_rate', models.FloatField(null=True, blank=True)),
                ('is_total', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='OutboundShipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('ShipmentId', models.CharField(max_length=50)),
                ('ShipmentName', models.CharField(max_length=255, null=True, blank=True)),
                ('LabelPrepType', models.CharField(max_length=100, null=True, blank=True)),
                ('ShipmentStatus', models.CharField(max_length=30, null=True, blank=True)),
                ('ShipFromCity', models.CharField(max_length=50, null=True, blank=True)),
                ('logistics_company', models.CharField(max_length=100, null=True, verbose_name='\u7269\u6d41\u516c\u53f8\u540d\u79f0', blank=True)),
                ('logistics_id', models.CharField(max_length=100, null=True, verbose_name='\u7269\u6d41\u8fd0\u5355\u53f7', blank=True)),
                ('ship_date', models.DateField(null=True, verbose_name='\u53d1\u8d27\u65f6\u95f4', blank=True)),
                ('total_freight', models.FloatField(null=True, verbose_name='\u603b\u8fd0\u8d39', blank=True)),
                ('duty', models.FloatField(null=True, verbose_name='\u603b\u5173\u7a0e', blank=True)),
                ('comment', models.CharField(max_length=255, null=True, blank=True)),
                ('settlement_id', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['-ship_date'],
            },
        ),
        migrations.CreateModel(
            name='OutboundShipmentItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('ShipmentId', models.CharField(max_length=50, null=True, blank=True)),
                ('ship_date', models.DateField(null=True, verbose_name='\u53d1\u8d27\u65f6\u95f4', blank=True)),
                ('SellerSKU', models.CharField(max_length=50, null=True, blank=True)),
                ('FulfillmentNetworkSKU', models.CharField(max_length=50, null=True, blank=True)),
                ('QuantityShipped', models.IntegerField(default=0, null=True, blank=True)),
                ('unit_price', models.FloatField(null=True, verbose_name='\u5546\u54c1\u5355\u4ef7', blank=True)),
                ('unit_freight', models.FloatField(default=0, null=True, verbose_name='\u8fd0\u8d39\u5355\u4ef7', blank=True)),
                ('fuel_tax', models.FloatField(default=0, null=True, verbose_name='\u71c3\u6cb9\u9644\u52a0\u7a0e', blank=True)),
                ('duty', models.FloatField(default=0, null=True, verbose_name='\u5173\u7a0e', blank=True)),
                ('width', models.FloatField(null=True, verbose_name='\u5546\u54c1\u5bbd\u5ea6', blank=True)),
                ('height', models.FloatField(null=True, verbose_name='\u5546\u54c1\u9ad8\u5ea6', blank=True)),
                ('length', models.FloatField(null=True, verbose_name='\u5546\u54c1\u957f\u5ea6', blank=True)),
                ('weight', models.FloatField(null=True, verbose_name='\u5546\u54c1\u91cd\u91cf', blank=True)),
                ('volume_weight', models.FloatField(null=True, verbose_name='\u4f53\u79ef\u91cd', blank=True)),
                ('unit_weight', models.FloatField(null=True, verbose_name='\u4f53\u79ef\u53c2\u6570', blank=True)),
                ('total_freight', models.FloatField(null=True, verbose_name='\u603b\u8fd0\u8d39', blank=True)),
                ('inventory', models.IntegerField(default=0, null=True, verbose_name='\u5e93\u5b58', blank=True)),
                ('unit_cost', models.FloatField(null=True, verbose_name='\u79fb\u5e93\u5355\u4f4d\u6210\u672c', blank=True)),
            ],
            options={
                'ordering': ['SellerSKU', '-shipment__ship_date'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('SellerSKU', models.CharField(max_length=50, verbose_name=b'SKU', db_index=True)),
                ('ASIN', models.CharField(db_index=True, max_length=20, null=True, verbose_name=b'Asin', blank=True)),
                ('FNSKU', models.CharField(max_length=20, null=True, verbose_name=b'FNSKU', blank=True)),
                ('Brand', models.CharField(max_length=100, null=True, verbose_name='\u54c1\u724c', blank=True)),
                ('Color', models.CharField(max_length=50, null=True, verbose_name='\u989c\u8272', blank=True)),
                ('Amount', models.FloatField(null=True, verbose_name='\u552e\u4ef7', blank=True)),
                ('CurrencyCode', models.CharField(max_length=10, null=True, verbose_name='\u8d27\u5e01\u5355\u4f4d', blank=True)),
                ('Image', models.CharField(max_length=255, null=True, verbose_name='\u56fe\u6807', blank=True)),
                ('TotalSupplyQuantity', models.IntegerField(null=True, blank=True)),
                ('Title', models.TextField(null=True, verbose_name='\u4e9a\u9a6c\u900a\u63cf\u8ff0', blank=True)),
                ('TitleCn', models.TextField(null=True, verbose_name='\u4e2d\u6587\u63cf\u8ff0', blank=True)),
                ('Binding', models.CharField(max_length=50, null=True, verbose_name='\u7c7b\u578b', blank=True)),
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
                ('volume_weight', models.FloatField(null=True, verbose_name='\u4f53\u79ef\u91cd', blank=True)),
                ('domestic_inventory', models.IntegerField(default=0, verbose_name='\u56fd\u5185\u5e93\u5b58')),
                ('amazon_inventory', models.IntegerField(default=0, verbose_name='\u4e9a\u9a6c\u900a\u5e93\u5b58')),
                ('supply_cost', models.FloatField(null=True, blank=True)),
                ('shipment_cost', models.FloatField(null=True, blank=True)),
                ('cost', models.FloatField(default=0, verbose_name='\u6210\u672c')),
                ('last_supply', models.DateField(null=True, verbose_name='\u4e0a\u4e00\u6b21\u5165\u5e93\u65e5\u671f', blank=True)),
                ('last_oversea', models.DateField(null=True, verbose_name='\u4e0a\u4e00\u6b21\u79fb\u5e93\u65e5\u671f', blank=True)),
                ('sold_count', models.IntegerField(default=0, verbose_name='\u5df2\u9500\u552e\u6570\u91cf')),
            ],
            options={
                'ordering': ['SellerSKU'],
            },
        ),
        migrations.CreateModel(
            name='ProductRemovalItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('RequestDate', models.DateTimeField(null=True, blank=True)),
                ('UpdateDate', models.DateTimeField(null=True, blank=True)),
                ('OrderId', models.CharField(max_length=50, null=True, blank=True)),
                ('OrderType', models.CharField(max_length=20, null=True, blank=True)),
                ('OrderStatus', models.CharField(max_length=20, null=True, blank=True)),
                ('SellerSKU', models.CharField(max_length=50, null=True, blank=True)),
                ('FNSKU', models.CharField(max_length=50, null=True, blank=True)),
                ('Disposition', models.CharField(max_length=20, null=True, blank=True)),
                ('Quantity', models.IntegerField(null=True, blank=True)),
                ('Fee', models.FloatField(null=True, blank=True)),
                ('cost', models.FloatField(null=True, verbose_name='\u5355\u4f4d\u6210\u672c', blank=True)),
                ('total_cost', models.FloatField(null=True, verbose_name='\u603b\u6210\u672c', blank=True)),
                ('income', models.FloatField(null=True, verbose_name='\u4e9a\u9a6c\u900a\u5b9e\u6536', blank=True)),
                ('profit', models.FloatField(default=0, null=True, blank=True)),
                ('profit_rate', models.FloatField(default=0, null=True, blank=True)),
                ('is_total', models.BooleanField(default=False)),
                ('product', models.ForeignKey(related_name='removals', blank=True, to='products.Product', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductReturn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('snapshot_date', models.DateTimeField()),
                ('type', models.CharField(max_length=20)),
                ('SellerSKU', models.CharField(max_length=50)),
                ('quantity', models.IntegerField()),
                ('disposition', models.CharField(max_length=20)),
                ('product', models.ForeignKey(to='products.Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductSettlement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('Quantity', models.IntegerField(null=True, blank=True)),
                ('custom_return_fee', models.FloatField(null=True, blank=True)),
                ('sales', models.FloatField(default=0, verbose_name='\u9500\u552e')),
                ('refund', models.FloatField(default=0, verbose_name='\u9000\u8d27')),
                ('other_fee', models.FloatField(default=0, verbose_name='\u5176\u4ed6\u670d\u52a1\u8d39')),
                ('other_trade', models.FloatField(default=0, verbose_name='\u5176\u4ed6\u4ea4\u6613')),
                ('income', models.FloatField(null=True, blank=True)),
                ('advertising_fee', models.FloatField(null=True, blank=True)),
                ('storage_fee', models.FloatField(null=True, blank=True)),
                ('subscription_fee', models.FloatField(null=True, verbose_name='\u8ba2\u9605\u8d39', blank=True)),
                ('cost', models.FloatField(null=True, verbose_name='\u6210\u672c', blank=True)),
                ('total_cost', models.FloatField(null=True, blank=True)),
                ('profit', models.FloatField(null=True, verbose_name='\u5229\u6da6', blank=True)),
                ('profit_rate', models.FloatField(null=True, verbose_name='\u5229\u6da6\u7387', blank=True)),
                ('is_calculated', models.BooleanField(default=False)),
                ('product', models.ForeignKey(blank=True, to='products.Product', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('AdjustmentID', models.CharField(max_length=100)),
                ('AmazonOrderId', models.CharField(max_length=50, null=True, blank=True)),
                ('MarketplaceName', models.CharField(max_length=100, null=True, verbose_name='\u5546\u57ce\u540d\u5b57', blank=True)),
                ('PostedDate', models.DateTimeField(null=True, verbose_name='\u63d0\u4ea4\u65f6\u95f4', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RefundItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('MerchantAdjustmentItemID', models.CharField(max_length=50, null=True, blank=True)),
                ('AmazonOrderId', models.CharField(max_length=50, null=True, blank=True)),
                ('OrderItemId', models.CharField(max_length=50, null=True, blank=True)),
                ('PostedDate', models.DateTimeField(null=True, verbose_name='\u63d0\u4ea4\u65f6\u95f4', blank=True)),
                ('SellerSKU', models.CharField(max_length=50, null=True, blank=True)),
                ('Quantity', models.IntegerField(null=True, blank=True)),
                ('UnitPrice', models.FloatField(null=True, verbose_name='\u9500\u552e\u5355\u4ef7', blank=True)),
                ('Principal', models.FloatField(null=True, blank=True)),
                ('OtherPrice', models.FloatField(null=True, verbose_name=b'\xe4\xb9\xb0\xe5\xae\xb6\xe5\x85\xb6\xe4\xbb\x96\xe9\x80\x80\xe6\xac\xbe', blank=True)),
                ('Fee', models.FloatField(null=True, verbose_name=b'\xe4\xba\x9a\xe9\xa9\xac\xe9\x80\x8a\xe8\xb4\xb9\xe7\x94\xa8\xe9\x80\x80\xe6\xac\xbe', blank=True)),
                ('Promotion', models.FloatField(null=True, verbose_name=b'\xe4\xbf\x83\xe9\x94\x80\xe8\xbf\x94\xe7\x82\xb9', blank=True)),
                ('cost', models.FloatField(null=True, verbose_name='\u5355\u4f4d\u6210\u672c', blank=True)),
                ('total_cost', models.FloatField(null=True, verbose_name='\u603b\u6210\u672c', blank=True)),
                ('income', models.FloatField(null=True, verbose_name='\u5b9e\u6536', blank=True)),
                ('profit', models.FloatField(default=0, null=True, blank=True)),
                ('profit_rate', models.FloatField(null=True, blank=True)),
                ('is_total', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-PostedDate'],
            },
        ),
        migrations.CreateModel(
            name='SellerCouponPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('PostedDate', models.DateTimeField(null=True, blank=True)),
                ('Amount', models.FloatField(default=0, null=True)),
                ('Count', models.IntegerField(default=0)),
                ('cost', models.FloatField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SellerDealPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('DealID', models.CharField(max_length=255)),
                ('PostedDate', models.DateTimeField(null=True, verbose_name='\u63d0\u4ea4\u65f6\u95f4', blank=True)),
                ('DealDescription', models.CharField(max_length=100, null=True, blank=True)),
                ('MarketplaceName', models.CharField(max_length=100, null=True, verbose_name='\u5546\u57ce\u540d\u5b57', blank=True)),
                ('TransactionType', models.CharField(max_length=50, null=True, verbose_name='\u670d\u52a1\u8d39\u7c7b\u578b', blank=True)),
                ('PaymentReason', models.CharField(max_length=100, null=True, blank=True)),
                ('DealFeeType', models.CharField(max_length=100, null=True, blank=True)),
                ('DealFeeAmount', models.FloatField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-PostedDate'],
            },
        ),
        migrations.CreateModel(
            name='Settlement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('report_id', models.CharField(max_length=50, null=True, blank=True)),
                ('AmazonSettlementID', models.CharField(max_length=100)),
                ('TotalAmount', models.FloatField(null=True, blank=True)),
                ('StartDate', models.DateTimeField(null=True, verbose_name='\u7ed3\u7b97\u5f00\u59cb\u65e5\u671f', blank=True)),
                ('EndDate', models.DateTimeField(null=True, verbose_name='\u7ed3\u7b97\u7ed3\u675f\u65e5\u671f', blank=True)),
                ('custom_return_fee', models.FloatField(null=True, blank=True)),
                ('Quantity', models.IntegerField(null=True, verbose_name='\u9500\u552e\u6570\u91cf', blank=True)),
                ('sales', models.FloatField(default=0, verbose_name='\u8ba2\u5355')),
                ('refund', models.FloatField(default=0, verbose_name='\u9000\u8d27')),
                ('other_fee', models.FloatField(default=0, verbose_name='\u5176\u4ed6\u670d\u52a1\u8d39')),
                ('other_trade', models.FloatField(default=0, verbose_name='\u5176\u4ed6\u4ea4\u6613')),
                ('income', models.FloatField(null=True, verbose_name='\u603b\u6536\u5165', blank=True)),
                ('advertising_fee', models.FloatField(null=True, blank=True)),
                ('advertising_fee_adjust', models.FloatField(null=True, verbose_name='\u5b9e\u9645\u652f\u4ed8\u7684\u603b\u5e7f\u544a\u8d39', blank=True)),
                ('storage_fee', models.FloatField(null=True, blank=True)),
                ('subscription_fee', models.FloatField(null=True, verbose_name='\u8ba2\u9605\u8d39', blank=True)),
                ('cost', models.FloatField(null=True, verbose_name='\u6210\u672c', blank=True)),
                ('total_cost', models.FloatField(null=True, verbose_name='\u603b\u6210\u672c', blank=True)),
                ('profit', models.FloatField(null=True, verbose_name='\u5229\u6da6', blank=True)),
                ('profit_rate', models.FloatField(null=True, verbose_name='\u5229\u6da6\u7387', blank=True)),
                ('calc_status', models.IntegerField(default=0)),
                ('is_downloading', models.BooleanField(default=False)),
                ('storage_imported', models.BooleanField(default=False)),
                ('removal_imported', models.BooleanField(default=False)),
                ('advertising_imported', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-EndDate'],
            },
        ),
        migrations.CreateModel(
            name='SettlementDataRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_type', models.CharField(max_length=20)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('settlement', models.ForeignKey(to='products.Settlement')),
            ],
        ),
        migrations.CreateModel(
            name='SettleOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(max_length=30, db_index=True)),
                ('MarketplaceName', models.CharField(max_length=100, null=True, blank=True)),
                ('AmazonOrderId', models.CharField(max_length=50, verbose_name='\u8ba2\u5355\u7f16\u53f7')),
                ('ShipmentID', models.CharField(max_length=50, null=True, verbose_name='\u7269\u6d41ID', blank=True)),
                ('PostedDate', models.DateTimeField(null=True, verbose_name='\u63d0\u4ea4\u65f6\u95f4', blank=True)),
                ('settlement', models.ForeignKey(related_name='orders', blank=True, to='products.Settlement', null=True)),
            ],
            options={
                'ordering': ['-PostedDate'],
            },
        ),
        migrations.CreateModel(
            name='SettleOrderItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('MarketplaceId', models.CharField(db_index=True, max_length=30, null=True, blank=True)),
                ('OrderItemId', models.CharField(max_length=20, null=True, blank=True)),
                ('AmazonOrderId', models.CharField(db_index=True, max_length=50, null=True, blank=True)),
                ('PostedDate', models.DateTimeField(null=True, verbose_name='\u63d0\u4ea4\u65f6\u95f4', blank=True)),
                ('SellerSKU', models.CharField(max_length=50, null=True, blank=True)),
                ('UnitPrice', models.FloatField(null=True, verbose_name='\u5355\u4ef7', blank=True)),
                ('Quantity', models.IntegerField(null=True, blank=True)),
                ('Principal', models.FloatField(null=True, verbose_name='\u8ba2\u5355\u4ed8\u6b3e', blank=True)),
                ('OtherPrice', models.FloatField(null=True, verbose_name=b'\xe5\x85\xb6\xe4\xbb\x96\xe4\xbb\x98\xe6\xac\xbe', blank=True)),
                ('Fee', models.FloatField(null=True, verbose_name=b'\xe4\xba\x9a\xe9\xa9\xac\xe9\x80\x8a\xe6\x94\xb6\xe5\x8f\x96\xe8\xb4\xb9\xe7\x94\xa8', blank=True)),
                ('Promotion', models.FloatField(null=True, verbose_name=b'\xe4\xbf\x83\xe9\x94\x80\xe8\xbf\x94\xe6\xac\xbe', blank=True)),
                ('income', models.FloatField(null=True, verbose_name='\u9500\u552e\u5b9e\u6536', blank=True)),
                ('advertising_fee', models.FloatField(null=True, blank=True)),
                ('storage_fee', models.FloatField(null=True, blank=True)),
                ('subscription_fee', models.FloatField(null=True, verbose_name='\u8ba2\u9605\u8d39', blank=True)),
                ('supply_cost', models.FloatField(null=True, verbose_name='\u56fd\u5185\u8fd0\u8d39', blank=True)),
                ('shipment_cost', models.FloatField(null=True, verbose_name='\u56fd\u9645\u8fd0\u8d39', blank=True)),
                ('cost', models.FloatField(default=0, null=True, verbose_name='\u5355\u4f4d\u6210\u672c', blank=True)),
                ('total_cost', models.FloatField(null=True, verbose_name='\u603b\u6210\u672c', blank=True)),
                ('profit', models.FloatField(default=0, null=True, blank=True)),
                ('profit_rate', models.FloatField(null=True, blank=True)),
                ('is_total', models.BooleanField(default=False)),
                ('order', models.ForeignKey(related_name='items', blank=True, to='products.SettleOrder', null=True)),
                ('product', models.ForeignKey(related_name='settle_items', blank=True, to='products.Product', null=True)),
                ('settlement', models.ForeignKey(related_name='order_items', blank=True, to='products.Settlement', null=True)),
            ],
            options={
                'ordering': ['-PostedDate'],
            },
        ),
        migrations.AddField(
            model_name='sellerdealpayment',
            name='settlement',
            field=models.ForeignKey(related_name='seller_deal_payments', blank=True, to='products.Settlement', null=True),
        ),
        migrations.AddField(
            model_name='sellercouponpayment',
            name='settlement',
            field=models.ForeignKey(related_name='coupons', blank=True, to='products.Settlement', null=True),
        ),
        migrations.AddField(
            model_name='refunditem',
            name='order_item',
            field=models.ForeignKey(blank=True, to='products.SettleOrderItem', null=True),
        ),
        migrations.AddField(
            model_name='refunditem',
            name='product',
            field=models.ForeignKey(related_name='refunds', blank=True, to='products.Product', null=True),
        ),
        migrations.AddField(
            model_name='refunditem',
            name='refund',
            field=models.ForeignKey(related_name='items', blank=True, to='products.Refund', null=True),
        ),
        migrations.AddField(
            model_name='refunditem',
            name='settlement',
            field=models.ForeignKey(blank=True, to='products.Settlement', null=True),
        ),
        migrations.AddField(
            model_name='refund',
            name='settlement',
            field=models.ForeignKey(related_name='refunds', blank=True, to='products.Settlement', null=True),
        ),
        migrations.AddField(
            model_name='productsettlement',
            name='settlement',
            field=models.ForeignKey(related_name='products', to='products.Settlement'),
        ),
        migrations.AddField(
            model_name='productreturn',
            name='settlement',
            field=models.ForeignKey(related_name='returns', to='products.Settlement'),
        ),
        migrations.AddField(
            model_name='productremovalitem',
            name='settlement',
            field=models.ForeignKey(related_name='removals', to='products.Settlement'),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together=set([('MarketplaceId', 'SellerSKU')]),
        ),
        migrations.AddField(
            model_name='outboundshipmentitem',
            name='product',
            field=models.ForeignKey(related_name='shipsOversea', to='products.Product'),
        ),
        migrations.AddField(
            model_name='outboundshipmentitem',
            name='shipment',
            field=models.ForeignKey(related_name='products', to='products.OutboundShipment'),
        ),
        migrations.AddField(
            model_name='othertransactionitem',
            name='product',
            field=models.ForeignKey(blank=True, to='products.Product', null=True),
        ),
        migrations.AddField(
            model_name='othertransactionitem',
            name='settlement',
            field=models.ForeignKey(to='products.Settlement'),
        ),
        migrations.AddField(
            model_name='othertransactionitem',
            name='transaction',
            field=models.ForeignKey(related_name='items', blank=True, to='products.OtherTransaction', null=True),
        ),
        migrations.AddField(
            model_name='othertransactionfee',
            name='settlement',
            field=models.ForeignKey(related_name='removal_products', to='products.Settlement'),
        ),
        migrations.AddField(
            model_name='othertransactionfee',
            name='transaction',
            field=models.ForeignKey(related_name='fees', to='products.OtherTransaction'),
        ),
        migrations.AddField(
            model_name='othertransaction',
            name='refund_item',
            field=models.ForeignKey(blank=True, to='products.RefundItem', null=True),
        ),
        migrations.AddField(
            model_name='othertransaction',
            name='settlement',
            field=models.ForeignKey(related_name='other_transactions', blank=True, to='products.Settlement', null=True),
        ),
        migrations.AddField(
            model_name='inboundshipment',
            name='product',
            field=models.ForeignKey(related_name='supplies', to='products.Product'),
        ),
        migrations.AddField(
            model_name='advertisingtransactiondetails',
            name='settlement',
            field=models.ForeignKey(related_name='advertising_transactions', blank=True, to='products.Settlement', null=True),
        ),
        migrations.AddField(
            model_name='advertisingproductitems',
            name='product',
            field=models.ForeignKey(related_name='advertising_fees', to='products.Product'),
        ),
        migrations.AddField(
            model_name='advertisingproductitems',
            name='settlement',
            field=models.ForeignKey(related_name='advertising_products', blank=True, to='products.Settlement', null=True),
        ),
    ]

#-*- coding:utf-8 -*-
from django.db import models

# Create your models here.


class Product(models.Model):
    MarketplaceId = models.CharField(max_length=30, db_index=True, null=True, blank=True)     # 市场Id
    SKU = models.CharField(max_length=20, verbose_name='SKU', db_index=True)
    ASIN = models.CharField(max_length=20, null=True, blank=True, verbose_name='Asin', db_index=True)
    FNSKU = models.CharField(max_length=20, null=True, blank=True, verbose_name='FNSKU')
    Brand = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'品牌')
    Color = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'颜色')
    Amount = models.FloatField(null=True, blank=True, verbose_name=u'售价')   # 售价
    CurrencyCode = models.CharField(max_length=10, null=True, blank=True, verbose_name=u'货币单位')      # 货币代码：USD-美元
    Image = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'图标')      # 图标
    ImageHeight = models.IntegerField(null=True, blank=True)    # 图标高
    ImageWidth = models.IntegerField(null=True, blank=True)     # 图标宽
    Title = models.TextField(null=True, blank=True, verbose_name=u'亚马逊描述')             # 商城描述
    TitleCn = models.TextField(null=True, blank=True, verbose_name=u'中文描述')           # 中文描述，手动输入
    ProductGroup = models.CharField(max_length=50, null=True, blank=True)   # 商品分组
    ProductTypeName = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'商品所在分组')    # 商品分组名称
    width = models.FloatField(null=True, blank=True, verbose_name=u'宽度')    # 商品本身高度，单位cm
    height = models.FloatField(null=True, blank=True, verbose_name=u'高度')   # 商品本身高度，单位cm
    length = models.FloatField(null=True, blank=True, verbose_name=u'长度')   # 商品本身程度，单位cm
    weight = models.FloatField(null=True, blank=True, verbose_name=u'重量')   # 商品本身重量，单位kg
    package_width = models.FloatField(null=True, blank=True, verbose_name=u'包装宽度')  # 单位cm
    package_height = models.FloatField(null=True, blank=True, verbose_name=u'包装高度') # 单位cm
    package_length = models.FloatField(null=True, blank=True, verbose_name=u'包装长度') # 单位cm
    package_weight = models.FloatField(null=True, blank=True, verbose_name=u'包装重量') # 单位kg
    PackageDimensions = models.CharField(max_length=100, null=True, blank=True)     # 包装大小、重量，格式： [{'height': 1.40, 'unit': 'inches'}]
    volume_weight = models.FloatField(null=True, blank=True, verbose_name=u'体积重')        # 体积重，height*width*length/5000
    remain_count = models.IntegerField(default=0, verbose_name=u'剩余数量')       # 商品剩余数量
    cost = models.FloatField(default=0, verbose_name=u'成本')     # 当前商品成本
    last_supply = models.DateField(null=True, blank=True, verbose_name=u'上一次入库日期')
    last_oversea = models.DateField(null=True, blank=True, verbose_name=u'上一次移库日期')

    class Meta:
        unique_together = (('MarketplaceId', 'SKU',),)


class ShipsIn(models.Model):
    """
    发往国内的商品信息，以商品为维度
    """
    product = models.ForeignKey(Product, related_name='supplies')
    count = models.IntegerField(verbose_name=u'数量')       # 商品数量
    # remain_count = models.IntegerField(verbose_name=u'剩余数量', default=0)    # count-发往国外的数量
    unit_price = models.FloatField(verbose_name=u'单价')
    total_freight = models.FloatField(verbose_name=u'总运费')
    charges = models.FloatField(null=True, blank=True, verbose_name=u'杂费')
    charges_comment = models.TextField(null=True, blank=True, verbose_name=u'杂费备注')
    ship_date = models.DateField(null=True, blank=True, verbose_name=u'到货日期')
    insert_time = models.DateTimeField(null=True, blank=True)   # 添加至数据库的时间


class ShipsOversea(models.Model):
    """
    发往国外的货件，以货件为维度
    """
    id = models.CharField(max_length=30, primary_key=True, verbose_name=u'货件号')
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    ship_date = models.DateField(null=True, blank=True, verbose_name=u'发货时间')     # 发货时间
    total_freight = models.FloatField(null=True, blank=True, verbose_name=u'总运费')        # 总运费


class ShipOverseaItem(models.Model):
    """
    每个货件里的商品信息
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    shipment = models.ForeignKey(ShipsOversea, related_name='products')
    product = models.ForeignKey(Product, related_name='shipsOversea')
    count = models.IntegerField(verbose_name=u'数量')
    unit_freight = models.FloatField(null=True, blank=True, verbose_name=u'运费单价')       # 单位：kg
    fuel_tax = models.FloatField(null=True, blank=True, verbose_name=u'燃油附加税')       # 百分比
    logistics_company = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'物流公司名称')
    logistics_id = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'物流运单号')
    package_width = models.FloatField(null=True, blank=True, verbose_name=u'外包装宽度')
    package_height = models.FloatField(null=True, blank=True, verbose_name=u'外包装高度')
    package_length = models.FloatField(null=True, blank=True, verbose_name=u'外包装长度')
    package_weight = models.FloatField(null=True, blank=True, verbose_name=u'外包装重量')
    total_freight = models.FloatField(null=True, blank=True, verbose_name=u'总运费')    # 通过计算获得：max(外箱体积重,外箱实际重)*运费单价*（1+燃油附加税） = 总运费


class Orders(models.Model):
    """
    销售记录
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)
    product = models.ForeignKey(Product, related_name='orders')
    OrderType = models.CharField(max_length=50)
    PurchaseDate = models.DateTimeField(verbose_name=u'购买时间')
    AmazonOrderId = models.CharField(max_length=50, verbose_name=u'订单编号')
    SellerOrderId = models.CharField(max_length=50, verbose_name=u'卖家订单号')
    Amount = models.FloatField(null=True, blank=True, verbose_name=u'售价')   # USD
    CurrencyCode = models.CharField(max_length=10, verbose_name=u'货币单位')      # 货币代码：USD-美元
    LastUpdateDate = models.DateTimeField(null=True, blank=True)                # 上一次更新时间
    LatestShipDate = models.DateTimeField(null=True, blank=True)                # 预计配送日期
    IsReplacementOrder = models.BooleanField(default=False)                     #
    ShipServiceLevel = models.CharField(max_length=50, null=True, blank=True)   # 配送服务级别
    OrderStatus = models.CharField(max_length=50, null=True, blank=True)        # 订单状态
    SalesChannel = models.CharField(max_length=100, null=True, blank=True)      # 商城地址
    NumberOfItemsUnshipped = models.IntegerField(default=0)         # 未发货数量
    PaymentMethod = models.CharField(max_length=50, null=True, blank=True)
    PaymentMethodDetail = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'付款方式')
    IsPremiumOrder = models.BooleanField(default=False)
    FulfillmentChannel = models.CharField(max_length=30, null=True, blank=True)
    IsPrime = models.BooleanField(default=True)     # 是否会员
    subscription_fee = models.FloatField(null=True, blank=True, verbose_name=u'订阅费')    # 单位：USD
    cost = models.FloatField(null=True, blank=True, default=0)      # 成本，USD


class Settlement(models.Model):
    """
    一次结算记录
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    start_date = models.DateField(verbose_name=u'结算开始日期')
    end_date = models.DateField(verbose_name=u'结算结束日期')
    advertising_fee = models.FloatField(null=True, blank=True, verbose_name=u'广告费') # 手动
    storage_fee = models.FloatField(null=True, blank=True, verbose_name=u'仓储费')     # 手动
    total_returns = models.FloatField(null=True, blank=True, verbose_name=u'总收入')   # 计算
    sold_account = models.IntegerField(null=True, blank=True, verbose_name=u'销售数量') # 计算
    total_cost = models.FloatField(null=True, blank=True, verbose_name=u'总成本')      # 计算
    profit = models.FloatField(null=True, blank=True, verbose_name=u'利润')           # 计算
    profit_rate = models.FloatField(null=True, blank=True, verbose_name=u'利润率')     # 计算





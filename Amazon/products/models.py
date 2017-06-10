#-*- coding:utf-8 -*-
from django.db import models

# Create your models here.


class Commission(models.Model):
    """
    佣金对照表
    """
    ProductGroup = models.CharField(max_length=50, verbose_name=u'商品类型', db_index=True)
    percentage = models.FloatField()    # 比例
    min_charge = models.FloatField(default=1.0)
    price = models.FloatField(null=True, blank=True)    # 有的商品以价格区分，<=price取percentage，>price取percentage_greater
    percentage_greater = models.FloatField(null=True, blank=True)


class Product(models.Model):
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    SellerSKU = models.CharField(max_length=50, verbose_name='SKU', db_index=True)
    ASIN = models.CharField(max_length=20, null=True, blank=True, verbose_name='Asin', db_index=True)
    FNSKU = models.CharField(max_length=20, null=True, blank=True, verbose_name='FNSKU')
    Brand = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'品牌')
    Color = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'颜色')
    Amount = models.FloatField(null=True, blank=True, verbose_name=u'售价')   # 售价
    CurrencyCode = models.CharField(max_length=10, null=True, blank=True, verbose_name=u'货币单位')      # 货币代码：USD-美元
    Image = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'图标')      # 图标
    TotalSupplyQuantity = models.IntegerField(null=True, blank=True)        #  亚马逊库存
    Title = models.TextField(null=True, blank=True, verbose_name=u'亚马逊描述')             # 商城描述
    TitleCn = models.TextField(null=True, blank=True, verbose_name=u'中文描述')           # 中文描述，手动输入
    Binding = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'类型')
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
    volume_weight = models.FloatField(null=True, blank=True, verbose_name=u'体积重')        # 体积重，height*width*length/5000
    remain_count = models.IntegerField(default=0, verbose_name=u'剩余数量')       # 商品剩余数量
    cost = models.FloatField(default=0, verbose_name=u'成本')     # 当前商品成本
    last_supply = models.DateField(null=True, blank=True, verbose_name=u'上一次入库日期')
    last_oversea = models.DateField(null=True, blank=True, verbose_name=u'上一次移库日期')

    class Meta:
        unique_together = (('MarketplaceId', 'SellerSKU',),)


class InboundShipment(models.Model):
    """
    发往国内的商品信息，以商品为维度
    """
    product = models.ForeignKey(Product, related_name='supplies')
    count = models.IntegerField(verbose_name=u'数量')       # 商品数量
    # remain_count = models.IntegerField(verbose_name=u'剩余数量', default=0)    # count-发往国外的数量
    unit_price = models.FloatField(verbose_name=u'运费单价')
    total_freight = models.FloatField(verbose_name=u'总运费')
    charges = models.FloatField(null=True, blank=True, verbose_name=u'杂费')
    charges_comment = models.TextField(null=True, blank=True, verbose_name=u'杂费备注')
    ship_date = models.DateField(null=True, blank=True, verbose_name=u'到货日期')
    insert_time = models.DateTimeField(null=True, blank=True)   # 添加至数据库的时间


class OutboundShipment(models.Model):
    """
    发往国外的货件，以货件为维度
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    ShipmentId = models.CharField(max_length=50)
    ShipmentName = models.CharField(max_length=255, null=True, blank=True)      # 您为入库货件提供的唯一名称。
    LabelPrepType = models.CharField(max_length=100, null=True, blank=True)     # 入库货件必需的标签准备的类型。
    ShipmentStatus = models.CharField(max_length=30, null=True, blank=True)
    ShipFromCity = models.CharField(max_length=50, null=True, blank=True)
    ship_date = models.DateField(null=True, blank=True, verbose_name=u'发货时间')     # 发货时间
    total_freight = models.FloatField(null=True, blank=True, verbose_name=u'总运费')        # 总运费

    class Meta:
        ordering = ['-ship_date']


class OutboundShipmentItem(models.Model):
    """
    每个货件里的商品信息
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    shipment = models.ForeignKey(OutboundShipment, related_name='products')
    product = models.ForeignKey(Product, related_name='shipsOversea')
    SellerSKU = models.CharField(max_length=50, null=True, blank=True)
    FulfillmentNetworkSKU = models.CharField(max_length=50, null=True, blank=True)      # 商品的亚马逊配送网络 SKU
    QuantityShipped = models.IntegerField()     # 要配送的商品数量。
    QuantityReceived = models.IntegerField(null=True, blank=True)    # 亚马逊配送中心已接收的商品数量
    QuantityInCase = models.IntegerField(null=True, blank=True)      # 每个包装箱中的商品数量（仅针对原厂包装发货商品）。请注意，QuantityInCase x 入库货件中的包装箱数 = QuantityShipped
    unit_freight = models.FloatField(null=True, blank=True, verbose_name=u'运费单价')       # 单位：kg
    fuel_tax = models.FloatField(null=True, blank=True, verbose_name=u'燃油附加税')       # 百分比
    duty = models.FloatField(null=True, blank=True, verbose_name=u'关税')
    logistics_company = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'物流公司名称')
    logistics_id = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'物流运单号')
    package_width = models.FloatField(null=True, blank=True, verbose_name=u'外包装宽度')
    package_height = models.FloatField(null=True, blank=True, verbose_name=u'外包装高度')
    package_length = models.FloatField(null=True, blank=True, verbose_name=u'外包装长度')
    package_weight = models.FloatField(null=True, blank=True, verbose_name=u'外包装重量')
    volume_weight = models.FloatField(null=True, blank=True, verbose_name=u'体积重')
    total_freight = models.FloatField(null=True, blank=True, verbose_name=u'总运费')    # 通过计算获得：max(外箱体积重,外箱实际重)*运费单价*（1+燃油附加税） = 总运费

    class Meta:
        ordering = ['SellerSKU']


class Orders(models.Model):
    """
    销售记录
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)
    OrderType = models.CharField(max_length=50, null=True, blank=True)
    PurchaseDate = models.DateTimeField(null=True, blank=True, verbose_name=u'购买时间')
    AmazonOrderId = models.CharField(max_length=50, verbose_name=u'订单编号')
    SellerOrderId = models.CharField(null=True, blank=True, max_length=50, verbose_name=u'卖家订单号')
    Amount = models.FloatField(null=True, blank=True, verbose_name=u'售价')   # USD
    CurrencyCode = models.CharField(null=True, blank=True, max_length=10, verbose_name=u'货币单位')      # 货币代码：USD-美元
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

    class Meta:
        ordering = ['-LastUpdateDate']


class OrderItem(models.Model):
    MarketplaceId = models.CharField(max_length=30, db_index=True, null=True, blank=True)
    # 从Order同步的信息
    order = models.ForeignKey(Orders, related_name='items')
    AmazonOrderId = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    PurchaseDate = models.DateTimeField(null=True, blank=True, verbose_name=u'购买时间')
    LastUpdateDate = models.DateTimeField(null=True, blank=True)                # 上一次更新时间
    OrderStatus = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'订单状态')  # =order.OrderStatus
    # 商品信息
    product = models.ForeignKey(Product, related_name='items', null=True, blank=True)
    Binding = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'类型')
    ProductGroup = models.CharField(max_length=50, null=True, blank=True)
    ProductTypeName = models.CharField(max_length=50, null=True, blank=True)
    SellerSKU = models.CharField(null=True, blank=True, max_length=50, db_index=True)
    ASIN = models.CharField(max_length=20, null=True, blank=True)
    # 订单子项信息
    OrderItemId = models.CharField(max_length=20)
    QuantityOrdered = models.IntegerField(null=True, blank=True, verbose_name=u'销售数量')
    QuantityShipped = models.IntegerField(null=True, blank=True, verbose_name=u'已发货数量')
    ItemPrice = models.FloatField(null=True, blank=True, verbose_name=u'总价')
    ShippingPrice = models.FloatField(null=True, blank=True, verbose_name=u'运费')
    ShippingDiscount = models.FloatField(null=True, blank=True, verbose_name=u'运费折扣')
    ItemTax = models.FloatField(null=True, blank=True, verbose_name=u'订单税')
    ShippingTax = models.FloatField(null=True, blank=True, verbose_name=u'运费税')
    PromotionDiscount = models.FloatField(null=True, blank=True, verbose_name=u'促销折扣')
    # 其他收费信息
    commission_per = models.FloatField(null=True, blank=True, verbose_name=u'佣金比例')     # 根据Product.ProductGroup
    commission = models.FloatField(null=True, blank=True, verbose_name=u'佣金')   # ItemPrice * commission_per
    subscription_fee = models.FloatField(null=True, blank=True, verbose_name=u'订阅费')    # 单位：USD
    cost = models.FloatField(null=True, blank=True, default=0)      # 成本，USD


class Settlement(models.Model):
    """
    一次结算记录
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    AmazonSettlementID = models.CharField(max_length=100)
    TotalAmount = models.FloatField(null=True, blank=True)
    StartDate = models.DateTimeField(null=True, blank=True, verbose_name=u'结算开始日期')
    EndDate = models.DateTimeField(null=True, blank=True, verbose_name=u'结算结束日期')
    subscribe_fee = models.FloatField(null=True, blank=True, verbose_name=u'订阅费') # 手动
    total_returns = models.FloatField(null=True, blank=True, verbose_name=u'总收入')   # 计算
    sold_account = models.IntegerField(null=True, blank=True, verbose_name=u'销售数量') # 计算
    total_cost = models.FloatField(null=True, blank=True, verbose_name=u'总成本')      # 计算
    profit = models.FloatField(null=True, blank=True, verbose_name=u'利润')           # 计算
    profit_rate = models.FloatField(null=True, blank=True, verbose_name=u'利润率')     # 计算

    class Meta:
        ordering = ['-EndDate']


class ProductSettlement(models.CharField):
    settlement = models.ForeignKey(Settlement, related_name='products')
    advertising_fee = models.FloatField(null=True, blank=True)       # 广告费
    storage_fee = models.FloatField(null=True, blank=True)           # 仓储费
    quantity = models.IntegerField(null=True, blank=True)           # 销售数量
    sales_amount = models.FloatField(null=True, blank=True)         # 总销售
    total_cost = models.FloatField(null=True, blank=True)           # 总成本
    profit = models.FloatField(null=True, blank=True, verbose_name=u'利润')
    profit_rate = models.FloatField(null=True, blank=True, verbose_name=u'利润率')


class Refund(models.Model):
    """
    退款
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    settlement = models.ForeignKey(Settlement, null=True, blank=True, related_name='refunds')   # 关联的结算周期
    AdjustmentID = models.CharField(max_length=100)
    AmazonOrderId = models.CharField(max_length=50, null=True, blank=True)
    MarketplaceName = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'商城名字')     # 如：Amazon.com
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')


class RefundItem(models.Model):
    """
    退款中的商品子项
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    settlement = models.ForeignKey(Settlement, null=True, blank=True)   # 关联的结算周期
    MerchantAdjustmentItemID = models.CharField(max_length=50)
    refund = models.ForeignKey(Refund, null=True, blank=True, related_name='items')
    OrderItemId = models.CharField(max_length=50, null=True, blank=True)
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')
    product = models.ForeignKey(Product, null=True, blank=True, related_name='refunds')
    SellerSKU = models.CharField(max_length=50, null=True, blank=True)
    Principal = models.FloatField(null=True, blank=True)        # 商品总价
    Shipping = models.FloatField(null=True, blank=True)         # 运费
    Commission = models.FloatField(null=True, blank=True)       # 退还的商品佣金
    RefundCommission = models.FloatField(null=True, blank=True) # 退货抽取的佣金
    PromotionPrincipal = models.FloatField(null=True, blank=True)   # 退还的销售促销
    PromotionShipping = models.FloatField(null=True, blank=True)    # 退还的运费促销
    ShippingChargeback = models.FloatField(null=True, blank=True)
    RestockingFee = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-PostedDate']


class OtherTransaction(models.Model):
    """
    其他服务费
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    settlement = models.ForeignKey(Settlement, null=True, blank=True, related_name='other_transactions')   # 关联的结算周期
    TransactionID = models.CharField(max_length=50)
    AmazonOrderId = models.CharField(max_length=50, null=True, blank=True)
    TransactionType = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'服务费类型') # RemovalComplete:亚马逊物流移除费用
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')
    Amount = models.FloatField(null=True, blank=True, verbose_name=u'总计')
    FBACustomerReturnPerUnitFee = models.FloatField(null=True, blank=True)    # FBA Customer Return Per Unit Fee,

    class Meta:
        ordering = ['-PostedDate']


class SellerDealPayment(models.Model):
    """
    促销费用
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    settlement = models.ForeignKey(Settlement, null=True, blank=True, related_name='seller_deal_payments')   # 关联的结算周期
    DealID = models.CharField(max_length=255)
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')
    DealDescription = models.CharField(max_length=100, null=True, blank=True)
    MarketplaceName = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'商城名字')     # 如：Amazon.com
    TransactionType = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'服务费类型')     # Lightning Deal Fee：秒杀费
    PaymentReason = models.CharField(max_length=100, null=True, blank=True)
    DealFeeType = models.CharField(max_length=100, null=True, blank=True)      # 促销类型
    DealFeeAmount = models.FloatField(null=True, blank=True)                   # 促销总费用

    class Meta:
        ordering = ['-PostedDate']


class AdvertisingTransactionDetails(models.Model):
    """
    广告费用
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    settlement = models.ForeignKey(Settlement, null=True, blank=True, related_name='advertising_transactions')   # 关联的结算周期
    InvoiceId = models.CharField(max_length=100, verbose_name=u'发票ID')
    TransactionType = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'服务费类型')
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')
    BaseAmount = models.FloatField(null=True, blank=True)
    TransactionAmount = models.FloatField(null=True, blank=True)


class SettleOrder(models.Model):
    """
    销售记录
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    settlement = models.ForeignKey(Settlement, null=True, blank=True, related_name='orders')   # 关联的结算周期
    MarketplaceId = models.CharField(max_length=30, db_index=True)
    MarketplaceName = models.CharField(max_length=100, null=True, blank=True)
    AmazonOrderId = models.CharField(max_length=50, verbose_name=u'订单编号')
    ShipmentID = models.CharField(null=True, blank=True, max_length=50, verbose_name=u'物流ID')
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')   # USD

    class Meta:
        ordering = ['-PostedDate']


class SettleOrderItem(models.Model):
    settlement = models.ForeignKey(Settlement, null=True, blank=True, related_name='order_items')   # 关联的结算周期
    MarketplaceId = models.CharField(max_length=30, db_index=True, null=True, blank=True)
    # 从Order同步的信息
    order = models.ForeignKey(SettleOrder, related_name='items')
    OrderItemId = models.CharField(max_length=20)
    AmazonOrderId = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')   # USD
    # 商品信息
    product = models.ForeignKey(Product, related_name='settle_items', null=True, blank=True)
    SellerSKU = models.CharField(max_length=50, null=True, blank=True)

    # 销售环节
    UnitPrice = models.FloatField(null=True, blank=True, verbose_name=u'单价')    # Principal/Quantity
    Quantity = models.IntegerField(null=True, blank=True)
    Principal = models.FloatField(null=True, blank=True, verbose_name=u'商品总价')
    Shipping = models.FloatField(null=True, blank=True, verbose_name=u'运费')
    FBAPerUnitFulfillmentFee = models.FloatField(null=True, blank=True, verbose_name=u'亚马逊物流基础服务费')
    ShippingChargeback = models.FloatField(null=True, blank=True)       # 买家运费付款
    GiftwrapChargeback = models.FloatField(null=True, blank=True)
    GiftWrap = models.FloatField(null=True, blank=True)
    FBAPerOrderFulfillmentFee = models.FloatField(null=True, blank=True)
    Commission = models.FloatField(null=True, blank=True, verbose_name=u'佣金')
    PromotionPrincipal = models.FloatField(null=True, blank=True, verbose_name=u'销售促销返点')   # 从销售收入中扣除
    PromotionShipping = models.FloatField(null=True, blank=True, verbose_name=u'运费促销返点')    # 从销售收入中扣除
    Amount = models.FloatField(null=True, blank=True, verbose_name=u'实收金额') #　以上

    # 成本
    subscription_fee = models.FloatField(null=True, blank=True, verbose_name=u'订阅费')    # 单位：USD
    cost = models.FloatField(null=True, blank=True, default=0)      # 成本，USD

    class Meta:
        ordering = ['-PostedDate']


class ProductReturn(models.Model):
    product = models.ForeignKey(Product)
    settlement = models.ForeignKey(Settlement, related_name='returns')
    snapshot_date = models.DateTimeField()
    type = models.CharField(max_length=20)
    SellerSKU = models.CharField(max_length=50)
    quantity = models.IntegerField()
    disposition = models.CharField(max_length=20)

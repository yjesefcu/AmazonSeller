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
    domestic_inventory = models.IntegerField(default=0, verbose_name=u'国内库存')          # 商品剩余数量
    amazon_inventory = models.IntegerField(default=0, verbose_name=u'亚马逊库存')
    supply_cost = models.FloatField(null=True, blank=True)    # 国内成本：包括商品单价和运费
    shipment_cost = models.FloatField(null=True, blank=True)     # 国外成本：国内至亚马逊的运费
    cost = models.FloatField(default=0, verbose_name=u'成本')     # 当前商品成本
    last_supply = models.DateField(null=True, blank=True, verbose_name=u'上一次入库日期')
    last_oversea = models.DateField(null=True, blank=True, verbose_name=u'上一次移库日期')
    sold_count = models.IntegerField(default=0, verbose_name=u'已销售数量')

    class Meta:
        unique_together = (('MarketplaceId', 'SellerSKU',),)
        ordering = ['SellerSKU']


class InboundShipment(models.Model):
    """
    发往国内的商品信息，以商品为维度
    """
    product = models.ForeignKey(Product, related_name='supplies')
    count = models.IntegerField(verbose_name=u'数量')       # 商品数量
    inventory = models.IntegerField(verbose_name=u'库存', default=0)      # 用于计算成本，在计算完订单后扣除
    real_inventory = models.IntegerField(null=True, blank=True)            # 实际库存
    # remain_count = models.IntegerField(verbose_name=u'剩余数量', default=0)    # count-发往国外的数量
    unit_price = models.FloatField(verbose_name=u'商品单价')
    total_freight = models.FloatField(verbose_name=u'总运费')
    charges = models.FloatField(null=True, blank=True, verbose_name=u'杂费')
    charges_comment = models.TextField(null=True, blank=True, verbose_name=u'杂费备注')
    ship_date = models.DateField(null=True, blank=True, verbose_name=u'到货日期')
    insert_time = models.DateTimeField(null=True, blank=True)   # 添加至数据库的时间
    unit_cost = models.FloatField(null=True, blank=True, verbose_name=u'单位成本')  # 包括单价与运费

    class Meta:
        ordering = ('-ship_date', )

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
    #     super(InboundShipment, self).save(force_insert, force_update, using, update_fields)
    #     # 更新Product.domestic_inventory
    #     self.product.domestic_inventory += self.count
    #     self.product.save()


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
    unit_freight = models.FloatField(null=True, blank=True, verbose_name=u'运费单价')

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
    QuantityShipped = models.IntegerField(null=True, blank=True, default=0)     # 要配送的商品数量。
    QuantityReceived = models.IntegerField(null=True, blank=True, default=0)    # 亚马逊配送中心已接收的商品数量
    QuantityInCase = models.IntegerField(null=True, blank=True, default=0)      # 每个包装箱中的商品数量（仅针对原厂包装发货商品）。请注意，QuantityInCase x 入库货件中的包装箱数 = QuantityShipped
    unit_freight = models.FloatField(null=True, blank=True, default=0, verbose_name=u'运费单价')       # 单位：kg
    fuel_tax = models.FloatField(null=True, blank=True, default=0, verbose_name=u'燃油附加税')       # 百分比
    duty = models.FloatField(null=True, blank=True, default=0, verbose_name=u'关税')
    logistics_company = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'物流公司名称')
    logistics_id = models.CharField(max_length=100, null=True, blank=True, verbose_name=u'物流运单号')
    package_width = models.FloatField(null=True, blank=True, verbose_name=u'外包装宽度')
    package_height = models.FloatField(null=True, blank=True, verbose_name=u'外包装高度')
    package_length = models.FloatField(null=True, blank=True, verbose_name=u'外包装长度')
    package_weight = models.FloatField(null=True, blank=True, verbose_name=u'外包装重量')
    volume_weight = models.FloatField(null=True, blank=True, verbose_name=u'体积重')

    total_freight = models.FloatField(null=True, blank=True, verbose_name=u'总运费')    # 通过计算获得：max(外箱体积重,外箱实际重)*运费单价*（1+燃油附加税） = 总运费
    inventory = models.IntegerField(null=True, blank=True, default=0, verbose_name=u'库存')
    unit_cost = models.FloatField(null=True, blank=True, verbose_name=u'移库单位成本')
    # domestic_unit_cost = models.FloatField(null=True, blank=True, verbose_name=u'入库单位成本')   # = InboundShipment.unit_cost
    # total_unit_cost = models.FloatField(null=True, blank=True, verbose_name=u'总的单位成本')  # = unit_cost + domestic_unit_cost， 即Product.unit_cost

    class Meta:
        ordering = ['SellerSKU', '-shipment__ship_date']


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
    subscription_fee_adjust = models.FloatField(null=True, blank=True, verbose_name=u'补偿金额')    # OtherTransaction.SubscriptionFeeAdj的总和
    balanced_adjust = models.FloatField(null=True, blank=True, verbose_name=u'余额调整')
    advertising_fee = models.FloatField(null=True, blank=True, verbose_name=u'从商品中统计的广告费')
    advertising_fee_adjust = models.FloatField(null=True, blank=True, verbose_name=u'实际支付的总广告费')   # 如果advertising_fee<advertising_fee_adjust，那么需要将多余的平均到商品中

    income = models.FloatField(null=True, blank=True, verbose_name=u'总收入')   # 计算
    amazon_cost = models.FloatField(null=True, blank=True, verbose_name=u'亚马逊所收费用')
    promotion = models.FloatField(null=True, blank=True, verbose_name=u'促销返点')
    amount = models.FloatField(null=True, blank=True, verbose_name=u'实收')
    quantity = models.IntegerField(null=True, blank=True, verbose_name=u'销售数量')           # 销售数量
    total_cost = models.FloatField(null=True, blank=True, verbose_name=u'总成本')      # 计算
    profit = models.FloatField(null=True, blank=True, verbose_name=u'利润')           # 计算
    profit_rate = models.FloatField(null=True, blank=True, verbose_name=u'利润率')     # 计算

    class Meta:
        ordering = ['-EndDate']


class ProductSettlement(models.Model):
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    settlement = models.ForeignKey(Settlement, related_name='products')
    product = models.ForeignKey(Product)
    advertising_fee = models.FloatField(null=True, blank=True)       # 广告费，需以负数保存
    storage_fee = models.FloatField(null=True, blank=True)           # 仓储费，需以负数保存

    quantity = models.IntegerField(null=True, blank=True)           # 销售数量
    income = models.FloatField(null=True, blank=True)         # 总销售
    amazon_cost = models.FloatField(null=True, blank=True, verbose_name=u'亚马逊所收费用')
    promotion = models.FloatField(null=True, blank=True, verbose_name=u'促销返点')
    amount = models.FloatField(null=True, blank=True, verbose_name=u'实收')
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
    MerchantAdjustmentItemID = models.CharField(max_length=50, null=True, blank=True)
    refund = models.ForeignKey(Refund, null=True, blank=True, related_name='items')
    AmazonOrderId = models.CharField(max_length=50, null=True, blank=True)
    OrderItemId = models.CharField(max_length=50, null=True, blank=True)
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')
    product = models.ForeignKey(Product, null=True, blank=True, related_name='refunds')     # product为空表示汇总记录
    SellerSKU = models.CharField(max_length=50, null=True, blank=True)
    PriceAdjustmentType = models.CharField(max_length=50, null=True, blank=True)
    PriceAdjustmentAmount = models.FloatField(null=True, blank=True)
    Principal = models.FloatField(null=True, blank=True)        # 商品总价
    Shipping = models.FloatField(null=True, blank=True)         # 运费
    Commission = models.FloatField(null=True, blank=True)       # 退还的商品佣金
    RefundCommission = models.FloatField(null=True, blank=True) # 退货抽取的佣金
    PromotionPrincipal = models.FloatField(null=True, blank=True)   # 退还的销售促销
    PromotionShipping = models.FloatField(null=True, blank=True)    # 退还的运费促销
    ShippingChargeback = models.FloatField(null=True, blank=True)
    RestockingFee = models.FloatField(null=True, blank=True)

    FBAReturnFee = models.FloatField(null=True, blank=True, verbose_name=u'退货费')    # = OtherTransaction中TransactionType= FBACustomerReturn的记录的Amount

    order_item = models.ForeignKey('SettleOrderItem', null=True, blank=True)        # 退款关联的订单
    quantity = models.IntegerField(null=True, blank=True)   # 销售的数量，从SettleOrderItem中读取
    cost = models.FloatField(null=True, blank=True, verbose_name=u'单位成本')         # 成本，应该为正数
    # 汇总
    total_cost = models.FloatField(null=True, blank=True, verbose_name=u'总成本')  # subscription_fee + cost
    income = models.FloatField(null=True, blank=True, verbose_name=u'订单付款') #　= PriceAdjustmentAmount
    amazon_cost = models.FloatField(null=True, blank=True, verbose_name=u'亚马逊所收费用')
    promotion = models.FloatField(null=True, blank=True, verbose_name=u'促销返点')
    amount = models.FloatField(null=True, blank=True, verbose_name=u'实收') #　=Principal
    profit = models.FloatField(null=True, blank=True, default=0)    # 利润

    is_total = models.BooleanField(default=False)      # 是否是汇总项

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
    TransactionType = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'服务费类型') # RemovalComplete:亚马逊物流移除费用，DisposalComplete：弃置服务费
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')
    Amount = models.FloatField(null=True, blank=True, verbose_name=u'总计')
    refund_item = models.ForeignKey('RefundItem', null=True, blank=True)        # AmazonOrderId对应的SettleOrderItem，为空说明没找到对应的订单

    class Meta:
        ordering = ['-PostedDate']


class OtherTransactionFee(models.Model):
    # 主要是移除和弃置，需要关联 ProductRemovalItem一起计算
    # 以下数据与关联的OtherTransaction一致
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    settlement = models.ForeignKey(Settlement, related_name=u'removal_products')
    transaction = models.ForeignKey(OtherTransaction, related_name='fees')
    TransactionID = models.CharField(max_length=50)
    AmazonOrderId = models.CharField(max_length=50, null=True, blank=True)
    TransactionType = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'服务费类型') # RemovalComplete:亚马逊物流移除费用，DisposalComplete：弃置服务费
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')
    # 以下为Fee信息
    Type = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'付款详情')
    Amount = models.FloatField(null=True, blank=True, verbose_name=u'总计')


class ProductRemovalItem(models.Model):
    """
    移除商品信息
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    settlement = models.ForeignKey(Settlement)
    RequestDate = models.DateTimeField(null=True, blank=True)
    UpdateDate = models.DateTimeField(null=True, blank=True)
    OrderId = models.CharField(max_length=50, null=True, blank=True)
    OrderType = models.CharField(max_length=20, null=True, blank=True)     # Return/Disposal
    OrderStatus = models.CharField(max_length=20, null=True, blank=True)
    SellerSKU = models.CharField(max_length=50, null=True, blank=True)
    FNSKU = models.CharField(max_length=50, null=True, blank=True)
    Disposition = models.CharField(max_length=20, null=True, blank=True)       # Sellable/Unsellable
    Quantity = models.IntegerField(null=True, blank=True)
    Fee = models.FloatField(null=True, blank=True)       # 弃置费用
    # 计算所得
    product = models.ForeignKey(Product, related_name='removals', null=True, blank=True)
    cost = models.FloatField(null=True, blank=True, verbose_name=u'单位成本')

    # 汇总
    total_cost = models.FloatField(null=True, blank=True, verbose_name=u'总成本')  # subscription_fee + cost
    amazon_cost = models.FloatField(null=True, blank=True, verbose_name=u'亚马逊所收费用')     # = Fee
    amount = models.FloatField(null=True, blank=True, verbose_name=u'实收') #　= amazon_cost
    profit = models.FloatField(null=True, blank=True, default=0)    # 利润

    is_total = models.BooleanField(default=False)      # 是否是汇总项


class OtherTransactionItem(models.Model):
    # 赔偿
    # 以下数据与关联的OtherTransaction一致
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    settlement = models.ForeignKey(Settlement)
    transaction = models.ForeignKey(OtherTransaction, related_name='items', null=True, blank=True)
    TransactionID = models.CharField(max_length=50, null=True, blank=True)
    AmazonOrderId = models.CharField(max_length=50, null=True, blank=True)
    TransactionType = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'服务费类型') # INCORRECT_FEES_ITEMS：费用更正，无需计算成本
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')
    # 赔偿明细
    SellerSKU = models.CharField(max_length=50, null=True, blank=True)
    Quantity = models.IntegerField(null=True, blank=True)
    Amount = models.FloatField(null=True, blank=True)

    # 其他
    product = models.ForeignKey(Product, null=True, blank=True)
    cost = models.FloatField(null=True, blank=True, verbose_name=u'单位成本')     # 如果是仓库丢失，需要扣除成本

    # 汇总
    total_cost = models.FloatField(null=True, blank=True, verbose_name=u'总成本')
    profit = models.FloatField(null=True, blank=True)   # 利润

    is_total = models.BooleanField(default=False)      # 是否是汇总项


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


class AdvertisingProductItems(models.Model):
    """
    广告业绩报告的数据
    """
    MarketplaceId = models.CharField(max_length=30, db_index=True)     # 市场Id
    settlement = models.ForeignKey(Settlement, null=True, blank=True, related_name='advertising_products')   # 关联的结算周期
    StartDate = models.DateTimeField(null=True, blank=True)
    EndDate = models.DateTimeField(null=True, blank=True)
    SellerSKU = models.CharField(max_length=50, null=True, blank=True)
    TotalSpend = models.FloatField(null=True, blank=True)
    product = models.ForeignKey(Product, related_name='advertising_fees')
    cost = models.FloatField(null=True, blank=True)     # cost为TotalSpend+校正费用（实际支出-所有商品综合)/商品数


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
    order = models.ForeignKey(SettleOrder, related_name='items', null=True, blank=True)
    OrderItemId = models.CharField(max_length=20, null=True, blank=True)
    AmazonOrderId = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    PostedDate = models.DateTimeField(null=True, blank=True, verbose_name=u'提交时间')   # USD
    # 商品信息
    product = models.ForeignKey(Product, related_name='settle_items', null=True, blank=True)
    SellerSKU = models.CharField(max_length=50, null=True, blank=True)

    # 销售环节
    UnitPrice = models.FloatField(null=True, blank=True, verbose_name=u'单价')    # Principal/Quantity
    Quantity = models.IntegerField(null=True, blank=True)
    Principal = models.FloatField(null=True, blank=True, verbose_name=u'订单付款')
    # Principal = models.FloatField(null=True, blank=True, verbose_name=u'商品总价')

    ShippingChargeback = models.FloatField(null=True, blank=True, verbose_name=u'买家运费付款')       # 买家运费付款
    Shipping = models.FloatField(null=True, blank=True, verbose_name=u'其他-运费')
    PromotionShipping = models.FloatField(null=True, blank=True, verbose_name=u'促销返点-运费')    # 从销售收入中扣除
    # FBAPerUnitFulfillmentFee + FBAPerOrderFulfillmentFee = 表格中的基础服务费
    FBAPerUnitFulfillmentFee = models.FloatField(null=True, blank=True, verbose_name=u'亚马逊物流基础服务费')
    FBAPerOrderFulfillmentFee = models.FloatField(null=True, blank=True)

    GiftwrapChargeback = models.FloatField(null=True, blank=True)
    GiftWrap = models.FloatField(null=True, blank=True)
    Commission = models.FloatField(null=True, blank=True, verbose_name=u'佣金')
    PromotionPrincipal = models.FloatField(null=True, blank=True, verbose_name=u'销售促销返点')   # 从销售收入中扣除

    #成本
    subscription_fee = models.FloatField(null=True, blank=True, verbose_name=u'订阅费')     # 单位：USD，负数
    supply_cost = models.FloatField(null=True, blank=True, verbose_name=u'国内运费')        # 负数， =product.supply_cost
    shipment_cost = models.FloatField(null=True, blank=True, verbose_name=u'国际运费')       # 负数， =product.shipment_cost
    cost = models.FloatField(null=True, blank=True, default=0, verbose_name=u'单位成本')      # =product.cost，USD            # 负数

    # 汇总
    total_cost = models.FloatField(null=True, blank=True, verbose_name=u'总成本')  # subscription_fee + cost
    income = models.FloatField(null=True, blank=True, verbose_name=u'订单付款') #　=Principal
    amazon_cost = models.FloatField(null=True, blank=True, verbose_name=u'亚马逊所收费用')
    promotion = models.FloatField(null=True, blank=True, verbose_name=u'促销返点')
    amount = models.FloatField(null=True, blank=True, verbose_name=u'实收') #　=Principal
    profit = models.FloatField(null=True, blank=True, default=0)    # 利润

    is_total = models.BooleanField(default=False)      # 是否是汇总项

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


class SettlementDataRecord(models.Model):
    """
    记录settlement相关数据是否已更新到数据库
    """
    SETTLEMENT = 'Settlement'
    REMOVAL = 'Removal'
    ADVERTISE = 'Advertising'

    settlement = models.ForeignKey(Settlement)
    data_type = models.CharField(max_length=20)     # 数据类型
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

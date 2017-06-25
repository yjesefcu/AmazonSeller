#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import os, datetime, urllib, json, logging
import dateutil.parser
from django.conf import settings
from django.db.models import Q, F, Sum
from amazon_services.service import OrderService, OrderItemService
from models import *


logger = logging.getLogger('product')
DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def to_float(value):
    if not value:
        return 0
    return float(value)


def sum_queryset(query_set, field):
    return to_float(query_set.aggregate(total=Sum(field)).get('total'))

def get_float(data, key):
    value = data.get(key)
    if not value:
        return 0
    return float(value)


class OrderStatus(enumerate):
    Pending = 'Pending'     # 等待付款
    Canceled = 'Canceled'   # 订单取消
    PartiallyShipped = 'PartiallyShipped'   #
    Unshipped = 'Unshipped' # 已付款未发货
    Shipped = 'Shipped'     # 已发货
    Unfulfillable = 'Unfulfillable'
    PendingAvailability = 'PendingAvailability'


def update_order_to_db(order_data, items):
    order, created = Orders.objects.get_or_create(MarketplaceId=order_data['MarketplaceId'],
                                                  AmazonOrderId=order_data['AmazonOrderId'])
    if not created and order.OrderStatus and order.OrderStatus == order_data['OrderStatus']:  # 订单状态没有变化
        return
    for field, value in order_data.items():
        setattr(order, field, value)
    order.save()
    # 更新items
    for item in items:
        _update_item_to_db(order, item)
    return order


def _update_item_to_db(order, item_data):
    """
    将OrderItem数据更新至数据库
    """
    item, created = OrderItem.objects.get_or_create(order=order, OrderItemId=item_data['OrderItemId'])
    if created:
        product, created = Product.objects.get_or_create(SellerSKU=item_data['SellerSKU'],
                                                         MarketplaceId=order.MarketplaceId)
        item.product = product
        item.AmazonOrderId = order.AmazonOrderId
        item.PurchaseDate = order.PurchaseDate
        item.MarketplaceId = order.MarketplaceId
        if product.Binding:
            item.Binding = product.Binding
            item.ProductGroup = product.ProductGroup
            item.ProductTypeName = product.ProductTypeName
            item.AmazonOrderId = order.AmazonOrderId
            item.MarketplaceId = order.MarketplaceId
    item.OrderStatus = order.OrderStatus
    item.LastUpdateDate = order.LastUpdateDate
    if 'ItemPrice' in item_data and item_data['ItemPrice'] and not item.ItemPrice:
        # 计算佣金
        item.commission = _calc_commission(item.Binding, item_data['ItemPrice'])
    # 更新其他信息
    for field, value in item_data.items():
        setattr(item, field, value)
    item.save()


def _calc_commission(binding, price):
    if not binding or not price:
        return None
    try:
        commission = Commission.objects.get(ProductGroup=binding)
    except Commission.DoesNotExist, ex:
        return None
    if not commission.price:
        return max(price * commission.percentage, commission.min_charge)
    # 如果佣金按价格区分
    if price <= commission.price:
        return max(price * commission.percentage, commission.min_charge)
    return commission.percentage_greater


def update_product_to_db(product_data):
    """
    """
    product, created = Product.objects.get_or_create(MarketplaceId=product_data['MarketplaceId'],
                                                     SellerSKU=product_data['SellerSKU'])
    if not product.Image:
        # 下载image到本地
        image = download_image(product_data['Image'])
        if image:
            product_data['Image'] = image
    for key, value in product_data.items():
        setattr(product, key, value)
    # 计算体积重
    product.volume_weight = float(product.package_width) * float(product.package_height) \
                            * float(product.package_length) / 5000
    product.save()
    _update_order_item_after_product_created(product)       # 更新商品相关的订单的佣金


def _update_order_item_after_product_created(product):
    """
    获取商品信息后，更新订单中的佣金
    """
    for item in OrderItem.objects.filter(ProductGroup__isnull=True, product=product):
        item.Binding = product.Binding
        item.ProductGroup = product.ProductGroup
        item.ProductTypeName = product.ProductTypeName
        commission = _calc_commission(product.Binding if product.Binding else product.ProductGroup, item.ItemPrice)
        item.commission = commission
        item.save()


def create_image_path():
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    p = os.path.join(settings.MEDIA_ROOT, 'icon')
    if not os.path.exists(p):
        os.mkdir(p)
    return 'icon/' + timestamp + '.png'


def download_image(img_url):
    name = create_image_path()
    urllib.urlretrieve(img_url, os.path.join(settings.MEDIA_ROOT, name))
    return settings.MEDIA_URL + name


##################  Settlement ####################


class SettlementDbHandler(object):

    def __init__(self, market):
        self.market = market
        self.MarketplaceId = market.MarketplaceId

    def update_settlement_to_db(self, data):
        if not data:
            return None
        settlement = self._update_settlement_to_db(data['SettlementData'])
        if not settlement:
            logger.error('create settlement failed: %s', json.dumps(data['SettlementData']))
            return None
        # 更新详细内容
        if 'Order' in data:
            for item in data['Order']:
                self._update_order_to_db(settlement, item)
        if 'Refund' in data:
            for item in data['Refund']:
                self._update_refund_to_db(settlement, item)
        if 'OtherTransactions' in data:
            for item in data['OtherTransactions']:
                self._update_transaction_to_db(settlement, item)
        if 'SellerDealPayment' in data:
            for item in data['SellerDealPayment']:
                self._update_deal_payment_to_db(settlement, item)
        if 'AdvertisingTransactionDetails' in data:
            for item in data['AdvertisingTransactionDetails']:
                self._update_advertising_transaction_to_db(settlement, item)
        self._init_settlement_products(settlement)
        return settlement

    def _init_settlement_products(self, settlement):
        """
        默认创建settlement与product的关系
        :return:
        """
        records = list()
        for product in Product.objects.all():
            item = ProductSettlement(MarketplaceId=settlement.MarketplaceId, settlement=settlement, product=product)
            records.append(item)
        try:
            ProductSettlement.objects.bulk_create(records)
        except BaseException, ex:
            logger.warning('create ProductSettlement failed, settlemen id:%d', settlement.pk)

    def _update_settlement_to_db(self, data):
        if not data:
            return None
        settlement, created = Settlement.objects.get_or_create(MarketplaceId=self.MarketplaceId, AmazonSettlementID=data['AmazonSettlementID'])
        if created:
            for key, value in data.items():
                setattr(settlement, key, value)
            settlement.save()
        return settlement

    def calc_and_update_amount(self, settlement):
        """
        计算订单或退款信息中的总收入amount，并更新到数据库中
        """

    def _update_order_to_db(self, settlement, data):
        """
        更新结算订单信息至数据库
        """
        if not data:
            return None
        try:
            order = SettleOrder.objects.get(settlement=settlement, AmazonOrderId=data['AmazonOrderId'],
                                            ShipmentID=data['ShipmentID']) # 存在则返回
            print 'Order exist:　%s' % json.dumps(data)
            return order
        except SettleOrder.DoesNotExist, ex:
            pass
        items = data['items']
        del data['items']
        order = SettleOrder.objects.create(MarketplaceId=self.MarketplaceId, settlement=settlement, **data)
        # 保存订单Item至数据库
        for item in items:
            self._update_order_item_to_db(order, item)
        return order

    def _update_order_item_to_db(self, order, data):
        if not data:
            return None
        data['order'] = order
        data['MarketplaceId'] = self.MarketplaceId
        data['settlement'] = order.settlement
        data['AmazonOrderId'] = order.AmazonOrderId
        data['PostedDate'] = order.PostedDate
        product, created = Product.objects.get_or_create(SellerSKU=data['SellerSKU'],
                                                         MarketplaceId=self.MarketplaceId)
        data['product'] = product
        data['SellerSKU'] = product.SellerSKU
        # 单价
        if data['Quantity'] and int(data['Quantity']) > 0:
            data['UnitPrice'] = float(data['Principal']) / int(data['Quantity'])
        # # s实收金额
        # data['amount'] = float(data.get('Principal')) + float(data.get('Shipping', 0)) + float(data.get('FBAPerUnitFulfillmentFee', 0)) + \
        #                   float(data.get('ShippingChargeback', 0)) + float(data.get('Commission', 0)) + float(data.get('PromotionShipping', 0))
        return SettleOrderItem.objects.create(**data)

    def _update_refund_to_db(self, settlement, data):
        if not data:
            return None
        try:
            refund = Refund.objects.get(settlement=settlement, AdjustmentID=data['AdjustmentID'])
            print 'Refund exist:　%s' % json.dumps(data)
            return refund
        except Refund.DoesNotExist, ex:
            pass
        data['MarketplaceId'] = self.MarketplaceId
        data['settlement'] = settlement
        items = data['items']
        del data['items']
        refund = Refund.objects.create(**data)
        for item in items:
            self._update_refund_item_to_db(refund, item)
        return refund

    def _update_refund_item_to_db(self, refund, data):
        if not data:
            return None
        try:
            item = RefundItem.objects.get(refund=refund, MerchantAdjustmentItemID=data['MerchantAdjustmentItemID'])
            print 'RefundItem exist:　%s' % json.dumps(data)
            return item
        except RefundItem.DoesNotExist, ex:
            pass
        data['PostedDate'] = refund.PostedDate
        data['MarketplaceId'] = refund.MarketplaceId
        data['settlement'] = refund.settlement
        data['refund'] = refund
        data['AmazonOrderId'] = refund.AmazonOrderId
        product, created = Product.objects.get_or_create(SellerSKU=data['SellerSKU'],
                                                         MarketplaceId=self.MarketplaceId)
        data['product'] = product
        data['SellerSKU'] = product.SellerSKU
        # 获取该订单的商品数量、以及退款的总额
        try:
            soi = SettleOrderItem.objects.get(OrderItemId=data['OrderItemId'])
            data['order_item'] = soi
            data['quantity'] = soi.Quantity
        except SettleOrderItem.DoesNotExist, ex:
            data['quantity'] = self._get_order_item_quantity_from_amazon(data['OrderItemId'], data['AmazonOrderId'])
        # data['amount'] = get_float(data, 'PriceAdjustmentAmount') + get_float(data, 'Shipping') + get_float(data, 'Commission') + \
        #                  get_float(data, 'RefundCommission') + get_float(data, 'PromotionPrincipal') + \
        #                  get_float(data, 'PromotionShipping') + get_float(data, 'ShippingChargeback') + \
        #                  get_float(data, 'ShippingChargeback')

        # 找到对应的订单信息
        return RefundItem.objects.create(**data)

    def _get_order_item_quantity_from_amazon(self, order_item_id, amazon_order_id):
        # 从亚马逊请求订单数量
        from amazon_services.models import MarketAccount
        market = MarketAccount.objects.get(MarketplaceId=self.MarketplaceId)
        orders = OrderItemService(market).list_items(amazon_order_id)
        for order in orders:
            if order['OrderItemId'] == order_item_id:

                return order.get('QuantityShipped', 0)
        logger.error('cannot get order item from amazon: %s', amazon_order_id)
        return None


    def _update_transaction_to_db(self, settlement, data):
        if not data:
            return None
        try:
            obj = OtherTransaction.objects.get(settlement=settlement, TransactionID=data['TransactionID'])
            print 'Transaction already exist: %s' % data['TransactionID']
            return obj
        except OtherTransaction.DoesNotExist, ex:
            pass
        data['MarketplaceId'] = self.MarketplaceId
        data['settlement'] = settlement
        fees = data.get('fees', None)
        items = data.get('items', None)
        if 'fees' in data:
            del data['fees']
        if 'items' in data:
            del data['items']
        obj = OtherTransaction.objects.create(**data)
        self._update_transaction_fees_to_db(obj, fees)
        self._update_transaction_items_to_db(obj, items)
        self._update_custom_return_fee(settlement)      # 将FBACustomReturn的退货费用更新到退款表中
        return obj

    def _update_transaction_fees_to_db(self, transaction, data):
        if not data:
            return
        fields = ['MarketplaceId', 'TransactionID', 'AmazonOrderId', 'TransactionType', 'PostedDate']
        for item in data:
            for field in fields:
                item[field] = getattr(transaction, field)
            OtherTransactionFee.objects.create(transaction=transaction, settlement=transaction.settlement, **item)

    def _update_transaction_items_to_db(self, transaction, data):
        if not data:
            return
        fields = ['MarketplaceId', 'TransactionID', 'AmazonOrderId', 'TransactionType', 'PostedDate']
        for item in data:
            for field in fields:
                item[field] = getattr(transaction, field)
            product, created = Product.objects.get_or_create(MarketplaceId=transaction.MarketplaceId, SellerSKU=item['SellerSKU'])
            OtherTransactionItem.objects.create(transaction=transaction, settlement=transaction.settlement, product=product, **item)

    def _update_deal_payment_to_db(self, settlement, data):
        if not data:
            return None
        try:
            obj = SellerDealPayment.objects.get(settlement=settlement, DealID=data['DealID'])
            print 'SellerDealPayment exist:　%s' % json.dumps(data)
            return obj
        except SellerDealPayment.DoesNotExist, ex:
            pass
        data['MarketplaceId'] = self.MarketplaceId
        data['settlement'] = settlement
        return SellerDealPayment.objects.create(**data)

    def _update_advertising_transaction_to_db(self, settlement, data):
        if not data:
            return None
        try:
            obj = AdvertisingTransactionDetails.objects.get(settlement=settlement, InvoiceId=data['InvoiceId'])
            print 'Advertising exist:　%s' % json.dumps(data)
            return obj
        except AdvertisingTransactionDetails.DoesNotExist, ex:
            pass
        data['MarketplaceId'] = self.MarketplaceId
        data['settlement'] = settlement
        return AdvertisingTransactionDetails.objects.create(**data)

    def _update_custom_return_fee(self, settlement):
        """
        退货费
        """
        return_fees = OtherTransaction.objects.filter(settlement=settlement, TransactionType='FBACustomerReturn')
        for fee in return_fees:
            try:
                refund = RefundItem.objects.get(AmazonOrderId=fee.AmazonOrderId)
                fee.refund_item = refund
                fee.save()
                refund.FBAReturnFee = fee.Amount     # 将退货费加到refund里
                refund.amount += to_float(fee.Amount)
                refund.save()
            except RefundItem.DoesNotExist, ex:
                continue
            except RefundItem.MultipleObjectsReturned, ex:
                logger.error('FBACustomReturn: multi object return when find AmazonOrderId in RefundItem:%s', fee.AmazonOrderId)


class RemovalDbHandler(object):

    def update_to_db(self, settlement, data):
        results = list()
        start_date = settlement.StartDate.strftime(DT_FORMAT)
        end_date = settlement.EndDate.strftime(DT_FORMAT)
        for item in data:
            update_data = dateutil.parser.parse(item['UpdateDate']).replace(tzinfo=None).strftime(DT_FORMAT)
            if update_data > end_date \
                or update_data < start_date:   # 如果报告日期超出结算日期，则不处理
                continue
            try:
                obj = ProductRemovalItem.objects.get(OrderId=item['OrderId'], SellerSKU=item['SellerSKU'],
                                                     RequestDate=item['RequestDate'])
                results.append(obj)
            except ProductRemovalItem.DoesNotExist,ex:
                item['settlement'] = settlement
                item['MarketplaceId'] = settlement.MarketplaceId
                product, created = Product.objects.get_or_create(SellerSKU=item['SellerSKU'], MarketplaceId=settlement.MarketplaceId)
                item['product'] = product
                item['Fee'] = -float(item['Fee'])
                results.append(ProductRemovalItem.objects.create(**item))
        return results


def update_product_advertising_to_db(settlement, data):
    """
    同步广告业绩报告数据到数据库
    :param settlement:
    :param data:
    """
    def _format_datetime(d):
        if d.endswith('PDT'):
            return d[0: len(d)-4]
        return d

    for item in data:
        item['MarketplaceId'] = settlement.MarketplaceId
        item['settlement'] = settlement
        item['StartDate'] = _format_datetime(item['StartDate'])
        item['EndDate'] = _format_datetime(item['EndDate'])
        product, created = Product.objects.get_or_create(MarketplaceId=settlement.MarketplaceId, SellerSKU=item['SellerSKU'])
        item['product'] = product
        item['cost'] = -float(item['TotalSpend'])
        AdvertisingProductItems.objects.create(**item)


#################  成本计算 ####################
class CostCalculate(object):

    def __init__(self):
        pass

    @classmethod
    def calc_current_cost(cls, product):
        """
        计算商品的当前成本
        """
        cost1 = cls._calc_supply_cost(product)
        cost2 = cls._calc_shipment_cost(product)
        product.supply_cost = cost1
        product.shipment_cost = cost2
        product.cost = cost1 + cost2
        product.save()
        return product.cost

    @classmethod
    def _calc_supply_cost(cls, product):
        """
        计算国内运费单价成本
        """
        supplies = InboundShipment.objects.filter(product=product, inventory__gt=0)
        quantity = 0    # 总数量
        amount = 0      # 总成本
        for supply in supplies:
            quantity += supply.inventory
            amount += supply.inventory * supply.unit_cost
        return amount/quantity if quantity else 0

    @classmethod
    def _calc_shipment_cost(self, product):
        """
        计算当前移库单位成本
        """
        shipments = OutboundShipmentItem.objects.filter(product=product, inventory__gt=0)
        quantity = 0
        amount = 0
        for s in shipments:
            quantity += s.inventory
            amount += s.inventory * s.unit_cost
        return amount/quantity if quantity else 0


#################  Settlement ####################
class ProductProfitCalc(object):

    def __init__(self, settlement):
        self.settlement = settlement
        self.sale_quantity = 0
        self.unfound_refund_quantity = 0

    def _clear(self, product):
        """
        清除，主要是恢复库存，不影响时间成本的计算
        :param product:
        :return:
        """
        """
        清除计算的结果
        :return:
        """
        try:
            ps = ProductSettlement.objects.get(settlement=self.settlement, product=product)
            if ps.quantity:
                self._update_inventory(product, -ps.quantity)        # 先将库存补充上
        except ProductSettlement.DoesNotExist, ex:
            return

    def calc_product_profit(self, product):
        # 首先更新商品当前单位成本
        self.sale_quantity = 0       # 每个商品计算时都先清零
        self.unfound_refund_quantity = 0
        self._clear(product)    # 先恢复库存
        CostCalculate.calc_current_cost(product)
        self._calc_order_profit(product)
        self._calc_with_refunds(product)
        self._calc_removals(product)
        self._calc_with_refunds(product)
        self._calc_lost(product)
        advertising_cost = self._calc_advertising(product)
        # 更新库存
        self._update_inventory(product, self.sale_quantity)
        ps, created = ProductSettlement.objects.get_or_create(settlement=self.settlement, product=product)
        ps.quantity = self.sale_quantity

        order_total = None
        refund_total = None
        removal_total = None
        lost_total = None
        # 统计
        order_total = SettleOrderItem.objects.get(settlement=self.settlement, product=product, is_total=True)
        refund_total = RefundItem.objects.get(settlement=self.settlement, product=product, is_total=True)
        removal_total = ProductRemovalItem.objects.get(settlement=self.settlement, product=product, is_total=True)
        lost_total = OtherTransactionItem.objects.get(settlement=self.settlement, product=product, is_total=True)

        ps.quantity = order_total.Quantity + refund_total.quantity + removal_total.Quantity + lost_total.Quantity
        ps.income = order_total.income + refund_total.income
        ps.amazon_cost = order_total.amazon_cost + refund_total.amazon_cost + removal_total.amazon_cost
        ps.promotion = order_total.promotion + refund_total.promotion
        ps.amount = order_total.amount + refund_total.amount + removal_total.amount + lost_total.Amount

        ps.advertising_fee = -advertising_cost
        ps.total_cost = order_total.total_cost + refund_total.total_cost + removal_total.total_cost + lost_total.total_cost - advertising_cost
        ps.profit = order_total.profit + refund_total.profit + removal_total.profit + lost_total.profit
        ps.profit_rate = ps.profit / ps.income if ps.income else 0
        ps.save()

    def _calc_order_profit(self, product):
        """
        计算订单的收入支出
        :param product:
        :return: 数量、实收、成本
        """
        orders = SettleOrderItem.objects.filter(product=product, settlement=self.settlement)
        for order in orders:
            self._calc_order_cost(product, order)

        # 计算汇总信息并记录
        total_item, created = SettleOrderItem.objects.get_or_create(settlement=self.settlement, product=product, is_total=True)
        query_set = SettleOrderItem.objects.filter(settlement=self.settlement, product=product, is_total=False)
        total_item.Quantity = sum_queryset(query_set, 'Quantity')
        total_item.promotion = sum_queryset(query_set, 'promotion')
        total_item.income = sum_queryset(query_set, 'income')
        total_item.amazon_cost = sum_queryset(query_set, 'amazon_cost')
        total_item.amount = sum_queryset(query_set, 'amount')
        total_item.total_cost = sum_queryset(query_set, 'total_cost')
        total_item.profit = sum_queryset(query_set, 'profit')
        total_item.save()

    def _calc_order_cost(self, product, order):
        """
        计算每个订单的成本
        :return:
        """
        subscribe_fee = order.subscription_fee if order.subscription_fee else 0
        # if not order.Principal:
        #     logger.info('order %s Principal is None or 0', order.AmazonOrderId)
        #     return subscribe_fee
        order.supply_cost = -product.supply_cost
        order.shipment_cost = -product.shipment_cost
        order.cost = -product.cost
        order.income = order.Principal
        order.amazon_cost = to_float(order.FBAPerUnitFulfillmentFee) + to_float(order.FBAPerOrderFulfillmentFee) \
                              + to_float(order.Commission)
        order.promotion = to_float(order.PromotionShipping) + to_float(order.PromotionPrincipal)
        order.amount = to_float(order.income) + to_float(order.amazon_cost) + to_float(order.promotion)
        order.total_cost = (order.supply_cost + order.shipment_cost) * order.Quantity + subscribe_fee
        order.profit = order.amount + order.total_cost
        order.save()
        return order.cost

    def _calc_with_refunds(self, product):
        """
        计算退货的收入支出
        :param product:
        """
        refunds = RefundItem.objects.filter(product=product, settlement=self.settlement)
        for refund in refunds:
            if refund.order_item:
                refund.cost = -refund.order_item.cost
            else:
                refund.cost = product.cost
                self.unfound_refund_quantity += 1
            refund.total_cost = refund.cost * refund.quantity
            refund.income = to_float(refund.PriceAdjustmentAmount)
            refund.promotion = to_float(refund.PromotionPrincipal) + to_float(refund.PromotionShipping)
            refund.amazon_cost = to_float(refund.Commission) + to_float(refund.RefundCommission)
            refund.amount = refund.income + refund.promotion + refund.amazon_cost
            refund.profit = refund.total_cost + refund.amount
            refund.save()

        # 计算汇总信息并记录
        total_item, created = RefundItem.objects.get_or_create(settlement=self.settlement, product=product, is_total=True)
        query_set = RefundItem.objects.filter(settlement=self.settlement, product=product, product__isnull=False)
        total_item.quantity = sum_queryset(query_set, 'quantity')
        total_item.promotion = sum_queryset(query_set, 'promotion')
        total_item.income = sum_queryset(query_set, 'income')
        total_item.amount = sum_queryset(query_set, 'amount')
        total_item.total_cost = sum_queryset(query_set, 'total_cost')
        total_item.profit = sum_queryset(query_set, 'profit')
        total_item.save()

    def _calc_removals(self, product):
        """
        计算弃置/移除的商品，相当于销售出去
        """
        items = ProductRemovalItem.objects.select_related('product').filter(settlement=self.settlement, product=product)
        for item in items:
            item.cost = -product.cost
            item.amazon_cost = to_float(item.Fee)
            item.amount = item.amazon_cost
            item.total_cost = product.cost * item.Quantity
            item.profit = item.total_cost + item.amount
            item.save()
            self.sale_quantity += item.Quantity

        # 计算汇总信息并记录
        total_item, created = ProductRemovalItem.objects.get_or_create(settlement=self.settlement, product=product, is_total=True)
        query_set = ProductRemovalItem.objects.filter(settlement=self.settlement, product=product, is_total=False)
        total_item.Quantity = sum_queryset(query_set, 'Quantity')
        total_item.amazon_cost = sum_queryset(query_set, 'amazon_cost')
        total_item.amount = sum_queryset(query_set, 'amount')
        total_item.total_cost = sum_queryset(query_set, 'total_cost')
        total_item.profit = sum_queryset(query_set, 'profit')
        total_item.save()

    def _calc_lost(self, product):
        """
        计算丢失赔偿的订单，相当于销售出去
        :param product:
        :return: 总成本
        """
        items = OtherTransactionItem.objects.filter(settlement=self.settlement, product=product)
        for item in items:
            if item.TransactionType == 'INCORRECT_FEES_ITEMS':  # 费用更正无需处理商品成本
                item.cost = 0
            else:
                item.cost = product.cost
                self.sale_quantity += item.Quantity
            item.total_cost = item.Quantity * item.cost
            item.profit = item.total_cost + item.Amount
            item.save()

        # 计算汇总信息并记录
        total_item, created = OtherTransactionItem.objects.get_or_create(settlement=self.settlement, product=product, is_total=True)
        query_set = OtherTransactionItem.objects.filter(settlement=self.settlement, product=product, is_total=False)
        total_item.Quantity = sum_queryset(query_set, 'Quantity')
        total_item.total_cost = sum_queryset(query_set, 'total_cost')
        total_item.Amount = sum_queryset(query_set, 'Amount')
        total_item.profit = sum_queryset(query_set, 'profit')
        total_item.save()

    def _update_inventory(self, product, count):
        """
        更新国内、亚马逊库存
        :param product:
        :param count: 如果为正数，表示销售的商品数，如果为负数，表示退货的数量
        """
        class_list = [InboundShipment, OutboundShipmentItem]
        order_list = ['ship_date', 'shipment__ship_date']
        quantity_key = ['count', 'QuantityShipped']
        if count == 0:
            return
        if count > 0:
            for i in [0, 1]:
                items = class_list[i].objects.filter(product=product, inventory__gt=0).order_by(order_list[i])
                tmp_count = count
                for supply in items:
                    if supply.inventory > tmp_count:
                        supply.inventory -= tmp_count
                        supply.save()
                        break
                    tmp_count -= supply.inventory
                    supply.inventory = 0
                    supply.save()
        else:
            count = -count
            for i in [0, 1]:
                items = class_list[i].objects.filter(product=product, inventory__lt=F(quantity_key[i])).order_by('-'+order_list[i])
                tmp = count
                for item in items:
                    if tmp <= getattr(item, quantity_key[i]) - item.inventory:
                        item.inventory += tmp
                        item.save()
                        break
                    tmp -= getattr(item, quantity_key[i]) - item.inventory
                    item.inventory = item.count
                    item.save()

    def _calc_advertising(self, product):
        # 统计广告费
        total = to_float(AdvertisingProductItems.objects.filter(product=product).aggregate(total=Sum('TotalSpend')).get('total'))
        return to_float(total)


class SettlementCalc(object):
    """
    结算利润计算
    """

    def __init__(self, settlement):
        self.settlement = settlement
        self.product_calc = ProductProfitCalc(settlement)

    def calc_settlement(self):
        """
        计算结算周期内所有商品的总收入、总成本、总利润
        :return:
        """
        settlement = self.settlement
        query_set = ProductSettlement.objects.filter(settlement=settlement)
        settlement.total_cost = sum_queryset(query_set, 'total_cost')
        settlement.income = sum_queryset(query_set, 'income')
        settlement.amazon_cost = sum_queryset(query_set, 'amazon_cost')
        settlement.promotion = sum_queryset(query_set, 'promotion')
        settlement.amount = sum_queryset(query_set, 'amount')
        settlement.quantity = sum_queryset(query_set, 'quantity')

        settlement.subscription_fee_adjust =sum_queryset(OtherTransaction.objects.filter(TransactionType='NonSubscriptionFeeAdj'), 'Amount')
        settlement.balanced_adjust = sum_queryset(OtherTransaction.objects.filter(TransactionType='BalanceAdjustment'), 'Amount')

        if settlement.advertising_fee is None:
            settlement.advertising_fee = sum_queryset(query_set, 'advertising_fee')
        settlement.advertising_fee_adjust = sum_queryset(query_set, 'advertising_fee')
        settlement.total_cost += settlement.advertising_fee
        settlement.profit = settlement.amount + settlement.total_cost
        settlement.profit_rate = settlement.profit / settlement.income if settlement.income else 0
        settlement.save()
        return settlement

    def _handle_returns(self, product):
        """
        处理退货
        :param product:
        """
        # 计算顾客退货且可销售的商品数量
        values = ProductReturn.objects.filter(product=product, settlement=self.settlement, type='CustomerReturns',
                                              disposition='SELLABLE').values_list('quantity', flat=True)
        total = sum(list(values))
        product.custom_return_quantity = total
        # 计算顾客退货且损坏的商品数量
        values = ProductReturn.objects.filter(product=product, settlement=self.settlement, type='CustomerReturns',
                                              disposition='CUSTOMER_DAMAGED').values_list('quantity', flat=True)
        total = sum(list(values))
        product.custom_damage_quantity = total
        # 计算顾客退货且可销售的商品数量
        values = ProductReturn.objects.filter(product=product, settlement=self.settlement, type='Adjustments')\
            .values_list('quantity', flat=True)
        total = sum(list(values))
        product.return_quantity = total
        # # 将退货数量补充到国内库存、国外库存
        # self._update_inventory(product, total)


##################  退货 ####################
def update_returns_to_db(settlement, item):
    product, created = Product.objects.get_or_create(MarketplaceId=settlement.MarketplaceId, SellerSKU=item['SellerSKU'])
    ProductReturn.objects.create(settlement=settlement, product=product, **item)


##################  文件导入 ####################
class FileImporter(object):

    @classmethod
    def import_removals(cls, text, settlement=None):
        """
        导入移除报告并保存到数据库
        :param text:
        """
        from amazon_services.text_parser import ProductRemovalParser
        from amazon_services.exception import TextParseException
        parser = ProductRemovalParser(text)
        items = parser.get_items()
        removals = RemovalDbHandler().update_to_db(settlement=settlement, data=items)
        return removals
#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import os, datetime, urllib, json, logging
from django.conf import settings
from django.db.models import Q, F
from amazon_services.service import OrderService, OrderItemService
from models import *


logger = logging.getLogger('product')


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
        settlement, created = Settlement.objects.get_or_create(MarketplaceId=self.MarketplaceId, AmazonSettlementID=data['AmazonSettlementID'])
        if created:
            for key, value in data.items():
                setattr(settlement, key, value)
            settlement.save()
        return settlement

    def update_order_to_db(self, settlement, data):
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
        # s实收金额
        data['Amount'] = float(data.get('Principal')) + float(data.get('Shipping', 0)) + float(data.get('FBAPerUnitFulfillmentFee', 0)) + \
                          float(data.get('ShippingChargeback', 0)) + float(data.get('Commission', 0)) + float(data.get('PromotionShipping', 0))
        return SettleOrderItem.objects.create(**data)

    def update_refund_to_db(self, settlement, data):
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
        product, created = Product.objects.get_or_create(SellerSKU=data['SellerSKU'],
                                                         MarketplaceId=self.MarketplaceId)
        data['product'] = product
        data['SellerSKU'] = product.SellerSKU
        return RefundItem.objects.create(**data)

    def update_transaction_to_db(self, settlement, data):
        if not data:
            return None
        try:
            obj = OtherTransaction.objects.get(settlement=settlement, TransactionID=data['TransactionID'])
            print 'OtherTransaction exist:　%s' % json.dumps(data)
            return obj
        except OtherTransaction.DoesNotExist, ex:
            pass
        data['MarketplaceId'] = self.MarketplaceId
        data['settlement'] = settlement
        return OtherTransaction.objects.create(**data)

    def update_deal_payment_to_db(self, settlement, data):
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

    def update_advertising_transaction_to_db(self, settlement, data):
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
        product.domestic_cost = cost1
        product.oversea_cost = cost2
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
            if not supply.unit_cost:
                # 如果单位成本为空，则计算单位成本
                supply.unit_cost = supply.unit_price + (supply.total_freight+supply.charges) / supply.count
                supply.save()
            quantity += supply.inventory
            amount += supply.inventory * supply.unit_cost
        return amount/quantity if quantity else 0

    def _calc_shipment_cost(self, product):
        """
        计算当前移库单位成本
        """
        shipments = OutboundShipmentItem.objects.filter(product=product, inventory__gt=0)
        quantity = 0
        amount = 0
        for s in shipments:
            quantity += s.inventory
            amount += quantity * s.unit_freight
        return amount/quantity if quantity else 0


#################  Settlement ####################
class SettlementCalc(object):
    """
    结算利润计算
    """

    def __init__(self, settlement):
        self.settlement = settlement

    def calc_settlement(self):
        """
        计算结算周期内所有商品的总收入、总成本、总利润
        :return:
        """
        items = ProductSettlement.objects.filter(settlement=self.settlement)
        amount = sum([item.sales_amount for item in items])
        cost = sum([item.total_cost for item in items])
        self.settlement.sales_amount = amount
        self.settlement.total_cost = cost
        self.settlement.profit = amount - cost
        self.settlement.profit_rate = self.settlement.profit / amount if amount else 0
        self.settlement.save()

    def calc_product_profit(self, product):
        # 首先更新商品当前单位成本
        CostCalculate.calc_current_cost(product)
        q1, a1, c1 = self._calc_with_orders(product)
        q2, a2, c2 = self._calc_with_refunds(product)
        # 更新库存
        self._update_inventory(product, q1-q2)
        ps, created = ProductSettlement.objects.get_or_create(settlement=self.settlement, product=product)
        ps.quantity = q1
        ps.sales_amount = a1 + a2
        ps.total_cost = c1 + c2 + ps.advertising_fee + ps.storage_fee
        ps.profit = ps.sales_amount - ps.total_cost
        ps.profit_rate = ps.profit / ps.sales_amount if ps.sales_amount else 0
        ps.save()

    def _clear(self, product):
        """
        清除计算的结果
        :return:
        """
        try:
            ps = ProductSettlement.objects.get(settlement=self.settlement, product=product)
            self._update_inventory(product, ps.quantity)        # 先将库存补充上
        except ProductSettlement.DoesNotExist, ex:
            return

    def _calc_with_orders(self, product):
        """
        计算订单的收入支出
        :param product:
        :return: 数量、实收、成本
        """
        orders = SettleOrderItem.objects.filter(product=product, settlement=self.settlement)
        if not orders:
            return 0, 0, 0
        quantity = 0
        cost_amount = 0     # 总成本
        principal_amount = 0
        for order in orders:
            cost_amount += self._calc_order_cost(product, order)
            principal_amount += order.Amount
            quantity += order.Quantity
        return quantity, principal_amount, cost_amount

    def _calc_with_refunds(self, product):
        """
        计算退货的收入支出
        :param product:
        """
        refunds = RefundItem.objects.filter(product=product, settlement=self.settlement)
        quantity = 0
        amount = 0
        cost = 0
        for refund in refunds:
            try:
                order = SettleOrderItem.objects.get(OrderItemId=refund.OrderItemId)
            except SettleOrderItem.DoesNotExist, ex:
                logger.warning('cannot find refund order: %s', refund.OrderItemId)
                order = None
            refund.amount = order.Principal + order.Shipping + order.Commission + order.RefundCommission + \
                           order.PromotionPrincipal + order.PromotionShipping + order.ShippingChargeback + order.RestockingFee
            refund.cost = order.cost if order else 0
            refund.quantity = order.Quantity if order else 1
            refund.save()
            quantity += refund.quantity
            amount = refund.amount
            cost = refund.cost
        return quantity, amount, cost

    def _handle_returns(self, product):
        """
        处理退货
        :param product:
        """
        values = ProductReturn.objects.filter(product=product, settlement=self.settlement).values_list('quantity', flat=True)
        total = sum(list(values))
        if not total:
            return
        # 将退货数量补充到国内库存、国外库存
        self._update_inventory(product, total)

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
            for i in [0, 1]:
                items = class_list[i].objects.filter(product=product, inventory__lt=F(quantity_key[i])).order_by('-'+order_list[i])
                tmp = count
                for item in items:
                    if tmp < getattr(item, quantity_key[i]) - item.inventory:
                        item.inventory += tmp
                        item.save()
                        break
                    tmp -= getattr(item, quantity_key[i]) - item.inventory
                    item.inventory = item.count
                    item.save()

    def _calc_order_cost(self, product, order):
        """
        计算每个订单的成本
        :return:
        """
        if not order.Principal:
            logger.info('order %s principal is None or 0', order.AmazonOrderId)
            return
        order.inbound_fee = product.domestic_cost * order.Quantity
        order.outbound_fee = product.oversea_cost * order.Quantity
        order.cost = (order.subscription_fee + order.inbound_fee + order.outbound_fee) * order.Quantity
        order.save()
        return order.cost


##################  退货 ####################
def update_returns_to_db(settlement, item):
    product, created = Product.objects.get_or_create(MarketplaceId=settlement.MarketplaceId, SellerSKU=item['SellerSKU'])
    ProductReturn.objects.create(settlement=settlement, product=product, **item)
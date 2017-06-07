#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import os, datetime, urllib, json
from django.conf import settings
from django.db.models import Q
from amazon_services.service import OrderService, OrderItemService
from models import *


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


##################  Settlement ####################
# def update_order_income(order, data, created=False):
#     """
#     计算订单销售情况
#     :param order: 数据库订单
#     :param data:  最新的订单数据
#     :param created: order是否最新创建
#     """
#     current_status = order.OrderStatus
#     new_status = data['OrderStatus']
#     if not created and current_status == new_status:    # 状态未更新
#         return
#     if new_status == OrderStatus.Pending:   # 等待付款状态不计入销售
#         return
#     if current_status == OrderStatus.Pending and new_status == OrderStatus.Canceled:
#         return
#     if created or (current_status == OrderStatus.Pending and new_status !=)

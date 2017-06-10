#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import datetime
from amazon_services.service import *
from amazon_services.models import MarketAccount
from api import *


DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def update_orders(market, last_update_time):
    """
    从亚马逊获取数据并更新订单信息
    :param market:
    :param last_update_time: datetime格式
    :return:
    """
    time_str = last_update_time.strftime(DT_FORMAT)
    orders = OrderService(market).get_orders(time_str)
    order_item_service = OrderItemService(market)
    for order in orders:
        # 读取OrderItem信息
        items = order_item_service.list_items(order['AmazonOrderId'])
        # 更新到数据库
        update_order_to_db(order, items)


def update_product(market=None):
    """
    完善商品信息
    :param market:
    """
    market_id = market.MarketplaceId if market else 'ATVPDKIKX0DER'
    products = Product.objects.filter(MarketplaceId=market_id, ASIN__isnull=True)
    # 5个一组
    length = 5
    for group in [products[i:i+length] for i in xrange(0, len(products), length)]:
        sku_list = [p.SellerSKU for p in group]
        products = ProductService(market).get_products(sku_list)
        for product in products:
            update_product_to_db(product)


def update_settlement(market=None):
    """
    同步结算结果
    :param market:
    """
    service = SettlementReportService(market)
    reports = service.get_list()
    if not reports:
        print 'Settlement Report is None'
        return
    if not market:
        market = MarketAccount()
        market.MarketplaceId = Marketplace_EN
    for report in reports:
        handler = SettlementDbHandler(market)
        settlement_data = service.get_one(report['ReportId'])
        settlement = handler.update_settlement_to_db(settlement_data['SettlementData'])
        if 'Order' in settlement_data:
            for item in settlement_data['Order']:
                handler.update_order_to_db(settlement, item)
        if 'Refund' in settlement_data:
            for item in settlement_data['Refund']:
                handler.update_refund_to_db(settlement, item)
        if 'OtherTransactions' in settlement_data:
            for item in settlement_data['OtherTransactions']:
                handler.update_transaction_to_db(settlement, item)
        if 'SellerDealPayment' in settlement_data:
            for item in settlement_data['SellerDealPayment']:
                handler.update_deal_payment_to_db(settlement, item)
        if 'AdvertisingTransactionDetails' in settlement_data:
            for item in settlement_data['AdvertisingTransactionDetails']:
                handler.update_advertising_transaction_to_db(settlement, item)


def update_inventories(settlement):
    """
    同步退货信息
    :param market:
    """
    for settlement in Settlement.objects.filter(returns__isnull=True):
        service = InventorySummaryService()
        request_report_id = service.request_report(settlement.StartDate, settlement.EndDate)
        print 'update_inventories: request report id: %s' % request_report_id
        time.sleep(60)
        inventories = service.get_by_request_id(request_report_id)
        # inventories = service.get_by_report_id('5396817722017327')
        if inventories:
            for one in inventories:
                if one['type'] == 'CustomerReturns':
                    update_returns_to_db(settlement, one)


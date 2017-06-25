#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import datetime, logging, json
import dateutil.parser
from amazon_services.service import *
from amazon_services.models import MarketAccount
from api import *


logger = logging.getLogger('product')


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
    last_settle_end_date = None
    if Settlement.objects.filter(MarketplaceId=market.MarketplaceId).exists():
        latest = Settlement.objects.filter(MarketplaceId=market.MarketplaceId).order_by('-EndDate').last()
        last_settle_end_date = latest.EndDate.strftime('%Y-%m-%d %H:%M:%S')
    # 如果settlement为空，取最近一次结算周期的数据。如果不为空，则取上一次到现在的所有settlements

    for report in reports:
        settlement_data = service.get_one(report['ReportId'])
        start_date = dateutil.parser.parse(settlement_data['SettlementData']['StartDate']).replace(tzinfo=None)
        end_date = dateutil.parser.parse(settlement_data['SettlementData']['EndDate']).replace(tzinfo=None)
        # 如果EndDate与StartDate不是相差14天，则不计算
        if (end_date - start_date).days != 14:
            continue
        try:
            SettlementDataRecord.objects.get(data_type=SettlementDataRecord.SETTLEMENT, start_time=settlement_data['SettlementData']['StartDate'])
            continue
        except SettlementDataRecord.DoesNotExist, ex:
            pass
        handler = SettlementDbHandler(market)
        settlement = handler.update_settlement_to_db(settlement_data)
        SettlementDataRecord.objects.create(data_type=SettlementDataRecord.SETTLEMENT, start_time=settlement.StartDate,
                                         end_time=settlement.EndDate, settlement=settlement)
        if not last_settle_end_date or settlement_data['SettlementData']['StartDate'] == last_settle_end_date:
            break


# def update_inventories(market, settlement):
#     """
#     同步退货信息
#     :param market:
#     """
#     if settlement.returns.exists():
#         logger.info('product returns of settlement exists: %s-%s', settlement.StartDate, settlement.EndDate)
#         return
#     logger.info('start update product returns of settlement: %s-%s', settlement.StartDate, settlement.EndDate)
#     service = InventorySummaryService(market)
#     request_report_id = service.request_report(settlement.StartDate, settlement.EndDate)
#     logger.info('update_inventories: request report id: %s', request_report_id)
#     time.sleep(60)
#     inventories = service.get_by_request_id(request_report_id)
#     # inventories = service.get_by_report_id('5396817722017327')
#     if inventories:
#         for one in inventories:
#             if one['type'] in ['CustomerReturns', 'Adjustments']:
#                 update_returns_to_db(settlement, one)


def update_removal_report(market, settlement):
    # 更新移除报告
    service = ProductRemovalReportService(market)
    try:
        SettlementDataRecord.objects.get(settlement=settlement, start_time=settlement.StartDate,
                                            end_time=settlement.EndDate, data_type=SettlementDataRecord.REMOVAL)
    except SettlementDataRecord.DoesNotExist, ex:
        items = service.get_list(settlement.StartDate, settlement.EndDate)
        if items:
            RemovalDbHandler().update_to_db(settlement, items)
            SettlementDataRecord.objects.create(settlement=settlement, start_time=settlement.StartDate,
                                                end_time=settlement.EndDate, data_type=SettlementDataRecord.REMOVAL)


def update_advertising_report(market, settlement):
    service = AdvertiseReportService(market)
    start = settlement.StartDate.replace(hour=0, minute=0, second=0)
    end = settlement.EndDate.replace(hour=0, minute=0, second=0)
    SUNDAY = 6
    tmp_start = start
    while tmp_start < end:
        if tmp_start.weekday() != SUNDAY or (end-tmp_start).days < 7:
            # 增加一个日请求
            # 数据库中是否已更新了相关数据
            try:
                SettlementDataRecord.objects.get(settlement=settlement, start_time=tmp_start,
                                                 end_time=tmp_start+datetime.timedelta(days=1), data_type=SettlementDataRecord.ADVERTISE)
            except SettlementDataRecord.DoesNotExist, ex:
                items = service.get_by_day(tmp_start)
                if items:
                    update_product_advertising_to_db(settlement, items)
                    SettlementDataRecord.objects.create(settlement=settlement, start_time=tmp_start,
                                                     end_time=tmp_start+datetime.timedelta(days=1), data_type=SettlementDataRecord.ADVERTISE)
            logger.info('settlement: %s, get advertising dally at : %s', settlement.StartDate, tmp_start)
            tmp_start = tmp_start + datetime.timedelta(days=1)
        else:
            # 增加一个周请求
            # 数据库中是否已更新了相关数据
            try:
                SettlementDataRecord.objects.get(settlement=settlement, start_time=tmp_start,
                                                 end_time=tmp_start+datetime.timedelta(days=7), data_type=SettlementDataRecord.ADVERTISE)
            except SettlementDataRecord.DoesNotExist, ex:
                items = service.get_by_week(tmp_start)
                if items:
                    update_product_advertising_to_db(settlement, items)
                    SettlementDataRecord.objects.create(settlement=settlement, start_time=tmp_start,
                                                     end_time=tmp_start+datetime.timedelta(days=7), data_type=SettlementDataRecord.ADVERTISE)
            logger.info('settlement: %s, get advertising weekly at : %s', settlement.StartDate, tmp_start)
            tmp_start = tmp_start + datetime.timedelta(days=7)


def update_all(market):
    # 总的更新入口
    if market.is_getting_report:
        return
    market.is_getting_report = True
    market.save()
    time.sleep(100)
    # try:
    #     update_settlement(market)
    #
    #     settlements = Settlement.objects.filter(returns__isnull=True)
    #     if settlements.exists():
    #         for settlement in settlements:
    #             update_advertising_report(market, settlement)
    #             # update_removal_report(market, settlement)
    #     update_product(market)
    # except BaseException, ex:
    #     logger.error(traceback.format_exc())
    market.is_getting_report = False
    market.save()
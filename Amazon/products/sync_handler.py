#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import datetime, logging, json
import dateutil.parser
from amazon_services.service import *
from amazon_services.models import MarketAccount
from api import *


logger = logging.getLogger('product')


DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


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
        if (end_date - start_date).days != 14 or start_date < market.period_start:
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
    data_valid = True   # 表示广告费读取时是否出错
    all_request_id = dict()     # 所有请求id
    dally_report_type = '_GET_PADS_PRODUCT_PERFORMANCE_OVER_TIME_DAILY_DATA_TSV_'
    weekly_report_type = '_GET_PADS_PRODUCT_PERFORMANCE_OVER_TIME_WEEKLY_DATA_TSV_'
    while tmp_start < end:
        if tmp_start.weekday() != SUNDAY or (end-tmp_start).days < 7:
            # 增加一个日请求
            # 数据库中是否已更新了相关数据
            try:
                SettlementDataRecord.objects.get(settlement=settlement, start_time=tmp_start,
                                                 end_time=tmp_start+datetime.timedelta(days=1), data_type=SettlementDataRecord.ADVERTISE)
            except SettlementDataRecord.DoesNotExist, ex:
                # 判断是否请求过
                try:
                    record = ReportRequestRecord.objects.get(report_type=dally_report_type, start_time=tmp_start)
                    all_request_id[record.request_report_id] = record.start_time
                except ReportRequestRecord.DoesNotExist, ex:
                    request_id = service.request_by_day(tmp_start)
                    all_request_id[request_id] = tmp_start
                    ReportRequestRecord.objects.get_or_create(report_type=dally_report_type, start_time=tmp_start,
                                                              request_report_id=request_id)
            tmp_start = tmp_start + datetime.timedelta(days=1)
        else:
            # 增加一个周请求
            # 数据库中是否已更新了相关数据
            try:
                SettlementDataRecord.objects.get(settlement=settlement, start_time=tmp_start,
                                                 end_time=tmp_start+datetime.timedelta(days=7), data_type=SettlementDataRecord.ADVERTISE)
            except SettlementDataRecord.DoesNotExist, ex:
                # 判断是否请求过
                try:
                    record = ReportRequestRecord.objects.get(report_type=weekly_report_type, start_time=tmp_start)
                    items = service.get_by_week(tmp_start, record.request_report_id)
                except ReportRequestRecord.DoesNotExist, ex:
                    items = service.get_by_week(tmp_start)
                if items is not None:
                    update_product_advertising_to_db(settlement, items)
                    SettlementDataRecord.objects.create(settlement=settlement, start_time=tmp_start,
                                                     end_time=tmp_start+datetime.timedelta(days=7), data_type=SettlementDataRecord.ADVERTISE)
                    logger.info('get weekly advertising success, start date:', tmp_start)
                else:
                    logger.info('get weekly advertising fail, start date:', tmp_start)
                    data_valid = False
            tmp_start = tmp_start + datetime.timedelta(days=7)
    if not len(all_request_id.keys()):
        return
    # 获取report_id
    max_try = 3
    try_time = 0
    while try_time < max_try and len(all_request_id.keys()):
        reports = service.list_report(dally_report_type)        # 获取所有报告
        request_id_list = all_request_id.keys()
        for report in reports:
            request_id = report['ReportRequestId']
            if request_id in request_id_list:
                report_id = report['ReportId']
                record = ReportRequestRecord.objects.get(request_report_id=request_id)
                record.report_id = report_id
                record.save()
                items = service.get_items_by_report_id(report_id)
                if items is not None:
                    update_product_advertising_to_db(settlement, items)
                    SettlementDataRecord.objects.get_or_create(settlement=settlement, start_time=all_request_id[request_id],
                                                             end_time=all_request_id[request_id]+datetime.timedelta(days=1),
                                                             data_type=SettlementDataRecord.ADVERTISE)
                    logger.info('get dally advertising success, start date:', tmp_start)
                    del all_request_id[request_id]
                else:
                    logger.info('get dally advertising fail, start date:', tmp_start)
                    data_valid = False
            if not len(all_request_id.keys()):
                break
        time.sleep(180)     # 等待3分钟
        try_time += 1
    if try_time >= max_try:
        logger.warning('try %d times, sync advertising report fail', max_try)
    if data_valid or try_time < max_try:
        settlement.advertising_report_valid = True
        advertising_fee = sum_queryset(ProductSettlement.objects.filter(settlement=settlement, is_total=False,
                                                                        product__isnull=False), 'advertising_fee')
        settlement.advertising_fee = advertising_fee
        settlement.save()


def update_all(market):
    # 总的更新入口
    if market.is_getting_report:
        return
    market.is_getting_report = True
    market.save()
    try:
        update_settlement(market)

        settlements = Settlement.objects.filter(advertising_report_valid=False)
        for settlement in settlements:
            update_advertising_report(market, settlement)
                # update_removal_report(market, settlement)
        update_product(market)
    except BaseException, ex:
        logger.error(traceback.format_exc())
    market.is_getting_report = False
    market.save()
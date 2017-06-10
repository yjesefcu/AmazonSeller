#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import requests, urllib, base64, hmac, hashlib, traceback, time, logging, threading, Queue
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import datetime
from xml_parser import *
from text_parser import *
# from models import RequestRecords
logger = logging.getLogger('amazon')
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


HOST = 'mws.amazonservices.com'
MWSAuthToken = '5560-3963-1886'
SellerId = 'ANL7YM4J4ZSFD'
AWSAccessKeyId = 'AKIAIJSW6PJWUZXQFLBQ'
SecretKey = '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'
Marketplace_EN = 'ATVPDKIKX0DER'

DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class OrderQueueHandle(threading.Thread):

    def __init__(self, target, args):
        super(OrderQueueHandle, self).__init__(target=target, args=args)
        self.queue = Queue.Queue

    def run(self):
        order = self.queue.get(block=True)
        while order:
            #
            order = self.queue.get(block=True)
        pass

    def add_order(self, order):
        """
        添加订单信息
        :param order: 从amazon查询回来的订单信息
        """
        self.queue.put(order)


class AmazonService(object):

    def __init__(self, market_account=None):
        self.market = market_account
        self.host = market_account.host if market_account else HOST
        self.SecretKey = market_account.SecretKey if market_account else SecretKey
        self.MarketplaceId = market_account.MarketplaceId if market_account else Marketplace_EN
        self.default = {
            'AWSAccessKeyId': market_account.AWSAccessKeyId if market_account else AWSAccessKeyId,
            'MWSAuthToken': market_account.MWSAuthToken if market_account else MWSAuthToken,
            'MarketplaceId.Id.1': self.MarketplaceId,
            'SellerId': market_account.SellerId if market_account else SellerId,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2'
        }
        self.last_post_time = None

    def post(self, uri, action, param=None, api_version='2013-09-01'):
        if not param:
            param = dict()
        parameters = {
            'Timestamp': datetime.datetime.utcnow().strftime(DT_FORMAT),
            'Version': api_version,     # API版本
            'Action': action,
        }   # 加上请求需要的参数
        parameters = dict(self.default.items() + parameters.items() + param.items())
        signature = self.create_signature(uri, parameters)
        parameters['Signature'] = signature
        form_data = '&'.join([key+'='+self._url_encode(value) for (key, value) in parameters.items()])
        url = 'https://%s%s?%s' % (self.host, uri, form_data)
        try:
            if not self._can_post():    # 如果当期已经超过限制，则等待相应的时间
                time.sleep(self._get_api_interval_time())
            r = requests.post(url, verify=False, headers={'Connection': 'close'})
            self.last_post_time = datetime.datetime.now()
            self._add_record(uri, action, form_data, r.text)
            return r
        except Exception, ex:
            traceback.format_exc()
            logger.warning('post exception: %s', traceback.format_exc())
        return None

    def _add_record(self, uri, action, param, response_text):
        if not self.market:     #  如果market为空，说明是调试信息，则不保存
            return
        errors = None
        # try:
        #     parser = BaseParser(response_text)
        #     if parser.is_error_response():
        #         errors = ', '.join([i for i in parser.errors()])
        #         result = RequestRecords.FAIL
        #     else:
        #         result = RequestRecords.SUCCESS
        # except Exception, ex:
        #     traceback.format_exc()
        #     logger.warning('xml parser fail: %s', response_text)
        #     result = RequestRecords.PARSER_FAIL
        # try:
        #     RequestRecords.objects.create(market=self.market, uri=uri, action=action, param=param,
        #                                   create_time=datetime.datetime.now(), sent_time=datetime.datetime.now(),
        #                                   result=result, errors=errors)
        # except BaseException, ex:
        #     logger.warning('create RequestRecord failed: %s', traceback.format_exc())

    def create_signature(self, uri, params):
        """
        签名生成器
        :param method 请求方法,POST/GET
        :param action： 服务接口
        :param params:  请求所需参数
        """
        host = self.host
        query_items = params.items()
        query_items.sort()
        form_data = '&'.join([key + '=' + self._url_encode(value) for (key, value) in query_items])
        url = '%s\n%s\n%s\n%s' % ('POST', host, uri, form_data)
        message = bytes(url).encode('utf-8')
        secret = bytes(self.SecretKey).encode('utf-8')
        signature = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
        return signature

    def _can_post(self):
        """
        根据api限制，判断是否能够发起请求，不能的话等待相应的时间
        """
        if not self.last_post_time:
            return True
        if (datetime.datetime.now() - self.last_post_time).seconds > self._get_api_interval_time():
            return True
        return False

    def _get_api_interval_time(self):
        """
        获取api规定的间隔时间，单位s
        """
        return 0

    @classmethod
    def _url_encode(cls, s):
        return urllib.quote(s).replace('/', '%2F').replace('%7E', '~')


class OrderService(AmazonService):

    def __init__(self, market_account=None):
        super(OrderService, self).__init__(market_account)
        self.order_item_service = OrderItemService()

    def get_orders(self, last_update_time):
        """
        获取订单列表
        :param last_update_time: 字符串格式
        :return:
        """
        return self._get_next_token(last_update_time=last_update_time)

    def _get_next_token(self, last_update_time=None, next_token=None):
        if last_update_time:
            r = self.post('/Orders/2013-09-01', 'ListOrders',
                      {'LastUpdatedAfter': last_update_time})
        else:
            r = self.post('/Orders/2013-09-01', 'ListOrdersByNextToken', {'NextToken': next_token})
        try:
            parser = OrderParse(r.text)
        except Exception, ex:
            traceback.format_exc()
            print r.text
            return None
        orders = parser.get_items()
        if parser.get_next_token():
            next_orders = self._get_next_token(next_token=parser.get_next_token())
            if next_orders:
                orders.extend(next_orders)
        return orders

    def _get_api_interval_time(self):
        return 60


class OrderItemService(AmazonService):

    def list_items(self, amazon_order_id):
        return self._get_next_token(amazon_order_id=amazon_order_id)

    def _get_next_token(self, amazon_order_id=None, next_token=None):
        if amazon_order_id:
            r = self.post('/Orders/2013-09-01', 'ListOrderItems',
                      {'AmazonOrderId': amazon_order_id})
        else:
            r = self.post('/Orders/2013-09-01', 'ListOrderItemsByNextToken', {'NextToken': next_token})
        if not r:
            logger.error('GetMatchingProductForId except. ')
            return None
        try:
            parser = OrderItemParser(r.text)
        except Exception, ex:
            traceback.format_exc()
            logger.warning('OrderItemService parse failed: %s', r.text)
            return None
        items = parser.get_items()
        if parser.get_next_token():
            next_items = self._get_next_token(next_token=parser.get_next_token())
            if next_items:
                items.extend(next_items)
        return items

    def _get_api_interval_time(self):
        return 1


class ProductService(AmazonService):

    def get_products(self, sku_list):
        """
        获取商品信息列表
        :param asin_list: SellerSKU列表，不超过5个
        """
        if len(sku_list) > 5:
            return
        param = {'IdType': 'SellerSKU', 'MarketplaceId': self.MarketplaceId}
        i = 1
        for id in sku_list:
            key = 'IdList.Id.%d' % i
            param[key] = id
            i += 1
        r = self.post('/Products/2011-10-01', 'GetMatchingProductForId',
                      param, api_version='2011-10-01')
        if not r:
            logger.error('GetMatchingProductForId except. ')
        try:
            parser = ProductParser(r.text)
        except Exception, ex:
            traceback.format_exc()
            logger.warning('GetMatchingProductForId parse failed: %s', r.text)
            return None
        items = parser.get_items()
        return items

    def _get_api_interval_time(self):
        return 1


class SettlementReportService(AmazonService):
    """
    结算报告
    """

    def get_list(self):
        """
        获取结算报告列表
        """
        r = self.post('/', 'GetReportList', {
            'ReportTypeList.Type.1': '_GET_V2_SETTLEMENT_REPORT_DATA_XML_'
        }, api_version='2009-01-01')

        try:
            parser = ReportListParser(r.text)
        except Exception, ex:
            traceback.format_exc()
            logger.warning('SettlementReport parse failed: %s', r.text)
            return None
        # 不获取NextToken的值
        items = parser.get_items()
        return items

    def get_one(self, report_id):
        """
        根据ReportId获取单个报告的xml信息
        :param report_id:
        """
        r = self.post('/', 'GetReport', {
            'ReportId': report_id
        }, api_version='2009-01-01')

        try:
            parser = SettlementReportParser(r.text)
        except Exception, ex:
            traceback.format_exc()
            logger.warning('SettlementReport parse failed: %s', r.text)
            return None
        # 不获取NextToken的值
        items = parser.get_items()
        return items

    def _get_api_interval_time(self):
        return 30


class InventorySummaryService(AmazonService):

    def request_report(self, start_time, end_time):
        """
        请求报告
        :return:
        """
        r = self.post('/', 'RequestReport', {
            'ReportType': '_GET_FBA_FULFILLMENT_INVENTORY_SUMMARY_DATA_',
            'StartDate': start_time.strftime(DT_FORMAT),
            'EndDate': end_time.strftime(DT_FORMAT)
        }, api_version='2009-01-01')
        return RequestReportParser(r.text).get_report_id()

    def get_by_request_id(self, request_report_id):
        # 如果十分钟内还没恢复，则不再请求
        count = 0
        report_id = self._check_report_done(request_report_id)
        while not report_id and count < 10:
            time.sleep(60)
            report_id = self._check_report_done(request_report_id)
        if count == 10:
            return None
        return self.get_by_report_id(report_id)

    def get_by_report_id(self, report_id):
        r = self.post('/', 'GetReport', {
            'ReportId': report_id
        }, api_version='2009-01-01')
        parser = InventorySummaryParser(r.text)
        return parser.get_items()

    def _check_report_done(self, report_id):
        r = self.post('/', 'GetReportList', {
            'ReportTypeList.Type.1': '_GET_FBA_FULFILLMENT_INVENTORY_SUMMARY_DATA_'
        }, api_version='2009-01-01')
        try:
            parser = ReportListParser(r.text)
        except Exception, ex:
            traceback.format_exc()
            logger.warning('SettlementReport parse failed: %s', r.text)
            return None
        # 不获取NextToken的值
        items = parser.get_items()
        # 如果report_id在reportList中存在，说明报告已经准备好了
        for report in items:
            if report['ReportRequestId'] == report_id:
                return report['RequestId']
        return False

    def get_one(self, report_id):
        """
        根据ReportId获取单个报告的xml信息
        :param report_id:
        """
        r = self.post('/', 'GetReport', {
            'ReportId': report_id
        }, api_version='2009-01-01')

        try:
            parser = SettlementReportParser(r.text)
        except Exception, ex:
            traceback.format_exc()
            logger.warning('SettlementReport parse failed: %s', r.text)
            return None
        # 不获取NextToken的值
        items = parser.get_items()
        return items

    def _get_api_interval_time(self):
        return 0

if __name__ == '__main__':
    # token = 'pXPDw7T+Fup/YYuZQbKv1QafEPREmauvizt1MIhPYZbaSgEpfAaYkXTkBHvJ93W/XVvMiz84ZXbNeGyEmOrLe7q8xqAchQNKtU38YwqRuVIwqcbUqh/LhCJ0wMvlylZkE3RvwDUQBA1G6ShfNgiExkSDtsD4aPvQcv0UYHXV8K5jpIXqERozsh35jNz11rwFKFx4/9h+5BG5ki8QZ/nAov0IfGeAvb95J/gMIjfO756fpVJGS+vu5pFHMXy6XL5lQW8Xd/Zkc1SuQyquFjSkBowoP8liP7H3sJdJobvDtjbZkLh8ZQWZdmTZrNwXH6VTGi/TbfXVDR7tObdzBnmaYnGsHLYYIfzBGxpr1p/cLrO96kATpJ2Ci+OjokijmI8Bbe7jhwcQGngpvkbRUhFumapDFyJ4Aaz0lmrLJ6gfmjoSyoYkkmy7z4+envNcHi41tHdkruHJ4Z15itQRr/9F9A=='
    # r = AmazonService().post('/Orders/2013-09-01', 'ListOrders', {'LastUpdatedAfter': '2017-05-01T00:00:00Z'})
    # r = AmazonService().post('/Orders/2013-09-01', 'ListOrdersByNextToken', {'NextToken': token})
    # r = AmazonService().post('/Orders/2013-09-01', 'ListOrdersByNextToken', {'NextToken': token})
    # print r.text
    # # r = AmazonService().post('/Products/2011-10-01', 'ListMatchingProducts',
    # #                          {'Query': 'MLA000153-SG', 'MarketplaceId': Marketplace_EN}, api_version='2011-10-01').text
    # print r.text
    # pass
    # print OrderService(None).get_orders('2017-05-01T00:00:00Z')
    # print OrderItemService(None).list_items('114-6870523-5093814')
    # print ProductService(None).get_products(['MLA000125', 'MLA000327'])
    # print SettlementReportService().get_items()
    start = datetime.datetime(year=2017, month=5, day=20)
    end = datetime.datetime(year=2017, month=6, day=10)
    report_id = InventorySummaryService().request_report(start, end)
    inventories = InventorySummaryService().get_inventory_list(report_id)

    # file_object = open('orders.txt')
    # try:
    #      all_the_text = file_object.read( )
    # finally:
    #      file_object.close( )
    # import json
    # orders = json.loads(all_the_text)
    # print 'order length: %d' % len(orders)
    # amazon_sell_id = [o['AmazonOrderId'] for o in orders]
    # print 'AmazonOrderId length: %d' % len(set(amazon_sell_id))
    # amazon_sell_id = [o['SellerOrderId'] for o in orders]
    # print 'SellerOrderId length: %d' % len(set(amazon_sell_id))
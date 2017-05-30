#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import requests, urllib, base64, hmac, hashlib, traceback, time, logging
import datetime
from django.conf import settings
from xml_parser import *
# from models import RequestRecords
logger = logging.getLogger('request')


HOST = 'mws.amazonservices.com'
MWSAuthToken = '5560-3963-1886'
SellerId = 'ANL7YM4J4ZSFD'
AWSAccessKeyId = 'AKIAIJSW6PJWUZXQFLBQ'
SecretKey = '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'
Marketplace_EN = 'ATVPDKIKX0DER'

DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class AmazonService():

    def __init__(self, market_account=None):
        self.market = market_account
        self.host = market_account.host if market_account else HOST
        self.SecretKey = market_account.SecretKey if market_account else SecretKey
        self.default = {
            'AWSAccessKeyId': market_account.AWSAccessKeyId if market_account else AWSAccessKeyId,
            'MWSAuthToken': market_account.MWSAuthToken if market_account else MWSAuthToken,
            'MarketplaceId.Id.1': market_account.MarketplaceId if market_account else Marketplace_EN,
            'SellerId': market_account.SellerId if market_account else SellerId,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2'
        }

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
            r = requests.post(url, verify=False)
            self._add_record(uri, action, form_data, r.text)
        except Exception, ex:
            traceback.format_exc()
            logger.warning('post exception: %s', traceback.format_exc())
        return r

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

    @classmethod
    def _url_encode(cls, s):
        return urllib.quote(s).replace('/', '%2F').replace('%7E', '~')


class OrderService(AmazonService):

    def get_orders(self, last_update_time):
        """
        获取订单列表
        :param last_update_time:
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
        orders = parser.get_items()
        if parser.get_next_token():
            time.sleep(60)   # 休眠1s
            next_orders = self._get_next_token(next_token=parser.get_next_token())
            if not next_orders:
                orders.extend(next_orders)
        return orders


class OrderItemService(AmazonService):

    def list_items(self, amazon_order_id):
        return self._get_next_token(amazon_order_id=amazon_order_id)

    def _get_next_token(self, amazon_order_id=None, next_token=None):
        if amazon_order_id:
            r = self.post('/Orders/2013-09-01', 'ListOrderItems',
                      {'AmazonOrderId': amazon_order_id})
        else:
            r = self.post('/Orders/2013-09-01', 'ListOrderItemsByNextToken', {'NextToken': next_token})
        try:
            parser = OrderItemParser(r.text)
        except Exception, ex:
            traceback.format_exc()
            logger.warning('OrderItemService parse failed: %s', r.text)
            return None
        items = parser.get_items()
        if parser.get_next_token():
            time.sleep(1)   # 休眠1s
            next_items = self._get_next_token(next_token=parser.get_next_token())
            if not next_items:
                items.extend(next_items)
        return items



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
    print OrderItemService(None).list_items('114-6870523-5093814')



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
#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import requests, urllib, base64, hmac, hashlib
import datetime
from django.conf import settings

HOST = 'mws.amazonservices.com'
MWSAuthToken = '5560-3963-1886'
SellerId = 'ANL7YM4J4ZSFD'
AWSAccessKeyId = 'AKIAIJSW6PJWUZXQFLBQ'
SecretKey = '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'
Marketplace_EN = 'ATVPDKIKX0DER'

DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class AmazonService():

    def post(self, uri, action, param=None, api_version='2013-09-01'):
        if not param:
            param = dict()
        parameters = {
            'AWSAccessKeyId': AWSAccessKeyId,
            'MWSAuthToken': MWSAuthToken,
            'MarketplaceId.Id.1': Marketplace_EN,
            'SellerId': SellerId,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2',
            'Timestamp': datetime.datetime.utcnow().strftime(DT_FORMAT),
            'Version': api_version,     # API版本
            'Action': action,
        }   # 加上请求需要的参数
        parameters = dict(parameters.items() + param.items())
        signature = self.create_signature(uri, parameters)
        parameters['Signature'] = signature
        form_data = '&'.join([key+'='+value for (key,value) in parameters.items()])
        url = 'https://%s%s?%s' % (HOST, uri, form_data)
        return requests.post(url, verify=False)

    def create_signature(self, uri, params):
        """
        签名生成器
        :param method 请求方法,POST/GET
        :param action： 服务接口
        :param params:  请求所需参数
        """
        host = HOST
        query_items = params.items()
        query_items.sort()
        form_data = '&'.join([key+'='+self._url_encode(value) for (key, value) in query_items])
        url = '%s\n%s\n%s\n%s' % ('POST', host, uri, form_data)
        message = bytes(url).encode('utf-8')
        secret = bytes(SecretKey).encode('utf-8')
        return self._url_encode(base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest()))

    @classmethod
    def _url_encode(cls, s):
        return urllib.quote(s).replace('/', '%2F').replace('%7E', '~')


if __name__ == '__main__':
    # for i in range(0, 30):
    #     print i
    # print AmazonService().post('/Orders/2013-09-01', 'ListOrders', {'CreatedAfter': '2017-05-01T12:00:00Z'})
    # r = AmazonService().post('/Products/2011-10-01', 'ListMatchingProducts',
    #                          {'Query': 'MLA000153-SG', 'MarketplaceId': Marketplace_EN}, api_version='2011-10-01').text
    # print r
    pass
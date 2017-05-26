#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import requests, urllib, base64, hmac, hashlib
import datetime
from django.conf import settings

HOST = 'mws.amazonservices.com'
AWSAccessKeyId = 'AKIAIJSW6PJWUZXQFLBQ'
MWSAuthToken = '5560-3963-1886'
SellerId = 'ANL7YM4J4ZSFD'
SecretKey = 'l8ML3TOApvsI9xsqO+xnXwa1bi2KWNNdTf0UHyYy'
Marketplace_EN = 'ATVPDKIKX0DER'

DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class Signature():

    @classmethod
    def get_signature(cls, method='POST', action='ListOrders', params=dict()):
        """
        签名生成器
        :param method 请求方法,POST/GET
        :param action： 服务接口
        :param params:  请求所需参数
        """
        query_string = cls._generate_url(params)
        print query_string
        return cls._encode(query_string)

    @classmethod
    def _encode(cls, query_string):
        message = bytes(query_string).encode('utf-8')
        secret = bytes(SecretKey).encode('utf-8')
        return base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())

    @classmethod
    def _url_encode(cls, s):
        return urllib.quote(s).replace('/', '%2F').replace('%7E', '~')

    @classmethod
    def _generate_url(cls, params=dict(), api_version='2013-09-01'):
        host = HOST
        request_uri = '/Orders/2013-09-01'
        parameters = {
            'AWSAccessKeyId': AWSAccessKeyId,
            'MWSAuthToken': MWSAuthToken,
            'MarketplaceId.Id.1': Marketplace_EN,
            'SellerId': SellerId,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2',
            'Timestamp': datetime.datetime.utcnow().strftime(DT_FORMAT),
            'Version': api_version,     # API版本
            'Action': 'ListOrders',
            'CreatedAfter': '2017-04-04T16:00:00Z'#(datetime.datetime.today()-datetime.timedelta(days=2)).utcnow().strftime(DT_FORMAT)
        }   # 加上请求需要的参数

        querys = parameters.items()
        querys.extend(params.items())
        querys.sort()
        query_string = '&'.join([key+'='+urllib.quote(value) for (key, value) in querys])
        print query_string
        url = '%s\n%s\n%s\n%s' % ('POST', host, request_uri, query_string)
        signature_string = cls._encode(url)
        print signature_string
        parameters['Signature'] = cls._url_encode(signature_string) # 3Qo/G/7xQ9XhZ3mfzMsFxhhMYRyh2Wb7s/X+KMgYDgE=
        # parameters['MarketplaceId.Id.1'] = urllib.quote(Marketplace_EN)
        print parameters
        query_string = '&'.join([key+'='+value for (key, value) in parameters.items()])
        print query_string
        r = requests.post('https://'+HOST+'/Orders/2013-09-01?'+query_string, verify=False)
        return r.text


if __name__ == '__main__':
    print datetime.datetime.utcnow().strftime(DT_FORMAT)
    user_agent = 'AppId/AppVersionId (Language=Python/2.7.3; Platform=Windows/Windows7)'
    print Signature._generate_url()
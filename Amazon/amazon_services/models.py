#-*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
HOST = 'mws.amazonservices.com'
MWSAuthToken = '5560-3963-1886'
SellerId = 'ANL7YM4J4ZSFD'
AWSAccessKeyId = 'AKIAIJSW6PJWUZXQFLBQ'
SecretKey = 'l8ML3TOApvsI9xsqO+xnXwa1bi2KWNNdTf0UHyYy'
Marketplace_EN = 'ATVPDKIKX0DER'


class Market(models.Model):
    """
    国家
    """
    id = models.CharField(max_length=10, primary_key=True)  # 市场编码，如en， ur
    cn = models.CharField(max_length=10)
    en = models.CharField(max_length=10)


class MarketAccount(models.Model):
    country = models.ForeignKey(Market)
    host = models.CharField(max_length=50)
    auth_token = models.CharField(max_length=15)
    access_key_id = models.CharField(max_length=25)
    secret_key = models.CharField(max_length=50)
    market_id = models.CharField(max_length=20)


class ApiCategory(models.Model):
    """
    API大类
    """
    desc = models.CharField(max_length=20)        # 类别描述
    uri = models.CharField(max_length=100)      #
    version = models.CharField(max_length=10)   # API版本


class ApiActions(models.Model):
    """
    API动作
    """
    category = models.ForeignKey(ApiCategory, related_name='actions')   # 所属类别
    desc = models.CharField(max_length=20)      # 该动作的描述
    name = models.CharField(max_length=50)   # 动作
    params = models.TextField(null=True, blank=True)    # 参数的json格式，key为参数名，
                                                        # value为参数类型：int/string/datetime等
    max_requests = models.IntegerField(null=True, blank=True)            # 最大请求限制，为空表示无限制
    recover_interval = models.IntegerField(null=True, blank=True)        # 请求恢复的时间间隔，以秒计算
    recover_count = models.IntegerField(null=True, blank=True)           # 每次恢复的请求个数
    request_remain = models.IntegerField(null=True, blank=True)          # 还剩下多少次请求
    last_request = models.DateTimeField(null=True, blank=True)           # 上一次请求的时间


class RequestRecords(models.Model):
    """
    请求记录
    """
    sender = models.ForeignKey(User)        # 请求发起人
    market = models.ForeignKey(MarketAccount)
    action = models.ForeignKey(ApiActions, related_name='records')
    uri = models.CharField(max_length=100)      # 请求的链接，即：action.uri
    action_name = models.CharField(max_length=50, null=True, blank=True)    # 动作，action.name
    params = models.TextField(null=True, blank=True)    # 参数，json格式
    create_time = models.DateTimeField()        # 请求创建的时间
    sent_time = models.DateTimeField(null=True, blank=True)   # 请求实际发送的时间
    result = models.IntegerField(default=0)     # 请求结果，0：未发送，1：成功，2：失败
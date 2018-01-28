#-*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from products.models import Product
# Create your models here.


class OrderStatus(models.Model):
    WaitForDepositPayed = 1     # 等待预付款付清
    WaitForProducing = 2        # 等待采购员填写生产完成信息
    WaitForPaying = 3           # 等待财务尾款打款
    WaitForTraffic = 4          # 等待采购员补充物流信息
    WaitForInbound = 5          # 等待仓库入库
    WaitForCheck = 6
    WaitForTrafficFeePayed = 7  # 等待物流费打款
    FINISH = 8                  # 完成
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    next_status = models.IntegerField(null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)       # 当处于这个状态时，可操作的角色是什么
    permissions = models.CharField(max_length=100, null=True, blank=True)  # 当处于这个状态时，需要的权限是什么


class Contract(models.Model):
    # 采购单合同
    contract_number = models.CharField(max_length=100)    # 合同号
    supplier = models.CharField(max_length=255)           # 供应商
    contact_person = models.CharField(max_length=50, null=True, blank=True)     # 联系人
    contact_phone = models.CharField(max_length=50, null=True, blank=True)
    traffic_comment = models.CharField(max_length=255, null=True, blank=True)   # 物流说明
    operator = models.CharField(max_length=100, null=True, blank=True)          # 经办人


class PurchasingOrder(models.Model):
    # 采购单中每个商品的详情
    # order = models.ForeignKey(PurchasingOrder, related_name='items')
    MarketplaceId = models.CharField(max_length=50)
    contract = models.ForeignKey(Contract)
    product = models.ForeignKey(Product, related_name='purchasing_orders')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')       # 如果parent不为空，说明是子采购单
    SellerSKU = models.CharField(max_length=50)
    name = models.CharField(max_length=255, null=True, blank=True)      # 商品名称
    creator = models.ForeignKey(User, null=True, blank=True)                   # 采购单创建人
    create_time = models.DateTimeField(null=True, blank=True)   # 采购单创建时间
    status = models.ForeignKey(OrderStatus)      # 采购单状态
    count = models.IntegerField(null=True, blank=True)      # 数量
    price = models.FloatField(null=True, blank=True)   # 采购单价
    total_price = models.FloatField(null=True, blank=True)  # 商品总价
    traffic_fee = models.FloatField(null=True, blank=True)  # 物流费
    other_fee = models.FloatField(null=True, blank=True)    # 杂费
    deposit = models.FloatField(null=True, blank=True)      # 预付款
    deposit_payed = models.FloatField(null=True, blank=True)    # 已缴纳的预付款
    traffic_fee_payed = models.FloatField(null=True, blank=True)    # 已缴纳的物流费
    other_fee_payed = models.FloatField(null=True, blank=True)      # 已缴纳的杂费
    final_payment_payed = models.FloatField(null=True, blank=True)  # 已交尾款
    expect_date = models.DateField(null=True, blank=True)   # 交期
    unit_price = models.FloatField(null=True, blank=True)   # 最终单价=（数量*单价+物流费+杂费）/数量
    # 入库
    received_count = models.IntegerField(null=True, blank=True)     # 已入库数量


class FinanceRecord(models.Model):
    # 费用缴纳记录
    order = models.ForeignKey(PurchasingOrder)
    fee_type = models.CharField(max_length=20)      # 费用类型：deposit(预付款)，traffic_fee, other_fee, principal(商品付款)
    need_payed = models.FloatField()        # 需付款数
    payed = models.FloatField()             # 实际付款数
    pay_time = models.DateTimeField()       # 付款时间
    creator = models.ForeignKey(User)       # 付款人


class InboundProducts(models.Model):
    # 已入库商品
    order = models.ForeignKey(PurchasingOrder, related_name='inbounds')
    product = models.ForeignKey(Product)
    shipping_date = models.DateField()      # 发货时间
    traffic_info = models.CharField(max_length=255, null=True, blank=True)      # 物流信息
    count = models.IntegerField(null=True, blank=True)
    inbound_time = models.DateTimeField(null=True, blank=True)   # 入库时间
    traffic_fee = models.FloatField(null=True, blank=True)      # 物流费
    traffic_fee_payed = models.FloatField(null=True, blank=True)    # 已缴纳的物流费
    status = models.ForeignKey(OrderStatus)
    # payment = models.FloatField(null=True, blank=True, default=0)

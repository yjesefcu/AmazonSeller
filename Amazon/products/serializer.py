__author__ = 'liucaiyun'
import datetime
from rest_framework import serializers
from models import *


class ProfitRateField(serializers.CharField):

    def to_representation(self, value):
        if not value:
            return '0%'
        return '%d%%' % (round(value, 3) * 100)


class FloatRoundField(serializers.FloatField):

    def to_representation(self, value):
        if not value:
            return value
        return round(value, 2)


class DateTimeFormat(serializers.DateTimeField):

    def to_representation(self, value):
        if not value:
            return ''
        return value.strftime('%Y-%m-%d %H:%M:%S')


class DateFormatField(serializers.DateTimeField):

    def to_representation(self, value):
        if not value:
            return ''
        return value.strftime('%m-%d')


class DateFormat(serializers.DateTimeField):

    def to_representation(self, value):
        return value.strftime('%Y-%m-%d')


class SettlementSerializer(serializers.ModelSerializer):
    StartDate = DateFormat()
    EndDate = DateFormat()
    profit = FloatRoundField()
    profit_rate = ProfitRateField()
    sales_amount = FloatRoundField()
    total_cost = FloatRoundField()

    class Meta:
        model = Settlement
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class ProductSettlementSerializer(serializers.ModelSerializer):
    settlement = SettlementSerializer()
    profit = FloatRoundField()
    profit_rate = ProfitRateField()
    sales_amount = FloatRoundField()
    total_cost = FloatRoundField()
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductSettlement
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    PostedDate = DateTimeFormat()
    profit = FloatRoundField()

    class Meta:
        model = SettleOrderItem
        fields = '__all__'


class InboundShipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = InboundShipment
        fields = '__all__'


class SimpleOutboundShipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutboundShipment
        fields = '__all__'


class OutboundShipmentItemSerializer(serializers.ModelSerializer):
    shipment = SimpleOutboundShipmentSerializer(read_only=True)

    class Meta:
        model = OutboundShipmentItem
        # fields = '__all__'
        exclude = ['shipment', 'product']


class OutboundShipmentSerializer(serializers.ModelSerializer):
    products = OutboundShipmentItemSerializer(many=True, read_only=True)

    class Meta:
        model = OutboundShipment
        fields = '__all__'


class ProductRemovalItemSerializer(serializers.ModelSerializer):
    UpdateDate = DateFormatField(read_only=True)
    product = ProductSerializer(read_only=True)
    profit = FloatRoundField()

    class Meta:
        model = ProductRemovalItem
        fields = '__all__'


class AdvertisingItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdvertisingProductItems
        fields = '__all__'


class ProductLostSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    PostedDate = DateFormatField(read_only=True)
    profit = FloatRoundField()

    class Meta:
        model = OtherTransactionItem
        fields = '__all__'


class RefundItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    PostedDate = DateFormatField(read_only=True)
    profit = FloatRoundField()

    class Meta:
        model = RefundItem
        fields = '__all__'



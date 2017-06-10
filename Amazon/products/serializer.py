__author__ = 'liucaiyun'
import datetime
from rest_framework import serializers
from models import *


class DateTimeFormat(serializers.DateTimeField):

    def to_representation(self, value):
        if not value:
            return ''
        return value.strftime('%Y-%m-%d %H:%M:%S')


class DateFormat(serializers.DateTimeField):

    def to_representation(self, value):
        return value.strftime('%Y-%m-%d')


class SettlementSerializer(serializers.ModelSerializer):
    StartDate = DateFormat()
    EndDate = DateFormat()

    class Meta:
        model = Settlement
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    PostedDate = DateTimeFormat()

    class Meta:
        model = SettleOrderItem
        fields = '__all__'


class InboundShipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = InboundShipment
        fields = '__all__'


class OutboundShipmentItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutboundShipmentItem
        # fields = '__all__'
        exclude = ['shipment', 'product', 'id']


class OutboundShipmentSerializer(serializers.ModelSerializer):
    products = OutboundShipmentItemSerializer(many=True, read_only=True)

    class Meta:
        model = OutboundShipment
        fields = '__all__'
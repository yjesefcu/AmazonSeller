__author__ = 'liucaiyun'
from rest_framework import serializers
from products.serializer import ProductSerializer
from models import *


class StatusField(serializers.CharField):

    def to_representation(self, value):
        for index in range(0, len(PurchasingOrder.STATUS_CHOICE)):
            v, name = PurchasingOrder.STATUS_CHOICE[index]
            if v == int(value):
                return name
        return value


class DateTimeFormat(serializers.DateTimeField):

    def to_representation(self, value):
        if not value:
            return ''
        return value.strftime('%Y-%m-%d %H:%M')


class ContractSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contract
        fields = '__all__'


class PurchasingOrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    create_time = DateTimeFormat(read_only=True)
    contract = ContractSerializer(read_only=True)
    status_name = StatusField(source='status')

    class Meta:
        model = PurchasingOrder
        fields = '__all__'


class InboundSerializer(serializers.ModelSerializer):
    inbound_time = DateTimeFormat()
    status_name = StatusField(source='status')

    class Meta:
        model = InboundProducts
        fields = '__all__'
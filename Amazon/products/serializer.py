__author__ = 'liucaiyun'
from rest_framework import serializers
from models import *


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class ShipInSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShipsIn
        fields = '__all__'


class ShipOverseaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShipsOversea
        fields = '__all__'
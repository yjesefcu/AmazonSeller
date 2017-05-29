#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status
from rest_framework.response import Response
from models import *
from serializer import *


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class ProductViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ShipInViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = ShipsIn.objects.all()
    serializer_class = ShipInSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def perform_create(self, serializer):
        # 保存时更新商品相应信息
        serializer.save()
        supply = serializer.instance
        product = supply.product
        # 修改商品的最后入库时间
        if not product.last_supply or product.last_supply < supply.ship_date:
            product.last_supply = supply.ship_date
        # 更新商品的剩余总数量
        product.remain_count += supply.count
        # 重新计算当前成本
        # todo
        product.save()


class ShipOverseaViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = ShipsOversea.objects.all()
    serializer_class = ShipOverseaSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
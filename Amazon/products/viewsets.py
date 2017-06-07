#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from models import *
from serializer import *


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class SettlementViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer


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


class InboundShipmentViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = InboundShipment.objects.all()
    serializer_class = InboundShipmentSerializer
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


class OrderViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = SettleOrderItem.objects.all()
    serializer_class = OrderItemSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('settlement',)

    # def get_queryset(self):
    #     """
    #     Optionally restricts the returned purchases to a given user,
    #     by filtering against a `username` query parameter in the URL.
    #     """
    #     queryset = SettleOrderItem.objects.all()
    #     settlement = self.request.query_params.get('settlement', None)
    #     if settlement is not None:
    #         queryset = queryset.filter(settlement=settlement)
    #     return queryset


class OutboundShipmentViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = OutboundShipment.objects.all()
    serializer_class = OutboundShipmentSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
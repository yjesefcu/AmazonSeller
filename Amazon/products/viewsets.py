#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django_filters.rest_framework import DjangoFilterBackend
from models import *
from serializer import *


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class SettlementViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('MarketplaceId',)


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

    @detail_route(methods=['get'])
    def settlements(self, request, pk):
        product = self.get_object()
        settlement_id_list = set(list(SettleOrderItem.objects.filter(product=product).values_list('settlement', flat=True)))
        settlements = Settlement.objects.filter(pk__in=settlement_id_list)
        serializer = SettlementSerializer(settlements, many=True)
        return Response(serializer.data)


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
    filter_fields = ('settlement', 'MarketplaceId')


class OutboundShipmentViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = OutboundShipment.objects.all()
    serializer_class = OutboundShipmentSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('MarketplaceId',)

    def create(self, request, *args, **kwargs):
        # 先检查商品SKU是否都存在
        data = request.data
        not_exists = self._check_sku(data)
        if not_exists:
            return Response({
                'result': 'fail',
                'msg': not_exists
            }, status=status.HTTP_400_BAD_REQUEST)
            del data['products']
        products = data.get('products', [])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        items = self._create_or_update_items(serializer.instance, products)
        return_data = serializer.data
        return_data['products'] = OutboundShipmentItemSerializer(items, many=True).data
        return Response(return_data, status=status.HTTP_201_CREATED, headers=headers)

    def _check_sku(self, data):
        if 'products' not in data:
            return None
        products = data['products']
        existed = list(Product.objects.all().values_list('SellerSKU', flat=True))
        not_exist = list()
        for p in products:
            if p['SellerSKU'] not in existed:
                not_exist.append(p['SellerSKU'])
        if not_exist:
            return ','.join(not_exist) + u': 商品未创建，请先创建产品.'
        return None

    def update(self, request, *args, **kwargs):
        # 先检查商品SKU是否都存在
        data = request.data
        not_exists = self._check_sku(data)
        if not_exists:
            return Response({
                'result': 'fail',
                'msg': not_exists
            }, status=status.HTTP_400_BAD_REQUEST)
            del data['products']
        # 更新shipment信息
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # 更新items
        self._create_or_update_items(instance, data.get('products'))
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def _create_or_update_items(self, shipment, data):
        if not data:
            return []
        items = list()
        for item in data:
            product = Product.objects.get(SellerSKU=item['SellerSKU'])
            # 计算体积重
            item['volume_weight'] = float(item['package_width']) * float(item['package_length']) * \
                                    float(item['package_height']) / float(5000)
            # 计算总运费
            item['total_freight'] = max(float(item['volume_weight']), float(item['package_weight'])) * \
                                    (1 + float(item['fuel_tax'])) * float(item['unit_freight']) * int(item['QuantityShipped'])
            s, created = OutboundShipmentItem.objects.get_or_create(shipment=shipment, MarketplaceId=shipment.MarketplaceId, product=product)
            for key, value in item.items():
                setattr(s, key, value)
            s.save()
            items.append(item)
        return items

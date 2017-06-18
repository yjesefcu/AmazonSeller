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


class SettlementProductViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = ProductSettlement.objects.all()
    serializer_class = ProductSettlementSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('settlement',)


class ProductViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('MarketplaceId',)

    @detail_route(methods=['get'])
    def settlements(self, request, pk):
        product = self.get_object()
        settlements = ProductSettlement.objects.filter(product=product)
        serializer = ProductSettlementSerializer(settlements, many=True)
        return Response(serializer.data)


class SupplyViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = InboundShipment.objects.all()
    serializer_class = InboundShipmentSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('product',)


class ProductShipmentItemViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = OutboundShipmentItem.objects.all()
    serializer_class = OutboundShipmentItemSerializer


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
        not_exists = self._check_product(data)
        if not_exists:
            return Response({
                'result': 'fail',
                'msg': not_exists
            }, status=status.HTTP_400_BAD_REQUEST)
            del data['products']
        products = data.get('products', [])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Inbound的数量比较 < Supply的剩余数量
        try:
            instance = OutboundShipment.objects.get(MarketplaceId=data['MarketplaceId'], ShipmentId=data['ShipmentId'])
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except OutboundShipment.DoesNotExist, ex:
            self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        items = self._create_or_update_items(serializer.instance, products)
        return_data = serializer.data
        return_data['products'] = OutboundShipmentItemSerializer(items, many=True).data
        return Response(return_data, status=status.HTTP_201_CREATED, headers=headers)

    def _check_product(self, data):
        """
        检查商品是否存在，或数量是否合理
        :param data:
        :return:
        """
        if 'products' not in data:
            return None
        products_data = data['products']
        existed = list(Product.objects.all().values_list('SellerSKU', flat=True))
        not_exist = list()
        for p in products_data:
            if p['SellerSKU'] not in existed:
                not_exist.append(p['SellerSKU'])
        if not_exist:
            return u', '.join(not_exist) + u': 商品不存在，请先创建商品'

        # 计算配送数量是否合理
        sku_list = [p['SellerSKU'] for p in products_data]
        inventory = dict(Product.objects.filter(SellerSKU__in=sku_list).values_list('SellerSKU', 'domestic_inventory'))
        count_exceed = list()
        for p in products_data:
            if 'id' in p:
                item = OutboundShipmentItem.objects.get(pk=p['id'])
                count = int(p['QuantityShipped']) - item.QuantityShipped
            else:
                count = int(p['QuantityShipped'])
            if count > inventory[p['SellerSKU']]:
                count_exceed.append(p['SellerSKU'])
        if count_exceed:
            return u', '.join(count_exceed) + u': 数量超过国内库存数量，请确认数量是否正确。或先添加入库货件信息。'

    def update(self, request, *args, **kwargs):
        # 先检查商品SKU是否都存在
        data = request.data
        not_exists = self._check_product(data)
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
            item['volume_weight'] = round(float(item['package_width']) * float(item['package_length']) * \
                                    float(item['package_height']) / float(5000), 2)

            # 计算总运费
            item['total_freight'] = max(float(item['volume_weight']), float(item['package_weight'])) * \
                                    (1 + float(item['fuel_tax'])) * float(item['unit_freight']) * int(item['QuantityShipped'])
            s, created = OutboundShipmentItem.objects.get_or_create(shipment=shipment, MarketplaceId=shipment.MarketplaceId, product=product)
            # 商品库存信息修改
            if int(item['QuantityShipped']) != s.QuantityShipped:
                self._update_inventory(s, int(item['QuantityShipped']) - s.QuantityShipped)
            s.inventory += int(item['QuantityShipped']) - s.QuantityShipped
            for key, value in item.items():
                setattr(s, key, value)
            s.save()
            items.append(s)
        return items

    def _update_inventory(self, shipment_item, count):
        product = shipment_item.product
        product.domestic_inventory -= count   # 如果数量变更，需要相应的更改商品的库存信息
        product.amazon_inventory += count
        product.save()

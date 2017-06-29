#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import os, datetime, chardet, threading
from django.conf import settings
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django_filters.rest_framework import DjangoFilterBackend
from amazon_services.exception import TextParseException
from amazon_services.models import MarketAccount
from models import *
from serializer import *
from api import FileImporter, to_float, get_float, ValidationChecker
from errors import Error
from data_export import DataExport


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class SettlementViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('MarketplaceId',)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    @detail_route(methods=['get'])
    def check(self, request, pk):
        """
        计算前检查数据的有效性
        """
        instance = self.get_object()
        # 数据是否有效，主要是广告数据
        if not instance.advertising_report_valid:
            return Response({'data_sync_valid': False})
        invalid_products = ValidationChecker(instance).check()
        sku_list = [p.SellerSKU for p in invalid_products]
        advertising_valid = True if instance.advertising_fee_adjust else False
        return Response({'products': ',  '.join(sku_list), 'storage_imported': instance.storage_imported,
                         'removal_imported': instance.removal_imported, 'advertising_valid': advertising_valid})

    @detail_route(methods=['get'])
    def calc(self, request, pk):
        from api import SettlementCalc, ProductProfitCalc
        instance = self.get_object()
        recalc_product = request.query_params.get('withProduct', True)
        if instance.calc_status == Error.RUNNING:
            return Response({'errno': Error.RUNNING})
        threading.Thread(target=SettlementCalc(settlement=instance).calc_settlement, args=[recalc_product, ]).start()
        return Response({'errno': Error.SUCCESS})

    @detail_route(methods=['get'])
    def calcStatus(self, request, pk):
        instance = self.get_object()
        return Response({'errno': instance.calc_status})

    @list_route(methods=['get'])
    def sync(self, request):
        # 同步数据
        from sync_handler import update_all
        market_place_id = request.query_params.get('MarketplaceId')
        market = MarketAccount.objects.get(MarketplaceId=market_place_id)
        if market.is_getting_report:
            return Response({'errno': Error.RUNNING})
        threading.Thread(target=update_all, args=[market, ]).start()
        return Response({'errno', Error.SUCCESS})

    @list_route(methods=['get'])
    def syncStatus(self, request):
        # 查询同步数据的状态
        market_place_id = request.query_params.get('MarketplaceId')
        market = MarketAccount.objects.get(MarketplaceId=market_place_id)
        if market.is_getting_report:
            return Response({'errno': Error.RUNNING})
        return Response({'errno', Error.SUCCESS})

    @detail_route(methods=['post'])
    def storage_upload(self, request, pk):
        instance = self.get_object()
        my_file = request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
        if not my_file:
            return Response({'errno': -1})
        text = ''
        for chunk in my_file.chunks():      # 分块写入文件
            text += unicode(chunk, chardet.detect(chunk)['encoding'])
        try:
            items = FileImporter().import_storage(text, instance)
        except TextParseException, ex:
            return Response({'errno': 1})
        instance.storage_imported = True
        instance.save()
        return Response({'error': 0, 'data': ProductRemovalItemSerializer(items, many=True).data})

    @detail_route(methods=['patch'])
    def advertising(self, request, pk):
        instance = self.get_object()
        fee = request.query_params.get('advertising_fee_adjust')

    @detail_route(methods=['get'])
    def download(self, request, pk):
        instance = self.get_object()
        filename = DataExport(instance).export()
        return Response({'path': filename})


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
    queryset = InboundShipment.objects.select_related('product').all()
    serializer_class = InboundShipmentSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    # filter_backends = (DjangoFilterBackend,)
    # filter_fields = ('product',)

    def perform_create(self, serializer):
        serializer.save()
        instance = serializer.instance
        # 计算单位成本
        instance.inventory = instance.count
        instance.real_inventory = instance.count
        instance.unit_cost = to_float(instance.unit_price) + (to_float(instance.total_freight)+to_float(instance.charges)) / instance.count
        instance.save()
        # 更新product的库存
        _query_dict = self.get_parents_query_dict()
        product = Product.objects.get(pk=_query_dict['product'])
        product.domestic_inventory += instance.inventory
        product.save()


class ProductShipmentItemViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = OutboundShipmentItem.objects.all()
    serializer_class = OutboundShipmentItemSerializer


class ProfitProductFilter(object):

    def filter_queryset(self, request, queryset, view):
        data = request.query_params
        if 'product' in data:
            product = data.get('product')
            if not product:
                queryset = queryset.filter(product__isnull=True)
            else:
                queryset = queryset.filter(product__pk=product)
        queryset = queryset.filter(is_total=data.get('is_total', False))
        return queryset


class SettlementProductViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = ProductSettlement.objects.select_related('product').all()
    serializer_class = ProductSettlementSerializer
    filter_backends = (DjangoFilterBackend, ProfitProductFilter,)
    filter_fields = ('settlement', 'product', 'is_total')


class OrderViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = SettleOrderItem.objects.select_related('product').all()
    serializer_class = OrderItemSerializer
    filter_backends = (DjangoFilterBackend, ProfitProductFilter,)
    # filter_fields = ('settlement', 'product', 'is_total')

    @detail_route(methods=['patch'])
    def cost(self, request, pk):
        # 更新成本
        instance = self.get_object()
        instance.update_unit_cost(request.data.get('cost'))
        return Response(self.get_serializer_class()(instance).data)


class OutboundShipmentItemViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = OutboundShipmentItem.objects.all()
    serializer_class = OutboundShipmentItemSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)


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
            item['total_freight'] = max(get_float(item, 'volume_weight'), get_float(item, 'package_weight')) * \
                                    (1 + get_float(item, 'fuel_tax')) * get_float(item, 'unit_freight') * int(item['QuantityShipped'])
            s, created = OutboundShipmentItem.objects.get_or_create(shipment=shipment, MarketplaceId=shipment.MarketplaceId, product=product)
            # 商品库存信息修改
            if int(item['QuantityShipped']) != s.QuantityShipped:
                self._update_inventory(s, int(item['QuantityShipped']) - s.QuantityShipped)
            s.inventory += int(item['QuantityShipped']) - s.QuantityShipped
            for key, value in item.items():
                setattr(s, key, value)
            s.unit_cost = get_float(item, 'total_freight') / int(item['QuantityShipped'])
            # s.domestic_unit_cost = self._calc_supply_cost(s.product)
            # s.inventory = int(item['QuantityShipped'])
            # s.total_unit_cost = s.unit_cost + s.domestic_unit_cost
            s.ShipmentId = shipment.ShipmentId
            s.ship_date = shipment.ship_date
            s.save()
            items.append(s)
        return items

    def _calc_supply_cost(self, product):
        # 计算商品当前的国内平均入库成本
        inbounds = InboundShipment.objects.filter(product=product, inventory__gt=0)
        amount = 0
        quantity = 0
        for inbound in inbounds:
            quantity += inbound.inventory
            amount += inbound.inventory * inbound.unit_cost
        return amount / quantity if quantity else 0

    def _update_inventory(self, shipment_item, count):
        # 更新商品库存
        product = shipment_item.product
        product.domestic_inventory -= count   # 如果数量变更，需要相应的更改商品的库存信息
        product.amazon_inventory += count
        product.save()
        # 更新InboundShipment的库存
        inbounds = InboundShipment.objects.filter(product=product, real_inventory__gt=0)
        tmp_count = count
        for inbound in inbounds:
            if tmp_count <= inbound.real_inventory:
                inbound.real_inventory -= tmp_count
                inbound.save()
                break
            tmp_count -= inbound.real_inventory
            inbound.real_inventory = 0
            inbound.save()


class RefundViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = RefundItem.objects.select_related('product').all()
    serializer_class = RefundItemSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    filter_backends = (DjangoFilterBackend, ProfitProductFilter,)
    # filter_fields = ('settlement', 'product', 'is_total')

    @detail_route(methods=['patch'])
    def cost(self, request, pk):
        # 更新成本
        instance = self.get_object()
        instance.update_unit_cost(request.data.get('cost'))
        return Response(self.get_serializer_class()(instance).data)


class RemovalViewSet(NestedViewSetMixin, ModelViewSet):

    queryset = ProductRemovalItem.objects.select_related('product').all()
    serializer_class = ProductRemovalItemSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    filter_backends = (DjangoFilterBackend, ProfitProductFilter,)
    # filter_fields = ('settlement', 'product', 'is_total')

    @detail_route(methods=['patch'])
    def cost(self, request, pk):
        # 更新成本
        instance = self.get_object()
        instance.update_unit_cost(request.data.get('cost'))
        return Response(self.get_serializer_class()(instance).data)

    @list_route(methods=['post'])
    def upload(self, request, *args, **kwargs):

        my_file = request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
        if not my_file:
            return Response({'errno': -1})
        text = ''
        for chunk in my_file.chunks():      # 分块写入文件
            text += unicode(chunk, chardet.detect(chunk)['encoding'])
        try:
            _query_dict = self.get_parents_query_dict()
            settlement = Settlement.objects.get(pk=_query_dict['settlement'])
            items = FileImporter().import_removals(text, settlement)
        except TextParseException, ex:
            return Response({'errno': 1})
        settlement.removal_imported = True
        settlement.save()
        return Response({'error': 0, 'data': ProductRemovalItemSerializer(items, many=True).data})


class ProductLostViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = OtherTransactionItem.objects.select_related('product').all()
    serializer_class = ProductLostSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    filter_backends = (DjangoFilterBackend, ProfitProductFilter,)
    # filter_fields = ('settlement', 'product', 'is_total')

    @detail_route(methods=['patch'])
    def cost(self, request, pk):
        # 更新成本
        instance = self.get_object()
        instance.update_unit_cost(request.data.get('cost'))
        return Response(self.get_serializer_class()(instance).data)


class AdvertisingViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = AdvertisingProductItems.objects.select_related('product').all()
    serializer_class = AdvertisingItemSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
__author__ = 'liucaiyun'
from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework_extensions.routers import ExtendedSimpleRouter
from viewsets import *


router = ExtendedSimpleRouter()
product = router.register(r'products', ProductViewSet, base_name="api_products")
product.register(r'supply', SupplyViewSet, base_name="api_ships_in", parents_query_lookups=['product'])
product.register(r'orders', OrderViewSet, base_name="api_product_orders", parents_query_lookups=['product'])
router.register(r'shipments', OutboundShipmentViewSet, base_name="api_ships_oversea")
settlement = router.register(r'settlements', SettlementViewSet, base_name="api_settlements")
settlement.register(r'products', SettlementProductViewSet, base_name="api_settlment_products", parents_query_lookups=['settlement'])

urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
    url('^image/upload/$', 'products.views.image_upload'),
    url(r'^sync$', 'products.views.sync_orders'),
)

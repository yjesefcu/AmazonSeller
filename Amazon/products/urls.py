__author__ = 'liucaiyun'
from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework_extensions.routers import ExtendedSimpleRouter
from viewsets import *


router = ExtendedSimpleRouter()
router.register(r'products', ProductViewSet, base_name="api_products")\
       .register(r'supply', ShipInViewSet, base_name="api_ships_in", parents_query_lookups=['product'])
router.register(r'oversea', ShipOverseaViewSet, base_name="api_ships_oversea")

urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
    url('^image/upload/$', 'products.views.image_upload'),
)

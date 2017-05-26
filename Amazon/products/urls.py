__author__ = 'liucaiyun'
from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework_extensions.routers import ExtendedSimpleRouter
from viewsets import *


router = ExtendedSimpleRouter()
router.register(r'products', ProductViewSet, base_name="api_products")

urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
)

__author__ = 'liucaiyun'
from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework_extensions.routers import ExtendedSimpleRouter
from viewsets import *


router = ExtendedSimpleRouter()

product = router.register(r'users', UserViewSet, base_name="api_users")

urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
)
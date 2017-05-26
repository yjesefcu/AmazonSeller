__author__ = 'liucaiyun'
from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('',
    url(r'^action$', 'amazon_services.views.request_to_amazon', name='request_to_amazon'),
)

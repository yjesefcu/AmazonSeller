#-*- coding:utf-8 -*-
import os, datetime
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from api import create_image_path
from amazon_services.models import MarketAccount
from models import *


def image_upload(request):
    if request.method == 'POST':
        my_file = request.FILES.get("image", None)    # 获取上传的文件，如果没有文件，则默认为None
        if not my_file:
            return HttpResponse("no files for upload!")
        file_path = create_image_path()
        destination = open(os.path.join(settings.MEDIA_ROOT, file_path), 'wb+')    # 打开特定的文件进行二进制的写操作
        for chunk in my_file.chunks():      # 分块写入文件
            destination.write(chunk)
        destination.close()
        return HttpResponse(settings.MEDIA_URL + file_path)


def sync_orders(request):
    from sync_handler import update_all
    market_place_id = request.GET.get('MarketplaceId')
    if not market_place_id:
        market_place_id = 'ATVPDKIKX0DER'
    market = MarketAccount.objects.get(MarketplaceId=market_place_id)
    update_all(market)

    return HttpResponse('success')
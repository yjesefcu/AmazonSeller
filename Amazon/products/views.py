#-*- coding:utf-8 -*-
import os, datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings


def create_image_path():
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    p = os.path.join(settings.MEDIA_ROOT, 'icon')
    if not os.path.exists(p):
        os.mkdir(p)
    return 'icon/' + timestamp + '.png'


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
        return HttpResponse('media/' + file_path)
#-*- coding:utf-8 -*-
import os
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
    # update_all(market)
    settlement = Settlement.objects.first()
    # _init_shipment()
    product = Product.objects.all().order_by('pk').first()
    from api import ProductProfitCalc, SettlementCalc
    for product in Product.objects.all():
        ProductProfitCalc(settlement).calc_product_profit(product)
    SettlementCalc(settlement).calc_settlement()
    # from api import SettlementDbHandler
    # SettlementDbHandler(market)._init_settlement_products(settlement)
    # return HttpResponse('success')


def _init_inbounds():
    import requests
    for product in Product.objects.all().order_by('pk'):
        data = {
            'count': '500',
            'unit_price': '1.58',
            'total_freight': '625',
            'charges': '25',
            'ship_date': '2017-05-23',
            'product': '%d' % product.pk
        }
        url = 'http://127.0.0.1:8000/api/products/%d/supply/' % product.pk
        r = requests.post(url, data=data)
        if r.status_code != 201:
            print r.text
            break


def _init_shipment():
    outbound = None
    products = list()
    import requests
    for product in Product.objects.all().order_by('pk'):
        if not outbound:
            outbound = {
                'MarketplaceId': product.MarketplaceId,
                'ShipmentId': 'abcdefghi',
                'ship_date': '2017-05-03'
            }
        item = {
            'SellerSKU': product.SellerSKU,
            'QuantityShipped': '199',
            'unit_freight': '1.19',
            'fuel_tax': '0.15',
            'duty': '53',
            'package_length': '10.9',
            'package_width': '3.1',
            'package_height': '1.9',
            'package_weight': '1.1'
        }
        products.append(item)
    outbound['products'] = products
    url = 'http://127.0.0.1:8000/api/shipments/'
    import json
    r = requests.post(url, data=json.dumps(outbound), headers={'content-type': 'application/json'})
    print r.status_code


# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#
#         if form.is_valid():
#             handle_upload_file(request.FILES.get('file', None))
#             ftemp = request.FILES.get('file', None)
#             print('ftemp: ', ftemp)
#             return HttpResponseRedirect('/success/')
#     else:
#         form = UploadFileForm()
#
#     return render(request, 'upload.html', {'form':form})
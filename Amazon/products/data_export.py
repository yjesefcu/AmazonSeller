#-*- coding:utf-8 -*-
"""
将数据格式化成excel需要的格式
"""
__author__ = 'liucaiyun'
import sys, xlwt
from xlwt import *
from models import *
from serializer import *
reload(sys)
sys.setdefaultencoding('utf-8')


#styleBlueBkg = xlwt.easyxf('font: color-index red, bold on')
#styleBlueBkg = xlwt.easyxf('font: background-color-index red, bold on')
bgRed = xlwt.easyxf('pattern: pattern solid, fore_colour red;')
bgBlue = xlwt.easyxf('pattern: pattern solid, fore_colour blue;')
bgLightBlue = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue; font: bold on;')
bgPaleBlue = xlwt.easyxf('pattern: pattern solid, fore_colour pale_blue; font: bold on;')
bgDarkBlue = xlwt.easyxf('pattern: pattern solid, fore_colour dark_blue; font: bold on;')
bgDarkBlueEga = xlwt.easyxf('pattern: pattern solid, fore_colour dark_blue_ega; font: bold on;')
bgIceBlue = xlwt.easyxf('pattern: pattern solid, fore_colour ice_blue; font: bold on;')
bgOceanBlue = xlwt.easyxf('pattern: pattern solid, fore_colour ocean_blue; font: bold on;') # 80% like
bgSkyBlue = xlwt.easyxf('pattern: pattern solid, fore_colour sky_blue; font: bold on;')
bgLightYellow = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow; font: bold on;')


#blueBkgFontStyle = xlwt.XFStyle()
#blueBkgFontStyle.Pattern = blueBackgroundPattern;
#styleBlueBkg = blueBkgFontStyle;

styleBold = xlwt.easyxf('font: bold on')


def add_product_info_to_fields(index, fields):
    fields.insert(index, u'描述')
    fields.insert(index, u'图片')
    fields.insert(index, u'SKU')


class DataExport(object):

    def __init__(self, settlement):
        self.settlement = settlement
        self.wb = Workbook()

    def _save(self):
        name = 'd:\\%s - %s.xls' % (self.settlement.StartDate.date(), self.settlement.EndDate.date())
        style = XFStyle()
        font = Font()
        font.name = 'SimSun' # 指定“宋体”
        style.font = font
        self.wb.save(name)

    def export(self):
        records = ProductSettlement.objects.select_related('product').filter(settlement=self.settlement)\
            .order_by('product__SellerSKU', 'is_total')
        summary = self.format_product_settlement(records)
        self.add_sheet(u'总计', summary)
        self.add_products()
        self._save()

    def format_product_settlement(self, records):
        """
        ProductSettlement to excel data
        """
        descriptions = [u'SKU', u'图片', u'描述', u'数量', u'商品价格', u'促销返点', u'亚马逊收取', u'实收', u'仓储费',
                        u'广告费', u'订阅费', u'总成本', u'利润', u'利润率']
        fields = ['product', 'quantity', 'income', 'promotion', 'amazon_cost', 'amount', 'storage_fee', 'advertising_fee',
                  'subscription_fee', 'total_cost', 'profit', 'profit_rate']
        results = [descriptions]
        items = ProductSettlementSerializer(records, many=True).data
        for item in items:
            product = item['product']
            if item['is_total']:
                product ={'SellerSKU': u'总计'}
            result = list()
            for field in fields:
                if field == 'product':
                    result.append(product.get('SellerSKU', ''))
                    result.append(product.get('Image', ''))
                    result.append(product.get('TitleCn'))
                else:
                    result.append(item.get(field, ''))
            results.append(result)
        return results

    def _save_settlement_detail(self, settlement):
        """
        将settlement的订单按 订单、退货、移除、弃置等写入表格
        :param product:
        :return:
        """
        pass

    def add_products(self):
        for ps in ProductSettlement.objects.filter(product__isnull=False).select_related('product').filter(settlement=self.settlement):
            product = ps.product
            self._save_orders(product)

    def _save_orders(self, product):
        sheet_name = product.SellerSKU
        ws = self.wb.add_sheet(sheet_name)
        # 订单
        orders = SettleOrderItem.objects.select_related('product').filter(settlement=self.settlement, product=product)\
            .order_by('product__SellerSKU', 'is_total')
        # orders = SettleOrderItem.objects.select_related('product').filter(settlement=self.settlement)\
        #     .exclude(product__isnull=False, is_total=True).order_by('product__SellerSKU', 'is_total')
        row = self._format_orders(ws, 0, orders, is_product=True)
        # 退货
        refunds = RefundItem.objects.select_related('product').filter(settlement=self.settlement, product=product)\
            .order_by('product__SellerSKU', 'is_total')
        row = self._format_refunds(ws, row+1, refunds, is_product=True)
        # 赔偿
        losts = OtherTransactionItem.objects.select_related('product').filter(settlement=self.settlement, product=product)\
            .order_by('product__SellerSKU', 'is_total')
        row = self._format_losts(ws, row+1, losts, is_product=True)
        # 弃置
        removals = ProductRemovalItem.objects.select_related('product').filter(settlement=self.settlement, product=product)\
            .order_by('product__SellerSKU', 'is_total')
        row = self._format_removals(ws, row+1, removals, is_product=True)
        # 结算
        settlement = ProductSettlement.objects.get(settlement=self.settlement, product=product)
        self._format_product_settlement(ws, row+1, settlement, is_product=True)

    def _format_orders(self, sheet, start_row, orders, is_product=False):
        if not orders.exists():
            return start_row
        descriptions = [u'日期', u'数量', u'商品价格', u'促销返点', u'亚马逊收取', u'实收',
                        u'订阅费', u'总成本', u'利润', u'利润率']
        fields = ['PostedDate', 'Quantity', 'income', 'promotion', 'amazon_cost', 'amount',
                  'subscription_fee', 'total_cost', 'profit', 'profit_rate']
        items = OrderItemSerializer(orders, many=True).data
        col_len = len(descriptions) if is_product else len(descriptions) + 3
        add_title(sheet, start_row+1, col_len, u'所有订单')
        return self._add_items_to_sheet(sheet, start_row+2, descriptions, fields, is_product, items)

    def _format_refunds(self, sheet, start_row, refunds, is_product=False):
        if not refunds.exists():
            return start_row
        descriptions = [u'日期', u'数量', u'商品价格', u'促销返点', u'亚马逊收取', u'实收',
                        u'订阅费', u'总成本', u'利润', u'利润率']
        fields = ['PostedDate', 'Quantity', 'income', 'promotion', 'amazon_cost', 'amount',
                  'subscription_fee', 'total_cost', 'profit', 'profit_rate']
        items = RefundItemSerializer(refunds, many=True).data
        col_len = len(descriptions) if is_product else len(descriptions) + 3
        add_title(sheet, start_row+1, col_len, u'退货')
        return self._add_items_to_sheet(sheet, start_row+2, descriptions, fields, is_product, items)

    def _format_losts(self, sheet, start_row, losts, is_product=False):
        if not losts.exists():
            return start_row
        descriptions = [u'日期', u'数量', u'商品价格', u'促销返点', u'亚马逊收取', u'实收',
                        u'订阅费', u'总成本', u'利润', u'利润率']
        fields = ['PostedDate', 'Quantity', 'income', 'promotion', 'amazon_cost', 'amount',
                  'subscription_fee', 'total_cost', 'profit', 'profit_rate']
        items = ProductLostSerializer(losts, many=True).data
        col_len = len(descriptions) if is_product else len(descriptions) + 3
        add_title(sheet, start_row+1, col_len, u'赔偿')
        return self._add_items_to_sheet(sheet, start_row+2, descriptions, fields, is_product, items)

    def _format_removals(self, sheet, start_row, removals, is_product=False):
        if not removals.exists():
            return start_row
        descriptions = [u'日期', u'数量', u'商品价格', u'促销返点', u'亚马逊收取', u'实收',
                        u'订阅费', u'总成本', u'利润', u'利润率']
        fields = ['PostedDate', 'Quantity', 'income', 'promotion', 'amazon_cost', 'amount',
                  'subscription_fee', 'total_cost', 'profit', 'profit_rate']
        items = ProductRemovalItemSerializer(removals, many=True).data
        col_len = len(descriptions) if is_product else len(descriptions) + 3
        add_title(sheet, start_row+1, col_len, u'弃置')
        return self._add_items_to_sheet(sheet, start_row+2, descriptions, fields, is_product, items)

    def _format_product_settlement(self, sheet, start_row, settlement, is_product=False):
        descriptions = [u'日期', u'数量', u'商品价格', u'促销返点', u'亚马逊收取', u'实收',
                        u'订阅费', u'总成本', u'利润', u'利润率']
        fields = ['PostedDate', 'Quantity', 'income', 'promotion', 'amazon_cost', 'amount',
                  'subscription_fee', 'total_cost', 'profit', 'profit_rate']
        items = ProductSettlementSerializer(settlement).data
        col_len = len(descriptions) if is_product else len(descriptions) + 3
        add_title(sheet, start_row+1, col_len, u'总计')
        return self._add_items_to_sheet(sheet, start_row+2, descriptions, fields, is_product, items)

    @classmethod
    def _add_items_to_sheet(cls, sheet, start_row, descriptions, fields, is_product, items):
        if not is_product:
            add_product_info_to_fields(1, descriptions)
            fields.insert(1, 'product')
        current_row = start_row
        for col in range(0, len(descriptions)):
            sheet.write(current_row, col, descriptions[col])
        if not isinstance(items, list):
            items = [items]
        for item in items:
            current_row += 1
            product = item['product']
            is_total = item['is_total']
            if is_total:
                product = {'SellerSKU': u'总计'}
            col = 0
            for field in fields:
                if field == 'product':
                    if not is_product:
                        add_to_col(sheet, current_row, col, product.get('SellerSKU', ''), is_total)
                        add_to_col(sheet, current_row, col+1, product.get('Image', ''), is_total)
                        add_to_col(sheet, current_row, col+2, product.get('TitleCn', ''), is_total)
                        col += 3
                else:
                    add_to_col(sheet, current_row, col, item.get(field, ''), is_total)
                    col += 1
        return current_row

    def add_sheet(self, sheet_name, data):
        ws = self.wb.add_sheet(sheet_name)
        rows = len(data)
        cols = len(data[0])
        for row in range(0, rows):
            for col in range(0, cols):
                ws.write(row + 1, col+1, data[row][col])


def add_to_col(sheet, r, c, value, is_total):
    if is_total:
        sheet.write(r, c, value, bgLightBlue)
    else:
        sheet.write(r, c, value)


def add_title(sheet, r, col_len, value):
    bg = bgLightYellow
    sheet.write(r, 0, value, bg)
    for c in range(1, col_len):
        sheet.write(r, c, '', bg)



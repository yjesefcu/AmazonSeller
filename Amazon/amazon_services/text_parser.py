#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'


class BaseTextParser(object):
    """
    对制表符文本格式的数据进行解析
    """

    def __init__(self, s):
        self.lines = list()
        for l in s.split('\r\n')[1:]:
            self.lines.append(tuple(l.strip().split('\t')))
        self.items = list()
        self._parse()

    def _parse(self):
        pass

    def get_items(self):
        return self.items


class InventorySummaryParser(BaseTextParser):
    """
    物流库存事件详情报告  解析
    """

    def _parse(self):

        for item in self.lines:
            d, id, type, status, update_date, sku, fnsku, disposition, quantity, cancled, disposed_quantity, \
            shipped_quantity, in_progress_quantity, fee, currency = item
            self.items.append({
                'RequestDate': d,
                'UpdateDate': update_date,
                'OrderId': id,
                'OrderStatus': status,
                'SellerSKU': sku,
                'FNSKU': fnsku,
                'Quantity': quantity,
                'Disposition': disposition,
                'Fee': fee
            })


class ProductRemovalParser(BaseTextParser):
    """
    商品移除表
    """
    def _parse(self):
        for item in self.lines:
            start_date, end_date, merchant, sku, clicks, impressions, ctr, currency, total_spend, avg = item
            self.items.append({
                'StartDate': start_date,
                'EndDate': end_date,
                'SellerSKU': sku,
                'TotalSpend': total_spend
            })


class AdvertisingParser(BaseTextParser):
    # 广告业绩表
    def _parse(self):
        for item in self.lines:
            if item and len(item) > 9:
                start_date, end_date, merchant, sku, clicks, impressions, ctr, currency, total_spend, avg = item
                self.items.append({
                    'StartDate': start_date,
                    'EndDate': end_date,
                    'SellerSKU': sku,
                    'TotalSpend': total_spend
                })


if __name__ == '__main__':
    f = open('text.txt', 'rb')
    string = f.readlines()
    f.close()
    parser = InventorySummaryParser(string)
    items = parser.get_items()
    print items
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
            d, t, sku, fulfillment_id, quantity, disposition = item
            self.items.append({
                'snapshot_date': d,
                'type': t,
                'SellerSKU': sku,
                'quantity': quantity,
                'disposition': disposition
            })



if __name__ == '__main__':
    f = open('text.txt', 'rb')
    string = f.readlines()
    f.close()
    parser = InventorySummaryParser(string)
    items = parser.get_items()
    print items
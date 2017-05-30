#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
import re
try:
    import xml.etree.cElementTree as ET
    from xml.etree.ElementTree import Element
except ImportError:
    import xml.etree.ElementTree as ET
import sys


class BaseParser(object):

    def __init__(self, s):
        try:
            if s.endswith('.xml'):
                s = self._read_from_file(s)
            encoded = self._encode(s)
            self.root = ET.fromstring(encoded.encode('utf-8'))   # 从字符串传递xml
            self.namespace = self._get_namespace(self.root)
            self.error_code = ''
            self.error_msg = ''
            self.items = []
            self.next_token = None
            if not self.is_error_response():
                self._parse()
        except Exception, e:
            raise Exception(u'parse xml string exception')

    def is_error_response(self):
        if self.root.tag == '{0}ErrorResponse'.format(self.namespace):
            # 失败的话获取失败信息
            self.error_code = self.find(self.root, 'Error/Code')
            self.error_msg = self.find(self.root, 'Error/Message')
            return True
        return False

    def errors(self):
        return self.error_code, self.error_msg

    def get_items(self):
        return self.items

    def get_next_token(self):
        return self.next_token

    def _read_from_file(self, f):
        file_object = open(f)
        try:
             all_the_text = file_object.read( )
        finally:
             file_object.close( )
        return all_the_text

    def _encode(self, s):
        """
        替换字符串中的特殊字符
        &lt;	<	小于
        &gt;	>	大于
        &amp;	&	和号
        &apos;	'	单引号
        &quot;	"	双引号
        """
        s = s.replace('&', '&amp;')
        return s

    def _get_namespace(self, root):
        import re
        m = re.match('\{.*\}', root.tag)
        return m.group(0) if m else ''

    def find(self, ele, tag):
        tags = tag.split('/')
        namespace_tags = ['{0}{1}'.format(self.namespace, t) for t in tags]
        return ele.find('/'.join(namespace_tags), tag)

    def findall(self, ele, tag):
        tags = tag.split('/')
        namespace_tags = ['{0}{1}'.format(self.namespace, t) for t in tags]
        return ele.findall('/'.join(namespace_tags), tag)

    def _parse(self):
        pass


class OrderParse(BaseParser):

    def _parse(self):
        result = self.find(self.root, 'ListOrdersResult')
        if not result:
            result = self.find(self.root, 'ListOrdersByNextTokenResult')
        orders = self.findall(result, 'Orders/Order')
        for order in orders:
            self.items.append(self._parse_order_values(order))
        next_token = self.find(result, 'NextToken')
        if next_token:
            self.next_token = next_token.text

    def _parse_order_values(self, order_element):
        fields = ['LatestShipDate', 'OrderType', 'PurchaseDate', 'AmazonOrderId', 'LastUpdateDate',
                  'IsReplacementOrder', 'ShipServiceLevel', 'OrderStatus', 'SalesChannel',
                  'NumberOfItemsUnshipped', 'IsPremiumOrder', 'MarketplaceId', 'FulfillmentChannel',
                  'IsPrime', 'SellerOrderId']
        order = dict()
        for field in fields:
            e = self.find(order_element, field)
            order[field] = e.text
        return order


class OrderItemParser(BaseParser):

    def _parse(self):
        result = self.find(self.root, 'ListOrderItemsResult')
        if not result:
            result = self.find(self.root, 'ListOrderItemsByNextTokenResult')
        items = self.findall(result, 'OrderItems/OrderItem')
        for item in items:
            item_parsed = self._parse_item_values(item)
            if item_parsed:
                self.items.append(self._parse_item_values(item))
        next_token = self.find(result, 'NextToken')
        if next_token:
            self.next_token = next_token.text

    def _parse_item_values(self, item_element):
        if not self.find(item_element, 'ItemPrice'):    # 如果没有订单价格，说明该订单还未付款，则不计入实际订单中
            return None
        item = dict()
        item['SKU'] = self.find(item_element, 'SellerSKU').text
        item['OrderItemId'] = self.find(item_element, 'OrderItemId').text
        item['ItemPrice'] = self.find(item_element, 'ItemPrice/Amount').text
        item_tax = self.find(item_element, 'ItemTax/Amount')
        if item_tax is not None:
            item['ItemTax'] = item_tax.text
        shipping_discount = self.find(item_element, 'ShippingDiscount/Amount')
        if shipping_discount is not None:
            item['ShippingDiscount'] = shipping_discount.text
        shipping_price = self.find(item_element, 'ShippingPrice/Amount')
        if shipping_price is not None:
            item['ShippingPrice'] = shipping_price.text
        shipping_tax = self.find(item_element, 'ShippingTax/Amount')
        if shipping_tax is not None:
            item['ShippingTax'] = shipping_tax.text
        return item


if __name__ == '__main__':
    parser = OrderParse('country.xml')
    print parser.is_error_response()
    # print parser.get_orders()
    # print parser.get_next_token()
#-*- coding:utf-8 -*-
__author__ = 'liucaiyun'
from PIL import Image
from xlwt import *

if __name__ == '__main__':
    w = Workbook()
    ws = w.add_sheet('xlwtwas here')
    ws.write(0, 0, u'中文')
    w.save('mini.xls')

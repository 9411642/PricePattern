# -*- coding: utf-8 -*-
"""
提供JDDBXML K線資料
"""
import requests
from bs4 import BeautifulSoup


class KBlock(object):
    """
    一根K棒
    """
    def __init__(self, date, open, high, low, close, volume):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def __repr__(self):
        return "<D:%d O:%.2f H:%.2f L:%.2f C:%.2f V:%d>" % (
            self.date, self.open, self.high, self.low, self.close, self.volume)


class KDataSvc(object):
    """
    提供K線查詢服務
    """
    def __init__(self, server):
        self.server = server

    """
    取得K線資料(目前只支援台股股票), 回傳array of KBlock
    """
    def getdata(self, symbol, freq, start, end):
        url = 'http://%s/jddbxml/gethistdata.aspx?SID=%s&ST=1&a=%d&b=%s&d=%s' % (
            self.server, symbol, freq, start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("item")
        klist = [KBlock(int(x['d']), float(x['o']), float(x['h']), float(x['l']), float(x['c']), float(x['v']))
                 for x in items]
        return klist[::-1]



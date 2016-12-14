# -*- coding: utf-8 -*-
"""
Ref: https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm

尋找歷史股價的趨勢線
"""
from __future__ import print_function
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import datetime

from math import *


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line(object):
    def __init__(self, a, b):
        self.m = (a.y - b.y) / (a.x - b.x)
        self.k = a.y - self.m * a.x

    def dist(self, p):
        return abs(self.m * p.x - p.y + self.k) / sqrt(self.m ** 2 + 1)


def douglas_peucker(points, eps):
    """
    eps: 當線段上每個點距離這條線都小於eps時, 則認為這一條線就是趨勢線. 否則以距離最大的點為分隔點, 分成左右兩組繼續往下找
    """
    if len(points) == 1:
        return [points[0]]
    line = Line(points[0], points[-1])
    _max = 0
    for i in range(1, len(points) - 1):
        if line.dist(points[i]) > _max:
            _max = line.dist(points[i])
            _furthest = i

    res = []
    if _max > eps:
        res1 = douglas_peucker(points[:_furthest], eps)
        res2 = douglas_peucker(points[_furthest:], eps)
        for i in range(len(res1)):
            res.append(res1[i])
        for i in range(len(res2)):
            res.append(res2[i])

    else:
        res.append(points[0])
        res.append(points[-1])

    return res


def plot_stock(stkid, start_time, end_time, epsilon):
    df = web.DataReader(stkid, 'yahoo', start_time, end_time)
    adj_close = df['Adj Close']

    points = []
    for i in range(len(adj_close)):
        a = Point(i, float(adj_close[i]))
        points.append(a)

    res = douglas_peucker(points, epsilon)
    line_x = []
    line_y = []
    for i in res:
        line_x.append(i.x)
        line_y.append(i.y)

    plt.plot(range(len(adj_close)), adj_close, c='b')
    plt.plot(line_x, line_y, c='r')
    plt.savefig("test.svg", format="svg")
    #plt.show()


if __name__ == "__main__":
    plot_stock("2498.TW", datetime.datetime(2013, 1, 1), datetime.datetime(2016, 6, 30), 20)

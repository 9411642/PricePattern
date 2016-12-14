# -*- coding: utf-8 -*-
"""
Ref: https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm

尋找歷史股價的趨勢線
"""
from __future__ import print_function
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
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


class RDP(object):
    def __init__(self, klist, epsilon):
        self.close = [k.close for k in klist]
        points = [Point(i, self.close[i]) for i in range(len(self.close))]
        self.lines = self.douglas_peucker(points, epsilon)
        self.line_x = [self.lines[i].x for i in range(len(self.lines))]
        self.line_y = [self.lines[i].y for i in range(len(self.lines))]

    def show(self):
        plt.plot(range(len(self.close)), self.close, c='b')
        plt.plot(self.line_x, self.line_y, c='r')
        plt.show()

    def render_png(self, pngfile):
        fig = Figure()
        subplot = fig.add_subplot(111)
        subplot.plot(range(len(self.close)), self.close, c='b')
        subplot.plot(self.line_x, self.line_y, c='r')
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(pngfile)

    def douglas_peucker(self, points, eps):
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

        lines = []
        if _max > eps:
            lines_left = self.douglas_peucker(points[:_furthest], eps)
            lines_right = self.douglas_peucker(points[_furthest:], eps)
            lines.extend(lines_left)
            lines.extend(lines_right)
        else:
            lines.append(points[0])
            lines.append(points[-1])

        return lines


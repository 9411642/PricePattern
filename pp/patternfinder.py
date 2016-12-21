# -*- coding: utf-8 -*-
"""
Ref:
- https://github.com/jbn/ZigZag
- http://www.investopedia.com/ask/answers/030415/what-zig-zag-indicator-formula-and-how-it-calculated.asp
- http://www.investopedia.com/university/charts/
- https://www.google.com.tw/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwjW-K7NuoTRAhULGJQKHS_uAmoQFggYMAA&url=http%3A%2F%2Fweb.mit.edu%2Fpeople%2Fwangj%2Fpap%2FLoMamayskyWang00.pdf&usg=AFQjCNEmFlwfXlmW_P7oIgCVefn5Ak53aw&sig2=c0X9UbqBI-6pwGXtarMlSQ
"""
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from pp import kdata

PEAK, VALLEY = 1, -1


def _is_close_enough(p1, p2, delta):
    """
    檢查p1,p2是否是在一直線上面 (TODO: 目前只判斷Y的數值(水平線), 以後的版本要改成判斷任何直線)
    :param p1: 第一個點的Y
    :param p2: 第二個點的Y
    :param delta: 差異範圍
    :return:
    """
    return abs(p1 - p2) / p2 <= delta


def _is_hs(X, pv_points, cur, delta):
    """
    Return true if 'cur'這個點是一個頭肩頂(head-and-shoulder)的pattern
    :param X: array of close price
    :param pv_points: pivot point, array of (index, direction)
    :param cur: 目前的點
    :param delta: E1/E5, E2/E4的容忍範圍
    :return: True or False
    """
    if cur > len(pv_points) - 5:
        return False

    # E1必須是個max
    _, direction = pv_points[cur]
    if direction != 1:
        return False

    # 接下來5個點的數值 = e1,e2,e3,e4,e5
    e1, e2, e3, e4, e5 = X[[p[0] for p in pv_points[cur:cur+5]]]

    # TODO 可以把e1,e2,e3,e4,e5這幾個點之間的距離考慮進去

    # E3要比E1/E5高
    if e3 < e1 or e3 < e5:
        return False

    e15 = (e1 + e5)/2
    e24 = (e2 + e4)/2
    return \
        _is_close_enough(e1, e15, delta) and \
        _is_close_enough(e5, e15, delta) and \
        _is_close_enough(e2, e24, delta) and \
        _is_close_enough(e4, e24, delta)


def _is_ihs(X, pv_points, cur, delta):
    """
    Return true if 'cur'這個點是一個反向頭肩頂(inverted head-and-shoulder)的pattern
    :param X: array of close price
    :param pv_points: pivot point, array of (index, direction)
    :param cur: 目前的點
    :param delta: E1/E5, E2/E4的容忍範圍
    :return:
    """
    if cur > len(pv_points) - 5:
        return False

    # TODO 可以把e1,e2,e3,e4,e5這幾個點之間的距離考慮進去

    # E1必須是個min
    _, direction = pv_points[cur]
    if direction != -1:
        return False

    # 接下來5個點的數值 = e1,e2,e3,e4,e5
    e1, e2, e3, e4, e5 = X[[p[0] for p in pv_points[cur:cur+5]]]

    # E3要比E1/E5低
    if e3 > e1 or e3 > e5:
        return False

    e15 = (e1 + e5)/2
    e24 = (e2 + e4)/2
    return \
        _is_close_enough(e1, e15, delta) and \
        _is_close_enough(e5, e15, delta) and \
        _is_close_enough(e2, e24, delta) and \
        _is_close_enough(e4, e24, delta)


def _is_double_bottom(X, pv_points, cur, delta):
    """
    Return true if 'cur'這個點是一個double-bottom的pattern
    :param X: array of close price
    :param pv_points: pivot point, array of (index, direction)
    :param cur: 目前的點
    :param delta: E2/E4的容忍範圍
    :return: True or False
    """
    if cur > len(pv_points) - 5:
        return False

    # E1必須是個max
    _, direction = pv_points[cur]
    if direction != 1:
        return False

    # 接下來5個點的數值 = e1,e2,e3,e4,e5
    e1, e2, e3, e4, e5 = X[[p[0] for p in pv_points[cur:cur+5]]]

    # E3要比E1/E5低
    if e3 > e1 or e3 > e5:
        return False

    # E2/E4要接近
    e24 = (e2 + e4)/2
    return \
        _is_close_enough(e2, e24, delta) and \
        _is_close_enough(e4, e24, delta)


def _is_double_top(X, pv_points, cur, delta):
    """
    Return true if 'cur'這個點是一個double-top的pattern
    :param X: array of close price
    :param pv_points: pivot point, array of (index, direction)
    :param cur: 目前的點
    :param delta: E2/E4的容忍範圍
    :return: True or False
    """
    if cur > len(pv_points) - 5:
        return False

    # E1必須是個max
    _, direction = pv_points[cur]
    if direction != 1:
        return False

    # 接下來5個點的數值 = e1,e2,e3,e4,e5
    e1, e2, e3, e4, e5 = X[[p[0] for p in pv_points[cur:cur+5]]]

    # E3要比E1/E5低
    if e3 > e1 or e3 > e5:
        return False

    # E2/E4要接近
    e24 = (e2 + e4)/2
    return \
        _is_close_enough(e2, e24, delta) and \
        _is_close_enough(e4, e24, delta)


class Finder(object):
    def __init__(self, klist):
        """
        Construct a PatternFinder object
        :param klist: array of KBlock
        """
        self.klist = klist
        self.X = kdata.get_close_nparray(klist)
        # self.pivots is an array of (VALLEY, 0, PEAK): 紀錄每一個點的屬性
        self.pivots = []
        # self.pv_points is an array of (index, DIR): 把PEAK/VALLEY points拉出來, 方便計算
        self.pv_points = []

    def init_pivots(self, thresh):
        """
        找出 zigzag points. 產出 self.pivots, 以及 self.pv_points
        :param thresh: The minimum relative change necessary to define a peak/valley
        :return:
        """
        up_thresh = thresh
        down_thresh = -1 * thresh
        initial_pivot = self._identify_initial_pivot(self.X, up_thresh, down_thresh)
        t_n = len(self.X)
        self.pivots = np.zeros(t_n, dtype='i1')
        self.pivots[0] = initial_pivot

        # Adding one to the relative change thresholds saves operations. Instead
        # of computing relative change at each point as x_j / x_i - 1, it is
        # computed as x_j / x_1. Then, this value is compared to the threshold + 1.
        # This saves (t_n - 1) subtractions.
        up_thresh += 1
        down_thresh += 1

        trend = -initial_pivot
        last_pivot_t = 0
        last_pivot_x = self.X[0]
        for t in range(1, len(self.X)):
            x = self.X[t]
            r = x / last_pivot_x

            if trend == -1:
                if r >= up_thresh:
                    self.pivots[last_pivot_t] = trend
                    trend = 1
                    last_pivot_x = x
                    last_pivot_t = t
                elif x < last_pivot_x:
                    last_pivot_x = x
                    last_pivot_t = t
            else:
                if r <= down_thresh:
                    self.pivots[last_pivot_t] = trend
                    trend = -1
                    last_pivot_x = x
                    last_pivot_t = t
                elif x > last_pivot_x:
                    last_pivot_x = x
                    last_pivot_t = t

        if last_pivot_t == t_n-1:
            self.pivots[last_pivot_t] = trend
        elif self.pivots[t_n-1] == 0:
            self.pivots[t_n-1] = -trend

        self.pv_points = [(i, self.pivots[i]) for i in np.arange(len(self.X))[self.pivots != 0]]

    def plot(self, pattern=[], width=12, height=9, filename=''):
        """
        Plot graph
        :param pattern: optional. array of index. 如果有傳的話, 則把這幾個點畫出連線(標示pattern)
        :param width: image width
        :param height: image height
        :param filename: optional. 如果有傳的話, 則render成png file
        :return:
        """
        size = (width, height)
        if filename:
            fig = Figure(figsize=size)
        else:
            fig = plt.figure(figsize=size)
        ax = fig.add_subplot(111)
        ax.set_xlim(-10, len(self.X)+10)
        ax.set_ylim(self.X.min()*0.99, self.X.max()*1.01)
        ax.plot(np.arange(len(self.X)), self.X, 'k:', alpha=0.7)
        ax.plot(np.arange(len(self.X))[self.pivots != 0], self.X[self.pivots != 0], 'k-')
        if len(pattern) > 0:
            y = [self.X[i] for i in pattern]
            ax.plot(pattern, y, color='b', linewidth=2)
            ax.scatter(pattern, y, color='r')
        if filename:
            canvas = FigureCanvasAgg(fig)
            canvas.print_png(filename)
        else:
            plt.show()

    def find_hs(self, delta=0.015):
        """
        搜尋 HS pattern (head-and-shoulder)
        :param delta: 頸線的誤差容忍值
        :return: array of patterns, 每一個pattern是一個array of index
        """
        patterns = []
        for i in range(len(self.pv_points)):
            if _is_hs(self.X, self.pv_points, i, delta):
                patterns.append([pt[0] for pt in self.pv_points[i:i+5]])
        return patterns

    def find_ihs(self, delta=0.015):
        """
        搜尋 IHS pattern (inverted-head-and-shoulder)
        :param delta: 頸線的誤差容忍值
        :return: array of patterns, 每一個pattern是一個array of index
        """
        patterns = []
        for i in range(len(self.pv_points)):
            if _is_ihs(self.X, self.pv_points, i, delta):
                patterns.append([pt[0] for pt in self.pv_points[i:i+5]])
        return patterns

    def find_double_bottom(self, delta=0.015):
        """
        搜尋 Double Bottom pattern
        :param delta: E2/E4的誤差容忍值
        :return: array of patterns, 每一個pattern是一個array of index
        """
        patterns = []
        for i in range(len(self.pv_points)):
            if _is_double_bottom(self.X, self.pv_points, i, delta):
                patterns.append([pt[0] for pt in self.pv_points[i:i+5]])
        return patterns

    def find_double_top(self, delta=0.015):
        """
        搜尋 Double Top pattern
        :param delta: E2/E4的誤差容忍值
        :return: array of patterns, 每一個pattern是一個array of index
        """
        patterns = []
        for i in range(len(self.pv_points)):
            if _is_double_top(self.X, self.pv_points, i, delta):
                patterns.append([pt[0] for pt in self.pv_points[i:i+5]])
        return patterns

    @staticmethod
    def _identify_initial_pivot(X, up_thresh, down_thresh):
        """Quickly identify the X[0] as a peak or valley."""
        x_0 = X[0]
        max_x = x_0
        max_t = 0
        min_x = x_0
        min_t = 0
        up_thresh += 1
        down_thresh += 1

        for t in range(1, len(X)):
            x_t = X[t]

            if x_t / min_x >= up_thresh:
                return VALLEY if min_t == 0 else PEAK

            if x_t / max_x <= down_thresh:
                return PEAK if max_t == 0 else VALLEY

            if x_t > max_x:
                max_x = x_t
                max_t = t

            if x_t < min_x:
                min_x = x_t
                min_t = t

        t_n = len(X)-1
        return VALLEY if x_0 < X[t_n] else PEAK


# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Ref:
- https://github.com/jbn/ZigZag
- http://www.investopedia.com/ask/answers/030415/what-zig-zag-indicator-formula-and-how-it-calculated.asp

尋找歷史股價的zigzag轉折線
"""
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

PEAK, VALLEY = 1, -1


def plot_zigzag(X, pivots, filename=''):
    size = (12, 9)
    if filename:
        fig = Figure(figsize=size)
    else:
        fig = plt.figure(figsize=size)
    ax = fig.add_subplot(111)
    ax.set_xlim(-10, len(X)+10)
    ax.set_ylim(X.min()*0.99, X.max()*1.01)
    ax.plot(np.arange(len(X)), X, 'k:', alpha=0.7)
    ax.plot(np.arange(len(X))[pivots != 0], X[pivots != 0], 'k-')
    ax.scatter(np.arange(len(X))[pivots == 1], X[pivots == 1], color='g')
    ax.scatter(np.arange(len(X))[pivots == -1], X[pivots == -1], color='r')
    if filename:
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(filename)
    else:
        plt.show()


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


def peak_valley_pivots(X, up_thresh, down_thresh):
    """
    Finds the peaks and valleys of a series.

    Parameters
    ----------
    X : This is your series.
    up_thresh : The minimum relative change necessary to define a peak.
    down_thesh : The minimum relative change necessary to define a valley.

    Returns
    -------
    an array with 0 indicating no pivot and -1 and 1 indicating valley and peak
    respectively

    Using Pandas
    ------------
    For the most part, X may be a pandas series. However, the index must
    either be [0,n) or a DateTimeIndex. Why? This function does X[t] to access
    each element where t is in [0,n).

    The First and Last Elements
    ---------------------------
    The first and last elements are guaranteed to be annotated as peak or
    valley even if the segments formed do not have the necessary relative
    changes. This is a tradeoff between technical correctness and the
    propensity to make mistakes in data analysis. The possible mistake is
    ignoring data outside the fully realized segments, which may bias analysis.
    """
    if down_thresh > 0:
        raise ValueError('The down_thresh must be negative.')

    initial_pivot = _identify_initial_pivot(X, up_thresh, down_thresh)

    t_n = len(X)
    pivots = np.zeros(t_n, dtype='i1')
    pivots[0] = initial_pivot

    # Adding one to the relative change thresholds saves operations. Instead
    # of computing relative change at each point as x_j / x_i - 1, it is
    # computed as x_j / x_1. Then, this value is compared to the threshold + 1.
    # This saves (t_n - 1) subtractions.
    up_thresh += 1
    down_thresh += 1

    trend = -initial_pivot
    last_pivot_t = 0
    last_pivot_x = X[0]
    for t in range(1, len(X)):
        x = X[t]
        r = x / last_pivot_x

        if trend == -1:
            if r >= up_thresh:
                pivots[last_pivot_t] = trend
                trend = 1
                last_pivot_x = x
                last_pivot_t = t
            elif x < last_pivot_x:
                last_pivot_x = x
                last_pivot_t = t
        else:
            if r <= down_thresh:
                pivots[last_pivot_t] = trend
                trend = -1
                last_pivot_x = x
                last_pivot_t = t
            elif x > last_pivot_x:
                last_pivot_x = x
                last_pivot_t = t

    if last_pivot_t == t_n-1:
        pivots[last_pivot_t] = trend
    elif pivots[t_n-1] == 0:
        pivots[t_n-1] = -trend

    return pivots


def compute_segment_returns(X, pivots):
    """Return a numpy array of the pivot-to-pivot returns for each segment."""
    pivot_points = X[pivots != 0]
    return pivot_points[1:] / pivot_points[:-1] - 1.0


def max_drawdown(X):
    """
    Return the absolute value of the maximum drawdown of sequence X.

    Note
    ----
    If the sequence is strictly increasing, 0 is returned.
    """
    mdd = 0
    peak = X[0]
    for x in X:
        if x > peak:
            peak = x
        dd = (peak - x) / peak
        if dd > mdd:
            mdd = dd
    return mdd


def pivots_to_modes(pivots):
    """
    Translate pivots into trend modes.

    Parameters
    ----------
    pivots : the result of calling peak_valley_pivots

    Returns
    -------
    A numpy array of trend modes. That is, between (VALLEY, PEAK] it is 1 and
    between (PEAK, VALLEY] it is -1.
    """
    modes = np.zeros(len(pivots), dtype='i1')
    modes[0] = pivots[0]
    mode = -modes[0]
    for t in range(1, len(pivots)):
        x = pivots[t]
        if x != 0:
            modes[t] = mode
            mode = -x
        else:
            modes[t] = mode
    return modes
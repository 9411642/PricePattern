# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import date
import numpy as np
import sys
sys.path.insert(0, '..')
from pp import kdata, zigzag

if __name__ == "__main__":
    kdatasvc = kdata.KDataSvc("203.67.19.12")
    klist = kdatasvc.getdata("2330.TW", 8, date(2014, 1, 1), date(2015, 12, 31))
    X = kdatasvc.klist_to_nparray(klist)
    pivots = zigzag.peak_valley_pivots(X, 0.03, -0.03)
    zigzag.plot_zigzag(X, pivots, 'zigzag.png')

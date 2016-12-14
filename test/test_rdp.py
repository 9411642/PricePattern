# -*- coding: utf-8 -*-
from datetime import date
import sys
sys.path.insert(0,'..')
from pp import rdp, kdata

if __name__ == "__main__":
    kdatasvc = kdata.KDataSvc("203.67.19.12")
    klist = kdatasvc.getdata("2330.TW", 8, date(2014, 1, 1), date(2015, 12, 31))
    r = rdp.RDP(klist, 3)
    r.show()

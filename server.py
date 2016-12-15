# -*- coding: utf-8 -*-
"""
    HTTP Web Server entry point

    To run the server:
    $ PORT=6060 python server.py
"""
from __future__ import print_function
from bottle import route, run, request, response, abort, static_file
from datetime import datetime, date
import os
import logging
import traceback
import tempfile
import numpy as np
from pp import rdp, kdata, zigzag


@route('/')
def default_static():
    return static_file("default.html", root=static_folder)


@route('/<filename>')
def server_static(filename):
    return static_file(filename, root=static_folder)


@route('/api/rdp')
def handle_rdp():
    """
    http://<server>/api/rdp?id=2330.TW&start=20100101&end=20151231&eps=5
    """
    try:
        sid, start_date, end_date, eps = get_param(request)
        logging.debug('sid=' + sid + ',start_date=' + str(start_date) + ',end_date=' + str(end_date) + ',eps=' + str(eps))
        klist = kdatasvc.getdata(sid, 8, start_date, end_date)
        r = rdp.RDP(klist, eps)
        png_file = get_temp_file()
        r.render_png(png_file)
        return static_file(png_file, root="/", mimetype="image/png")
    except Exception as e:
        logging.error(traceback.format_exc())
        abort(500, e.message)


@route('/api/zigzag')
def handle_zigzag():
    """
    http://<server>/api/zigzag?id=2330.TW&start=20100101&end=20151231&eps=5
    """
    try:
        sid, start_date, end_date, eps = get_param(request)
        logging.debug('sid=' + sid + ',start_date=' + str(start_date) + ',end_date=' + str(end_date) + ',eps=' + str(eps))
        klist = kdatasvc.getdata(sid, 8, start_date, end_date)
        X = kdatasvc.klist_to_nparray(klist)
        pivots = zigzag.peak_valley_pivots(X, eps * 0.01, eps * -0.01)
        png_file = get_temp_file()
        zigzag.plot_zigzag(X, pivots, png_file)
        return static_file(png_file, root="/", mimetype="image/png")
    except Exception as e:
        logging.error(traceback.format_exc())
        abort(500, e.message)


def get_param(req):
    sid = req.query.id or ''
    if not sid:
        raise ValueError('missing id parameter')
    today = date.today()
    default_start_date = date(today.year - 2, today.month, today.day)
    start_date = parse_date(req.query.start or '', default_start_date)
    end_date = parse_date(req.query.end or '', today)
    eps = int(req.query.eps or '5')
    return sid, start_date, end_date, eps


def parse_date(dt, def_value):
    try:
        return datetime.strptime(dt, "%Y%m%d").date()
    except:
        return def_value


def get_temp_file():
    tf = tempfile.NamedTemporaryFile()
    temp_file_name = tf.name
    tf.close()
    return temp_file_name

try:
    port = int(os.getenv('PORT', '6060'))
    kdatasvc = kdata.KDataSvc("203.67.19.12")
    static_folder = os.path.join(os.path.dirname(__file__), "web")
except:
    port = 6060

run(port=port, debug=True)

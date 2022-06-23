from __future__ import print_function
import os
import io
import uuid
import urllib
import json
import time
import random
from base64 import urlsafe_b64encode, urlsafe_b64decode
import threading
import Queue
from datetime import datetime, timedelta
import pytz
from BTrees import OOBTree
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.utils import timezone
from django.contrib.staticfiles.templatetags.staticfiles import static as reverse_static_url
from django.core.urlresolvers import reverse as reverse_url
from django.views.static import serve as static_serve
from django.utils.safestring import mark_safe
from fatcat.conf import settings as _settings
from fdstock import time_utils
from fdstock.networking import NetManager

net_mgr = NetManager.get_inst()


TZ_TW = pytz.timezone("Asia/Taipei")
def timestamp_to_datetime(ts):
  dt = datetime.fromtimestamp(ts).replace(tzinfo=pytz.utc)
  dt2 = dt.astimezone(TZ_TW)
  return dt2

def equity_list_view(request):
  with net_mgr.db_cli_pool.connection() as db_cli:
    objs = []
    items = db_cli.call('ALL_EQUITY', None)
    for info in items:

      objs.append(info)
    
  return TemplateResponse(request, "equity_list.html", {
    "objs": objs,
  })

def index(request):
  results = []
  return TemplateResponse(request, "index.html", {
    "results": results,
  })

def timeline_view(request):
  code = request.GET['code']
  with net_mgr.twseix_cli_pool.connection() as twseix_cli:

    now = ts_to_tz_tw(time.time())
    end = now
    start = end - timedelta(days=2)

    start_t = int(start.strftime('%Y%m%d%H%M%S'))
    end_t = int(end.strftime('%Y%m%d%H%M%S'))

    #rtn = cli.call('TIMELINE_ITEMS', None, '2330', start_t, end_t)[0]
    rtn = twseix_cli.call('TIMELINE_ITEMS', code, start_t, end_t)[0]
    print('TIMELINE_ITEMS', code, start_t, end_t, 'rtn', rtn)
    counter = 0
    objs = []
    for info in rtn:
      counter += 1
      uts = int(info['tlong'])
      ts = uts / 1000.0
      dt = ts_to_tz_tw(ts)
      print(counter, 'uts', uts, dt)
      info['time_desc'] = dt.strftime('%Y-%m-%d %H:%M:%S')
      objs.append(info)

  return TemplateResponse(request, "timeline.html", {
    "objs": objs,
  })

def bc_view(request):
  code = request.GET['s']
  date = request.GET['date']

  data_points = []

  date_desc = ''

  
  with net_mgr.db_cli_pool.connection() as db_cli:
    with net_mgr.twseix_cli_pool.connection() as twseix_cli:
      equity = db_cli.call('GET_EQUITY', code)[0]
      if equity is not None:
        now = time_utils.ts_to_tz_tw(time.time())

        year = date[0:4]
        month = date[4:6]
        day = date[6:8]

        date_desc = '%s-%s-%s' % (year, month, day)

        start_key = int('%s0000' % date)
        end_key = int('%s2359' % date)

        #rtn = cli.call('TIMELINE_ITEMS', None, '2330', start_t, end_t)[0]
        items = twseix_cli.call('ITEMS_STOCK_MINUTE_DATA', code, start_key, end_key)[0]
        print('ITEMS_STOCK_MINUTE_DATA', code, start_key, end_key, 'items', len(items))
        for item in items:
          tkey0 = item['tkey']

          dt = time_utils.ixtime_to_tz_tw(tkey0)
          print('tkey0', tkey0, 'dt', dt, 'items',item)

          trade_volume = item['total_trade_volume']
          last_trade_price = item['last_trade_price']

          time_label = dt.strftime('%H:%M')
          point = {'y': last_trade_price, 'label': time_label}
          print('point', point)

          data_points.append(point)



  return TemplateResponse(request, 'bc.html', {
    'equity': equity,
    'date_desc': date_desc,
    'data_points': mark_safe(json.dumps(data_points)),
  })


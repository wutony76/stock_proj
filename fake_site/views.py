from __future__ import print_function
import random
import re
from datetime import datetime
import json
from BTrees import OOBTree
from django.http import HttpResponse, JsonResponse
from fdstock.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw
from fake_site.dataset import DataSet




dataset = DataSet()

def index(request):
  return HttpResponse('')

def get_stock_info_view(request):
  ex_ch = request.GET['ex_ch']
  uts = int(request.GET['_'])
  print('get_stock_info', ex_ch, uts)
  a = re.search('tse_(\w+).tw', ex_ch)
  code = a.group(1)


  data = dataset.gen_stock_info(code, uts)



  ctx = {
    'msgArray':[data],
    "referer":"","userDelay":5000,"rtcode":"0000","queryTime":{"sysDate":"20210901","stockInfoItem":1535,"stockInfo":101062,"sessionStr":"UserSession","sysTime":"16:32:03",
    "showChart":False,"sessionFromTime":-1,"sessionLatestTime":-1},"rtmessage":"OK","exKey":"if_tse_2330.tw_zh-tw.null","cachedAlive":14261
  }
  
  #return HttpResponse(json.dumps(ctx), content_type='text/html;charset=UTF-8')
  return HttpResponse(json.dumps(ctx, ensure_ascii=False))

#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import random
import re
import requests
import time
from datetime import datetime
import json
from BTrees import OOBTree
import collections


from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse as reverse_url
#from django.shortcuts import render, redirect

from fdstock.rpcclient import RPCClientPool
from fcworks.conf import settings as _settings
#from fatcat.conf import settings as _settings
from fdstock.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw
from get_tw50_list import start_get_tw50_list
from get_tw50_info import start_get_tw50_infos

#from get_ig_info import start_get_exponent_info
#from yfaDict import IG_EXPONENT 


db_cli_pool = RPCClientPool(_settings.FDSTOCK_YFA_DB_ADDR)
#########################################################

def tw50_list(request):
  #print("tw50_list")
  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('TW50_LIST')
    #print('TW50_LIST', len(rtn))
    #print("rtn", rtn)
    
  rtn2 = []
  if len(rtn) > 0:
    for r in rtn:
      d = {}
      d['code'] = r.get(b'code').decode()
      d['name'] = r.get(b'name').decode()
      rtn2.append(d)

  return TemplateResponse(request, 'stock/tw50_list.html', {
    'len':len(rtn),
    'rtn':rtn2,
  })


def update_tw50_list(request):
  #print("update_tw50_list")
  tw50_list = start_get_tw50_list()
  t0 = time.time()
  with db_cli_pool.connection() as db_cli: 
    call_args=[]
    for _stock in tw50_list:
      code, name = _stock
      info = {
        'code':code,
        'name':name,
        'active': True,
      }
      call_args.append(int(code))
      call_args.append(info)
    print('call_args', call_args, len(call_args))
    rtn = db_cli.call('UPDATE_TW50_LIST', *call_args)
    print('UPDATE_TW50_LIST', rtn)
  dt = time.time() - t0

  return HttpResponse( 'get tw50 list: %s' % dt )



  


def tw50_info(request):
  stock_code = request.GET['code']
  #print('stock_code', stock_code)
  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('TW50_INFO', stock_code)
    #print("TW50_INFO", rtn)
    data_uts = []
    data_volume = []
    rtn.reverse()
  #return HttpResponse('stock info.') 
  print ( rtn )
  rtn2 = []
  if len(rtn) > 0:
    for r in rtn:
      d = {}
      d['code'] = r.get(b'code').decode()
      d['time'] = r.get(b'time').decode()
      d['value'] = r.get(b'value')
      d['uts'] = int(r.get(b'uts'))
      d['timestamp'] = int(r.get(b'timestamp'))
      rtn2.append(d)


  return TemplateResponse(request, 'stock/tw50_info.html', {
    'code':stock_code,
    'rtn':rtn2,

    'data_date':data_uts,
    'data_volume':data_volume,
    #'dataPoints': dataPoints
  })

#https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1m&mkt=10&sym=1101&callback=jQuery111305285216738598696_1634200372625&_=1634200372626
#--refresh all tw50 info--#
def update_tw50_info(request):
  #print('update_tw50_info')
  try:
    q = request.GET['q']  
  except:
    q = None
  t0 = time.time()
  with db_cli_pool.connection() as db_cli:
    tw50_list_keys = db_cli.call('TW50_LIST_KEY')
    #print("tw50_list_keys", tw50_list_keys, len(tw50_list_keys))
    #print("tw50_list_keys", tw50_list_keys, len(tw50_list_keys))

    count = int(len(tw50_list_keys)/5)
    for i in range(count):
      _s = i*5
      _e = _s+5
      ##print ("i =", i, tw50_list_keys[_s:_e])
      code_sample = tw50_list_keys[_s:_e]
      _info_list = start_get_tw50_infos(code_sample)

      call_args = []
      for item in _info_list:
        _code = item['code']
        call_args.append(_code)
        call_args.append(item)
      #print ("call_args =", call_args)
      with db_cli_pool.connection() as db_cli:
        rtn = db_cli.call('UPDATE_TW50_INFO', *call_args)
        #print('UPDATE_TWSE_EXPONENT_INFO', rtn)
  dt = time.time() - t0
  return HttpResponse("update_tw50_info %s" % dt)
########################################################



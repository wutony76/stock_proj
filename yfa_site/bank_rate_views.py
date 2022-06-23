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
#from django.core.urlresolvers import reverse as reverse_url
#from django.shortcuts import render, redirect

from fdstock.rpcclient import RPCClientPool
from fcworks.conf import settings as _settings
from fdstock.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw
from get_bank_rate import start_get_bank_rate_list

#from get_ig_info import start_get_exponent_info
from yfaDict import BANK_RATE


db_cli_pool = RPCClientPool(_settings.FDSTOCK_YFA_DB_ADDR)
#########################################################



def bank_rate_list(request):
  rtn = BANK_RATE 
  return TemplateResponse(request, 'stock/bank_rate_list.html', {
    'len':len(rtn),
    'rtn':rtn,
  })


def bank_rate_info(request):
  stock_code = request.GET['code']
  #print('stock_code', stock_code)
  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('BANK_INFO', stock_code)
    print("BANK_INFO", rtn)
    data_uts = []
    data_volume = []
    rtn.reverse()
  #return HttpResponse('stock info.') 
  rtn2 = []
  if len(rtn)> 0:
    for r in rtn:
      print("r", r)
      d = {}
      d['uts'] = int(r.get(b'uts'))
      d['ts'] = int(r.get(b'timestamp'))
      d['code'] = r.get(b'code').decode()
      d['buy_value'] = r.get(b'buy_value').decode()
      d['sell_value'] = r.get(b'sell_value').decode()
      rtn2.append(d)


  return TemplateResponse(request, 'stock/bank_info.html', {
    'code':stock_code,
    'rtn':rtn2,

    'data_date':data_uts,
    'data_volume':data_volume,
    #'dataPoints': dataPoints
  })

#--refresh all bank_taiwan info--#
def update_bank_rate_info(request):
  try:
    q = request.GET['q']  
  except:
    q = None
  t0 = time.time()
  with db_cli_pool.connection() as db_cli:
    #code_sample = tw50_list_keys[_s:_e]

    sample = ["0040000"] #bank_taiwan
    _info_list = start_get_bank_rate_list(sample)
    #print ("_info_list =", _info_list)
    call_args = []
    for item in _info_list:
      _code = item['code']
      call_args.append(_code)
      call_args.append(item)

    #print ("call_args =", call_args)
    with db_cli_pool.connection() as db_cli:
      rtn = db_cli.call('UPDATE_BANK_INFO', *call_args)
      #print('UPDATE_TWSE_EXPONENT_INFO', rtn)

  dt = time.time() - t0
  return HttpResponse("update_bank_rate_info %s" % dt)
########################################################



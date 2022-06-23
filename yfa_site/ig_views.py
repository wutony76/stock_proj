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
#from fatcat.conf import settings as _settings

from fdstock.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw
from fake_site.dataset import DataSet


from get_ig_info import start_get_exponent_info
from yfaDict import IG_EXPONENT 


dataset = DataSet()
db_cli_pool = RPCClientPool(_settings.FDSTOCK_YFA_DB_ADDR)





#########################################################

def ig_exponent_list(request):
  #twse_exponent = TWSE_EXPONENT
  #other_twse_exponent = OTHER_EXPONENT 
  #twse_exponent = collections.OrderedDict(sorted(twse_exponent.items()))
  ig_exponent = IG_EXPONENT

  return TemplateResponse(request, 'stock/ig_exponent_list.html', {
    'len':len(ig_exponent),
    'rtn':ig_exponent,
  })



def ig_exponent_info(request):
  exponent_code = request.GET['code']  
  print('exponent_code', exponent_code)

  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('TWSE_EXPONENT_INFO', exponent_code)
    print("TWSE_EXPONENT_INFO", rtn)

    data_uts = []
    data_volume = []

    #for r in rtn[-20:]:
    #  if r['volume'] is not None:
    #    data_uts.append( int( r['uts'] )*1000 )
    #    data_volume.append(r['volume'])
    rtn.reverse()
    #rtn = rtn[:50]

  #return HttpResponse('stock info.') 
  return TemplateResponse(request, 'stock/ig_exponent_info.html', {
    'code':exponent_code,
    'rtn':rtn,

    'data_date':data_uts,
    'data_volume':data_volume,
    #'dataPoints': dataPoints
  })


#--refresh all twse exponent info--#
def update_ig_exponent_info(request):
  print('update_ig_exponent_info')

  t0 = time.time()
  with db_cli_pool.connection() as db_cli:
    print('db_cli', db_cli)
    _info_list = start_get_exponent_info()
    call_args = []
    for item in _info_list:
      _code = item['code']
      call_args.append(_code)
      call_args.append(item)
      
    #print ("call_args =", call_args)
    with db_cli_pool.connection() as db_cli:
      rtn = db_cli.call('UPDATE_TWSE_EXPONENT_INFO', *call_args)
      #print('UPDATE_TWSE_EXPONENT_INFO', rtn)
  dt = time.time() - t0

  return HttpResponse("update_ig_exponent_info %s" % dt)

########################################################



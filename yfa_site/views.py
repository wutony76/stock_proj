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
from fake_site.dataset import DataSet


from get_list import start_get_twse_list
from get_exponent_list import start_get_exponent_list
from get_exponent_info import start_get_exponent_info
from get_exponent_info2 import start_get_exponent_info as get_twse_exponent_info
from get_exponent_info2_other import start_get_exponent_info as get_twse_exponent_info_other
from get_exponent_info2_eftri import start_get_exponent_info as get_twse_exponent_info_eftri
from get_exponent_info2_yahoo import start_get_yahoo_exponent_infos
from get_exponent_info2_yahoo1 import start_get_yahoo_exponent_infos as start_get_yahoo_exponent_infos1
from get_exponent_info2_yahoo2 import start_get_yahoo_exponent_infos as start_get_yahoo_exponent_infos2
from get_exponent_info2_yahoo3 import start_get_yahoo_exponent_infos as start_get_yahoo_exponent_infos3
from get_exponent_info2_yahoo4 import start_get_yahoo_exponent_infos as start_get_yahoo_exponent_infos4
from get_exponent_info2_yahoo5 import start_get_yahoo_exponent_infos as start_get_yahoo_exponent_infos5
#from get_exponent_info2_yahoo import start_get_yahoo_exponent_infos
from yfa_site.networking import RPCHttpClient
from yfa_site import yfaDict


from yfaDict import TWSE_EXPONENT, OTHER_EXPONENT, EFTRI_EXPONENT


dataset = DataSet()
db_cli_pool = RPCClientPool(_settings.FDSTOCK_YFA_DB_ADDR)

def index(request):
  return TemplateResponse(request, 'index.html', { })
  #return HttpResponse('')




#--stock list--#
def stock_list(request):
  print("stock_list")
  with db_cli_pool.connection() as db_cli:
    print('db_cli', db_cli)
    rtn = db_cli.call('STOCK_CODE')
    print('STOCK_CODE', len(rtn))

  return TemplateResponse(request, 'stock/list.html', {
    "len" : len(rtn),
    "rtn" : rtn
  })


#--refresh stock list--#
def get_stock_list(request):
  print("get_stock_list")
  new_stack_list_info = start_get_twse_list() 
  #print("new_stack_list_info - ", new_stack_list_info)

  call_args = []
  for k, v in new_stack_list_info.items():
    #print("info - ", "%s - %s"%(k, v))
    info = {
      'code':k,
      'name':v,
    }
    call_args.append(k)
    call_args.append(info)
  print("len - ", len(new_stack_list_info) )

  with db_cli_pool.connection() as db_cli:
    #pass
    rtn = db_cli.call('UPDATE_STOCK_CODE', *call_args)
    print('UPDATE_STOCK_CODE', rtn)

  #return HttpResponse('is stock refresh success.') 
  return HttpResponseRedirect( reverse_url("stock_list") )


#--stock info--#
def stock_info(request):
  stock_code = request.GET['code']  
  print('stock_code', stock_code)

  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('STOCK_INFO', int(stock_code))
    print("STOCK_INFO", rtn)

    data_uts = []
    data_volume = []
    #dataPoints = []
    for r in rtn[-20:]:
      if r['volume'] is not None:
        #_data = {}
        #_data["x"] = ts_to_tz_tw( r['uts'] ).strftime("%m%d")
        #_data["y"] = r['volume']
        #dataPoints.append( _data )
        #data_uts.append( int(ts_to_tz_tw( r['uts'] ).strftime("%Y%m%d")) )
        data_uts.append( int( r['uts'] )*1000 )
        data_volume.append(r['volume'])
    rtn.reverse()
    rtn = rtn[:50]

  #return HttpResponse('stock info.') 
  return TemplateResponse(request, 'stock/info.html', {
    'code':stock_code,
    'rtn':rtn,

    'data_date':data_uts,
    'data_volume':data_volume,
    #'dataPoints': dataPoints
  })

#--refresh stock info--#
def get_stock_info(request):
  stock_code = request.GET['code']  
  print('stock_code', stock_code)

  target = '%s.TW'%stock_code
  url = 'https://query1.finance.yahoo.com/v8/finance/chart/%s' % target
  #print ('get url -',url)
  uts = int(time.time())

  req_data = {
    #'ex_ch': 'tse_%s.tw' % eq_code,
    #'_': uts,
    #'period1':0,
    'period1':946656000, #2000-1-1 0:0:0
    'period2':uts,
    'interval':'1d',
    'events':'history',
    '':uts,
  }
  #print ('req_data -',req_data)
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
  rep = requests.get(url, params=req_data, headers=headers)
  print ('status_code -',rep.status_code)

  if rep.status_code != 200:
    return HttpResponse("get is Errors")

  content = rep.content
  item = parse_timeline_item (content)
  #print("item ", item)
  print("item ", len(item))

  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('UPDATE_STOCK_INFO', *item)
    print("UPDATE_STOCK_INFO", rtn)
    
  #return HttpResponse('stock info.') 
  return HttpResponseRedirect( reverse_url("stock_info")+"?code="+stock_code )



#--refresh all stock info--#
def update_stock_info(request):
  print('update_stock_info')

  with db_cli_pool.connection() as db_cli:
    print('db_cli', db_cli)
    rtn = db_cli.call('STOCK_CODE')
    print('STOCK_CODE', len(rtn))
    print('STOCK_CODE', rtn)
    for r in rtn:
      #print(r['code'])
      stock_code = r['code']
      target = '%s.TW'%stock_code
      url = 'https://query1.finance.yahoo.com/v8/finance/chart/%s' % target
      uts = int(time.time())
      req_data = {
        'period1':946656000, #2000-1-1 0:0:0
        'period2':uts,
        'interval':'1d',
        'events':'history',
        '':uts,
      }
      headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
      rep = requests.get(url, params=req_data, headers=headers)
      print ('status_code -',rep.status_code)

      if rep.status_code != 200:
        return HttpResponse("get is Errors")
      content = rep.content

      try:
        print("content ", content)
        item = parse_timeline_item (content)
        #print("item ", len(item))
        with db_cli_pool.connection() as db_cli:
          rtn = db_cli.call('UPDATE_STOCK_INFO', *item)
          print("UPDATE_STOCK_INFO", rtn)
      except:
        pass

  return HttpResponse("update_stock_info")



########################################################
#-- exponent list --#
def exponent_list(request):
  print("exponent_list")
  with db_cli_pool.connection() as db_cli:
    print('db_cli', db_cli)
    rtn = db_cli.call('EXPONENT_CODE')
    print('EXPONENT_CODE', len(rtn))

  return TemplateResponse(request, 'stock/exponent_list.html', {
    "len" : len(rtn),
    "rtn" : rtn
  })


#--refresh exponent list--#
def get_exponent_list(request):
  print("exponent_list")
  new_exponent_list = start_get_exponent_list()
  call_args = []
  for item in new_exponent_list:
    _code = item['c']
    _name = item['n']
    info = {
      'code':_code,
      'name':_name,
    }
    call_args.append(_code)
    call_args.append(info)

  print("len - ", len(new_exponent_list) )
  print("len - ", call_args )

  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('UPDATE_EXPONENT_CODE', *call_args)
    print('UPDATE_EXPONENT_CODE', rtn)

  return HttpResponseRedirect( reverse_url("exponent_list") )



#-- exponent info --#
#指數
def exponent_info(request):
  exponent_code = request.GET['code']  
  print('exponent_code', exponent_code)

  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('EXPONENT_INFO', exponent_code)
    print("EXPONENT_INFO", rtn)

    data_uts = []
    data_volume = []

    #for r in rtn[-20:]:
    #  if r['volume'] is not None:
    #    data_uts.append( int( r['uts'] )*1000 )
    #    data_volume.append(r['volume'])
    rtn.reverse()
    #rtn = rtn[:50]

  #return HttpResponse('stock info.') 
  return TemplateResponse(request, 'stock/exponent_info.html', {
    'code':exponent_code,
    'rtn':rtn,

    'data_date':data_uts,
    'data_volume':data_volume,
    #'dataPoints': dataPoints
  })


#--refresh exponent info--#
def get_exponent_info(request):
  exponent_code = request.GET['code']  
  print('exponent_code', exponent_code)
  _info_list = start_get_exponent_info(exponent_code)
  call_args = []
  for item in _info_list:
    _code = item['code']
    call_args.append(_code)
    call_args.append(item)

  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('UPDATE_EXPONENT_INFO', *call_args)
    print('UPDATE_EXPONENT_INFO', rtn)
  return HttpResponseRedirect( reverse_url("exponent_info")+"?code="+exponent_code )


#--refresh all stock info--#
def update_exponent_info(request):
  print('update_exponent_info')
  with db_cli_pool.connection() as db_cli:
    print('db_cli', db_cli)
    rtn = db_cli.call('EXPONENT_CODE')
    print('EXPONENT_CODE', len(rtn))
    for r in rtn:
      exponent_code = r['code']
      _info_list = start_get_exponent_info(exponent_code)
      call_args = []
      for item in _info_list:
        _code = item['code']
        call_args.append(_code)
        call_args.append(item)

      with db_cli_pool.connection() as db_cli:
        rtn = db_cli.call('UPDATE_EXPONENT_INFO', *call_args)
        print('UPDATE_EXPONENT_INFO', rtn)

  return HttpResponse("update_exponent_info")




#########################################################
def twse_exponent_list(request):
  twse_exponent = TWSE_EXPONENT
  other_twse_exponent = OTHER_EXPONENT 

  twse_exponent = collections.OrderedDict(sorted(twse_exponent.items()))
  return TemplateResponse(request, 'stock/twse_exponent_list.html', {
    'len':len(twse_exponent),
    'rtn':twse_exponent,
    'rtn2':other_twse_exponent,
    'rtn3': collections.OrderedDict(sorted(EFTRI_EXPONENT.items())),
  })


# --5秒指數統計
def twse_exponent_info(request):
  exponent_code = request.GET['code']  
  print('exponent_code', exponent_code)

  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('TWSE_EXPONENT_INFO', exponent_code)
    #print("TWSE_EXPONENT_INFO", rtn)

    data_uts = []
    data_volume = []

    #for r in rtn[-20:]:
    #  if r['volume'] is not None:
    #    data_uts.append( int( r['uts'] )*1000 )
    #    data_volume.append(r['volume'])
    rtn.reverse()
    #rtn = rtn[:50]

  rtn2 = []
  if len(rtn)>0:
    for r in rtn:
      print("r", r)
      d={}
      d['uts'] = int(r.get(b"uts"))
      d['timestamp'] = int(r.get(b"timestamp"))
      d['code'] = r.get(b"code").decode()
      d['time'] = r.get(b"time").decode()
      d['value'] = r.get(b"value")
      print("d", d)
      rtn2.append(d)


  #return HttpResponse('stock info.') 
  return TemplateResponse(request, 'stock/twse_exponent_info.html', {
    'code':exponent_code,
    'rtn':rtn2,

    'data_date':data_uts,
    'data_volume':data_volume,
    #'dataPoints': dataPoints
  })


#--refresh all twse exponent info--#
def update_twse_exponent_info(request):
  print('update_twse_exponent_info')
  t0 = time.time()
  with db_cli_pool.connection() as db_cli:
    print('db_cli', db_cli)
    _info_list = get_twse_exponent_info()

    call_args = []
    for item in _info_list:
      _code = item['code']
      call_args.append(_code)
      call_args.append(item)

    with db_cli_pool.connection() as db_cli:
      rtn = db_cli.call('UPDATE_TWSE_EXPONENT_INFO', *call_args)
      #print('UPDATE_TWSE_EXPONENT_INFO', rtn)

  dt = time.time() - t0
  return HttpResponse("update_twse_exponent_info %s" % dt)



def update_yahoo_exponent_info(request):
  try:
    q = request.GET['q']  
  except:
    q = None

  print('update_yahoo_exponent_info')
  t0 = time.time()

  ### stock ###
  _info_list = start_get_yahoo_exponent_infos1()
  
  call_args = []
  for item in _info_list:
    _code = item['code']
    call_args.append(_code)
    call_args.append(item)
    
  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('UPDATE_TWSE_EXPONENT_INFO', *call_args)
    print('UPDATE_TWSE_EXPONENT_INFO', rtn)
  #cli = RPCHttpClient(_settings.FDSTOCK_YFA_WORKER_HTTP)
  #sample_dict = yfaDict.YAHOO_EXPONENT
  #all_keys = sorted(sample_dict.keys())
  #print (all_keys)

  #if q == "1": 
  #  keys = all_keys[0:8] 
  #elif q == "2": 
  #  keys = all_keys[8:16] 
  #elif q == "3": 
  #  keys = all_keys[16:24] 
  #elif q == "4": 
  #  keys = all_keys[24:32] 
  #elif q == "5": 
  #  keys = all_keys[32:]
  #else:
  #  keys = all_keys

  #_info_list = get_twse_exponent_info()
  #cli = RPCHttpClient(_settings.FDSTOCK_YFA_WORKER_HTTP)
  #call_args = []

  #for k in keys:
  #  v = sample_dict[k]
  #  print("start_get_yahoo_exponent_infos>>", k, v["yahoo_url"])
  #  call_args.append(k)
  #  call_args.append(v["yahoo_url"])

  
  #t0 = time.time()
  dt = time.time() - t0
  return HttpResponse("update_yahoo_exponent_info %s" % dt)


  
  #print("ttt call_args ", call_args)
  t0 = time.time()
  rtn = cli.call("GET_YAHOO", *call_args)
  dt = time.time() - t0
  print("GET_YAHOO dt", dt)

  call_args = []
  for item in rtn:
    _code = item['code']
    item["_update_ts"] = time.time()

    call_args.append(_code)
    call_args.append(item)
    #print("RTN", item)

  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('UPDATE_TWSE_EXPONENT_INFO', *call_args)
    #print('UPDATE_TWSE_EXPONENT_INFO', rtn)

  dt = time.time() - t0
  return HttpResponse("update_yahoo_exponent_info %s" % dt)




def update_yahoo_exponent_info2(request):
  try:
    q = request.GET['q']  
  except:
    q = None

  print('update_yahoo_exponent_info2')
  t0 = time.time()
  cli = RPCHttpClient(_settings.FDSTOCK_YFA_WORKER_HTTP2)

  sample_dict = yfaDict.YAHOO_EXPONENT
  all_keys = sorted(sample_dict.keys())
  print (all_keys)

  if q == "1": 
    keys = all_keys[0:8] 
  elif q == "2": 
    keys = all_keys[8:16] 
  elif q == "3": 
    keys = all_keys[16:24] 
  elif q == "4": 
    keys = all_keys[24:32] 
  elif q == "5": 
    keys = all_keys[32:]
  else:
    keys = all_keys

  #_info_list = get_twse_exponent_info()
  cli = RPCHttpClient(_settings.FDSTOCK_YFA_WORKER_HTTP2)
  call_args = []

  for k in keys:
    v = sample_dict[k]
    #print("start_get_yahoo_exponent_infos>>", k, v["yahoo_url"])
    call_args.append(k)
    call_args.append(v["yahoo_url"])
  
  t0 = time.time()
  rtn = cli.call("GET_YAHOO", *call_args)
  dt = time.time() - t0
  print("GET_YAHOO dt", dt)

  call_args = []
  for item in rtn:
    _code = item['code']
    item["_update_ts"] = time.time()

    call_args.append(_code)
    call_args.append(item)
    #print("RTN", item)

  with db_cli_pool.connection() as db_cli:
    rtn = db_cli.call('UPDATE_TWSE_EXPONENT_INFO', *call_args)
    #print('UPDATE_TWSE_EXPONENT_INFO', rtn)

  dt = time.time() - t0
  return HttpResponse("update_yahoo_exponent_info2 %s" % dt)






def _old_update_yahoo_exponent_info(request):
  try:
    q = request.GET['q']  
  except:
    q = None

  print('update_yahoo_exponent_info')
  t0 = time.time()
  with db_cli_pool.connection() as db_cli:
    print('db_cli', db_cli)

    if q == "1": 
      _info_list = start_get_yahoo_exponent_infos1()
    elif q == "2": 
      _info_list = start_get_yahoo_exponent_infos2()
    elif q == "3": 
      _info_list = start_get_yahoo_exponent_infos3()
    elif q == "4": 
      _info_list = start_get_yahoo_exponent_infos4()
    elif q == "5": 
      _info_list = start_get_yahoo_exponent_infos5()

    else:
      _info_list = start_get_yahoo_exponent_infos()
    #_info_list = get_twse_exponent_info()

    call_args = []
    for item in _info_list:
      _code = item['code']
      call_args.append(_code)
      call_args.append(item)

    with db_cli_pool.connection() as db_cli:
      rtn = db_cli.call('UPDATE_TWSE_EXPONENT_INFO', *call_args)
      #print('UPDATE_TWSE_EXPONENT_INFO', rtn)

  dt = time.time() - t0
  return HttpResponse("update_yahoo_exponent_info %s" % dt)





  


# --電子類指數及金融保險類指數
def twse_exponent_info_eftri(request):
  exponent_code = request.GET['code']  
  print('exponent_code', exponent_code)
  #exponent_code = exponent_code[3:len(exponent_code)]
  #exponent_code = exponent_code.replace("_", "");
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

  rtn2 = []
  if len(rtn) > 0:
    for r in rtn:
      d = {}
      print(r)
      d['uts'] = int( r.get(b'uts') )
      d['timestamp'] = int( r.get(b'timestamp') )
      d['code'] = r.get(b'code').decode() 
      d['time'] = r.get(b'time').decode() 
      d['value'] = r.get(b'value').decode()
      rtn2.append(d) 
  


  return TemplateResponse(request, 'stock/twse_exponent_info.html', {
    'code':exponent_code,
    'rtn':rtn2,

    'data_date':data_uts,
    'data_volume':data_volume,
    #'dataPoints': dataPoints
  })


def update_twse_exponent_info_eftri(request):
  print('update_twse_exponent_info_eftri')
  t0 = time.time()
  with db_cli_pool.connection() as db_cli:
    print('db_cli', db_cli)
    _info_list = get_twse_exponent_info_eftri()

    call_args = []
    for item in _info_list:
      _code = item['code']
      call_args.append(_code)
      call_args.append(item)

    with db_cli_pool.connection() as db_cli:
      rtn = db_cli.call('UPDATE_TWSE_EXPONENT_INFO', *call_args)
      #print('UPDATE_TWSE_EXPONENT_INFO', rtn)
  dt = time.time() - t0
  return HttpResponse("get_twse_exponent_info_eftri %s" % dt)






# --其他證卷指數
def twse_exponent_info_other(request):
  exponent_code = request.GET['code']  
  print('exponent_code', exponent_code)
  exponent_code = exponent_code[3:len(exponent_code)]
  exponent_code = exponent_code.replace("_", "");
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


  rtn2 = []
  if len(rtn) > 0:
    for r in rtn:
      d = {}
      print(r)
      d['uts'] = int( r.get(b'uts') )
      d['timestamp'] = int( r.get(b'timestamp') )
      d['code'] = r.get(b'code').decode() 
      d['time'] = r.get(b'time').decode() 

      parameter = r.get(b'parameter')
      if parameter is not None:
        parameter = r.get(b'parameter').decode()
        
      d['value'] = parameter 
      rtn2.append(d) 

  #return HttpResponse('stock info.') 
  return TemplateResponse(request, 'stock/twse_exponent_info_other.html', {
    'code':exponent_code,
    'rtn':rtn2,

    'data_date':data_uts,
    'data_volume':data_volume,
    #'dataPoints': dataPoints
  })


def update_twse_exponent_info_other(request):
  print('update_twse_exponent_info_other')

  t0 = time.time()
  with db_cli_pool.connection() as db_cli:
    print('db_cli', db_cli)
    _info_list = get_twse_exponent_info_other(OTHER_EXPONENT)

    call_args = []
    for item in _info_list:
      _code = item['code']
      call_args.append(_code)
      call_args.append(item)

    with db_cli_pool.connection() as db_cli:
      rtn = db_cli.call('UPDATE_TWSE_EXPONENT_INFO', *call_args)
      #print('UPDATE_TWSE_EXPONENT_INFO', rtn)
  dt = time.time() - t0
  return HttpResponse("get_twse_exponent_info_other %s" % dt)
########################################################



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
  return HttpResponse(json.dumps(ctx, ensure_ascii=False))


def parse_timeline_item(content):
  if content == 'Forbidden':
    return
  raw = json.loads(content)
  if raw.has_key('finance'):
    if raw['finance']['result'] == 'null':
      return

  data = raw['chart']['result'][0]
  res_ts = data['timestamp']
  #print("res_ts = ", res_ts)
  out = []

  for i in range(len(res_ts)):
    #print("i = ", i)
    print("res_ts = ", len(res_ts))
    ts = data['timestamp'][i]
    info = data['indicators']['quote'][0]
    _close = info['close'][i]
    _open = info['open'][i]
    _volume = info['volume'][i]
    _high = info['high'][i]
    _low = info['low'][i]

    item = {
      'uts': ts,
      'timestamp': ts,
      'code': int(data['meta']['symbol'].split('.')[0]),
      'close':_close,
      'open':_open,
      'volume':_volume,
      'high':_high,
      'low':_low,
    }
    print("-------------------------------------")
    out.append( item )
  #print('ITEM', item)
  return out 



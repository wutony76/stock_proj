#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import time
import json
import re
import string
import time
import csv
from datetime import datetime 
import requests
import pandas as pd

import collections
import yfaDict



def start_get_yahoo_exponent_infos():
  print("start_get_yahoo_exponent_infos")
  out = []
  t0 = time.time()
  sample_dict = yfaDict.YAHOO_EXPONENT
  sample_dict = collections.OrderedDict(sorted(sample_dict.items()))

  for k, v in sample_dict.items()[32:34]:
    print (k, v["yahoo_url"])
    out = start_get_exponent_info(out, v["yahoo_url"])

  #for k, v in yfaDict.YAHOO_EXPONENT.items():
  #  #print (k, v["yahoo_url"])
  #  out = start_get_exponent_info(out, v["yahoo_url"])
  
  dt = time.time() - t0
  print("DOWNLOAD dt", dt)
  #print("out = ", out, len(out))
  return out




def start_get_exponent_info( out, yahoo_url ):
  
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
  url = yahoo_url
  _code = url.split('=')[-1]
  req_data = {
    #'response':'csv',
    #'date':_date,
    #'ts':time.time(),
  }

  rep = requests.get(url, params=req_data, headers= headers)
  if rep.status_code != 200:
    return out 

  _data = rep.content

  #---update
  _data.strip()
  t_index = _data.index('"tick"', 100)
  s_t = t_index
  _data = "{"+ _data[s_t:len(_data)-2]

  #-head -back
  if not _data.startswith("{"):
    while not _data.startswith("{"):
      _data = _data[1:len(_data)]
  if not _data.endswith("}"):
    while not _data.endswith("}"):
      _data = _data[0:len(_data)-1]
  load_data = json.loads( _data, strict=False )
  #---update_end


  #_data = _data[7:len(_data)-2]
  #load_data = json.loads(_data)
  #print ("tick = ", len( load_data["tick"] ) )

  #out = []
  analyze_data = load_data["tick"][-1]
  #print ("analyze_data = ", analyze_data )

  t = str(analyze_data["t"])
  #print ("t = ", t, len(t) )
  _y = t[0:4]
  _m = t[4:6]
  _d = t[6:8]
  _hr = t[8:10]
  _min = t[10:12]
  _sec = t[12:14]

  #print ( _y, _m, _d, _hr, _min, _sec )
  _date = datetime(int(_y), int(_m), int(_d), int(_hr), int(_min), int(_sec))
  #--- server need -8hr ---#
  unixtime = int( time.mktime(_date.timetuple()) ) - 8*60*60 
  


  #print ( "unixtime ", unixtime )
  ts = unixtime
  p = analyze_data["p"]

  item = {
    'uts': unixtime,
    'timestamp': unixtime,
    'code': _code,

    'time': "%s:%s-%s"%(_hr, _min, _sec),
    'value': p,
  }

  out.append(item)
  #print( "out ", out )
  return out



def main(*args):
  start_get_yahoo_exponent_infos()
  #start_get_exponent_info("https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1m&mkt=10&sym=%23011&callback=twse05")

if __name__ == "__main__":
  main()


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




def start_get_tw50_infos(code_list):
  #print("start_get_tw50_infos")
  print("start_get_tw50_infos code_list", code_list)

  out = []
  t0 = time.time()
  for code in code_list:
    out = start_tw50_single_info(out, code)
  dt = time.time() - t0
  #print("DOWNLOAD dt", dt)
  #print("out = ", out, len(out))
  return out


def start_tw50_single_info(out, code):
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
  #url = yahoo_url
  url = "https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1s&mkt=10"
  req_data = {
    'sym':code,
    'callback':code,
  }
  print("url =",url)

  rep = requests.get(url, params=req_data, headers= headers)
  if rep.status_code != 200:
    return out 

  _data = rep.content
  _data = _data.decode()
  _data.strip()
  #print("_data =", _data)


  #print("t=", _data.index('"tick"'))
  t_index = _data.index('"tick"', 100)
  #print("t=", t_index)
  s_t = t_index
  _data = "{"+ _data[s_t:len(_data)-2]
  #_data = _data[7:len(_data)-2]

  #-head -back
  if not _data.startswith("{"):
    while not _data.startswith("{"):
      _data = _data[1:len(_data)]
  if not _data.endswith("}"):
    while not _data.endswith("}"):
      _data = _data[0:len(_data)-1]

  #print( "d=",_data)
  load_data = json.loads( _data, strict=False )
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
    'code': code,
    'time': "%s:%s-%s"%(_hr, _min, _sec),
    'value': p,
  }

  out.append(item)
  #print( "out ", out )
  return out



def main(*args):
  out = []
  sample = ["1101", "1102" ,"1103"]
  #start_tw50_single_info(out, *sample)
  start_get_tw50_infos(sample)

  #start_get_yahoo_exponent_infos()
  #start_get_exponent_info("https://tw.quote.finance.yahoo.net/quote/q?type=tick&perd=1m&mkt=10&sym=%23011&callback=twse05")

if __name__ == "__main__":
  main()


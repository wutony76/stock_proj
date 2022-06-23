#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function

import json
import requests
import pandas as pd
import re
import string

import time
from datetime import datetime 



def start_get_exponent_info( exponent_code ):
#def start_get_exponent_list():
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}

  url = 'https://www.taiwanindex.com.tw/site/getIndexJSON2'
  #url = 'https://www.taiwanindex.com.tw/site/indexDBJSON'
  req_data = {
    'code':exponent_code,
    'time':'2359',
  }
  rep = requests.get(url, params=req_data, headers= headers)
  if rep.status_code != 200:
    return []

  _data = parse_timeline_item(exponent_code, rep.content)
  #print ("_data ", _data)
  return _data



def parse_timeline_item(code, content):
  if content == 'Forbidden':
    return

  raw = json.loads(content)
  #return raw
  today = datetime.now()
  res_ts = raw['time']
  _y = today.year
  _m = today.month
  _d = today.day
  str_time = "%s_%s_%s"%(_y, _m, _d) 

  out = []
  for i in range(len(res_ts)):
    #print("i = ", i)
    print("res_ts = ", len(res_ts))
    _time = raw['time'][i].split(":")
    value = raw['value'][i]
    
    _date = datetime(_y, _m, _d, int(_time[0]), int(_time[1]))
    unixtime = time.mktime(_date.timetuple())

    #print (_date , type(_date))
    #ts = _date
    #ts = dt_to_ts(_date)
    
    item = {
      'uts': unixtime,
      'timestamp': unixtime,
      'code': code,
      'time':_time,
      'value':value,
    }
    print("-------------------------------------")
    out.append( item )
  return out 





def main(*args):
  start_get_exponent_info("TE20")

  #code = u"1101　台泥"
  #re_char ='[0-9 \t\n\r\f\v]'
  #name = re.sub( re_char, '',code ) 
  #print(name , len(name))

  #split_str = code.split()
  #print(split_str , len(split_str))
  #print(split_str[1] , len(split_str))


if __name__ == "__main__":
  main()




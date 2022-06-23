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

def start_get_exponent_info():
  #sample_dict = {v: k for k, v in sample_dict.items()}
#def start_get_exponent_list():
  today = datetime.now()
  _y = today.year
  _m = today.month
  _d = today.day
  _date = "%s%02d%02d"%(_y, _m, _d)
  print(_date)
  
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
  url = 'https://www.twse.com.tw/exchangeReport/MI_5MINS_INDEX'
  req_data = {
    'response':'csv',
    'date':_date,
    'ts':time.time(),
  }

  t0 = time.time()

  rep = requests.get(url, params=req_data, headers= headers)
  if rep.status_code != 200:
    return []
  _data = rep.content

  dt = time.time() - t0
  print("DOWNLOAD dt", dt)
  #print ("_data ", _data)
  data = csv.reader(_data.splitlines())

  out = []
  for line in data:
    #print('line->', line, len(line) )
    _len = len(line)
    if len(line) == 36:
      try:
        t = line[0].replace("=", "");
        t = t.replace('"', '');
        #print("t =", t )
        #_time = line[0].split(":")
        _time = t.split(":")
        #print( "_time =", _time )
        if len(_time) != 3:
          continue

        for i in range(_len):
          #print (i)
          if i == 0 or i == 35:
            continue
          index = i 
          str_index = "%02d" % index
          _code = "twse%s" % str_index

          _date = datetime(_y, _m, _d, int(_time[0]), int(_time[1]))
          #_date = _date + datetime.timedelta(hours=-8) 
          unixtime = int( time.mktime(_date.timetuple()) ) - 8*60*60

          item = {
            'uts': unixtime,
            'timestamp': unixtime,
            'code': _code,
            'time': line[0],
            'value':line[i],
          }
          out.append(item)
      except:
        pass
  #print( "out ", out )
  return out

  #_data = parse_timeline_item(exponent_code, rep.content)
  ##print ("_data ", _data)
  #return _data



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
    #print("res_ts = ", len(res_ts))
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
    #print("-------------------------------------")
    out.append( item )
  return out 


def main(*args):
  start_get_exponent_info()

if __name__ == "__main__":
  main()


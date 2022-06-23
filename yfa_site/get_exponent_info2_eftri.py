#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import time
import json
import re
import string
import time

import csv
import urllib.request
import codecs

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

  url = 'https://www.twse.com.tw/indicesReport/EFTRI_HIST'
  req_data = {
    #'response':'csv',
    'date':_date,
    'ts':time.time(),
  }
  t0 = time.time()

  #ftpstream = urllib.request.urlopen(url)
  #print(ftpstream)
  #csvfile = csv.reader(codecs.iterdecode(ftpstream, 'utf-8')) 
  
  #for line in csvfile: 
  #  print(line)
  #  data = line


  rep = requests.get(url, params=req_data, headers= headers)
  if rep.status_code != 200:
    return []

  _data = rep.content
  _data = _data.decode()

  jsData = json.loads(_data)
  #print("jsData = ", jsData)
  data = jsData["data"]
  print("data = ", data)


  out = []
  for _i, line in enumerate(data):
    _len = len(line)
    print( "i = ", _i)
    print( "line = ", line, len(line))

    if len(line) == 11:
      try:
        _time = line[0].split("/")
        print( "_time =", _time )


        for i in range(_len):
          #print (i)
          if i == 0 or i == 11:
            continue
          index = i 
          str_index = "%02d" % index
          _code = "eftri%s" % str_index

          _date = datetime(_y, _m, _d, int(_time[1]), int(_time[2]))
          unixtime = time.mktime(_date.timetuple())

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

  print( "out ", out )
  return out



def main(*args):
  start_get_exponent_info()

if __name__ == "__main__":
  main()


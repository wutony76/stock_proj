#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import time
import json
import re
import string
import time
import csv
import queue as Queue
from datetime import datetime 
import requests
import pandas as pd
from yfaDict import OTHER_EXPONENT, OTHER_EXPONENT_CONF




def delay_loop(que):
  for i in range(2):
    print("i = ", i)
    try:
      que.get(timeout = 1)
    except Queue.Empty:
      pass     

def start_get_exponent_info( _dict_key = None):
  que = Queue.Queue()
  today = datetime.now()
  _y = today.year
  _m = today.month
  _d = today.day
  _date = "%s%02d%02d"%(_y, _m, _d)
  print(_date)
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'} 
  out = []
  for _key in _dict_key.keys():
    ori_key = _key[3:len(_key)]
    _key = ori_key.replace("_", "");
    print("ori_key", ori_key)
    print("_key", _key)
    #url = 'https://www.twse.com.tw/exchangeReport/%s' % ori_key
    if _key == "MIINDEX4":
      url = 'https://www.twse.com.tw/exchangeReport/%s' % ori_key
    else:
      url = 'https://www.twse.com.tw/indicesReport/%s' % ori_key


    req_data = {
      #'response':'csv',
      'date':_date,
      'ts':time.time(),
    }
    try:
      t0 = time.time()
      rep = requests.get(url, params=req_data, headers= headers)
      print("url", url)
      print("status_code", rep.status_code)
      if rep.status_code != 200:
        continue
      _data = rep.content

      print("ori_data", type(_data))
      _data = _data.decode() 
      jsData = json.loads(_data)
      d = jsData.get('data')
      print("ttt d", d, type(d))


      dt = time.time() - t0
      print("DOWNLOAD dt", dt)
      #--- analyze_data ---#
      #out = analyze_data(out, _key, data)
      data = d
      out = analyze_data2(out, _key, data)

    except:
      pass

    delay_loop(que)
  print("out =", out)
  return out 



#--- analyze_output_data ---#
def output_data(out, code, data):
  conf = OTHER_EXPONENT_CONF.get(code, None)
  print("output conf", conf)

  if conf is None:
    return  out


  for _i, line in enumerate(data):
    print("_loop ", _i, line)
    if len(line) == conf[1]:
      _parameter = line[1]  
    #if _i > conf[0] and len(line) == conf[1]:
    #if True:
      #_parameter = []
      #for i in range(conf[1] -1):
      #  _parameter.append( line[i] )
      #print("_parameter =", _parameter, conf[1])
      _time = line[0] 
      format_time = _time.split("/")
      _y = int(format_time[0]) + 1911
      _m = int(format_time[1])
      _d = int(format_time[2])
      _date = datetime(_y, _m, _d, 0, 0)
      unixtime = int( time.mktime(_date.timetuple()) )
      print("unixtime ", unixtime)

      # -time- #
      #if conf[1] == 7:
      #  _time = "%s/%s" % (line[0], line[1])
      #  _y = int( line[0] ) + 1911
      #  _m = int( line[1] )
      #  _d = 1
      #  _date = datetime(_y, _m, _d, 0, 0)
      #  unixtime = time.mktime(_date.timetuple())
      #else:
      #  _time = _parameter[0]
      #  format_time = _time.split("/")
      #  _y = int(format_time[0]) + 1911
      #  _m = int(format_time[1])
      #  _d = int(format_time[2])
      #  _date = datetime(_y, _m, _d, 23, 59)
      #  unixtime = time.mktime(_date.timetuple())
      # -time end.- #

      item = {
        'uts': unixtime,
        'timestamp': unixtime,
        'code': code,
        'time': _time,
        #'value':line[i],
        'parameter': _parameter,
      }
      out.append(item)
  return out
  
  
def analyze_data2(out, code, data):
  output_data(out, code, data)
  return out


#--- analyze_data ---#
def analyze_data(out, code, data):
  output_data(out, code, data)
  return out

  ##寶島股價指數
  #if code == "FRMSA":
  #  for _i, line in enumerate(data):
  #    print("_loop ", _i, line)

  #    #if _i != 0:
  #    if _i > 0 and len(line) == 4:
  #      #print(_i, line)
  #      _time = line[0]
  #      format_time = _time.split("/")
  #      _coin = line[1]     #寶島股價指數
  #      _coin2 = line[2]    #寶島股價報酬指數
  #      #print(_time, _coin, _coin2)
  #      _y = int(format_time[0]) + 1911
  #      _m = int(format_time[1])
  #      _d = int(format_time[2])
  #      _date = datetime(_y, _m, _d, 23, 59)
  #      unixtime = time.mktime(_date.timetuple())
  #      item = {
  #        'uts': unixtime,
  #        'timestamp': unixtime,
  #        'code': code,
  #        'time': _time,
  #        #'value':line[i],
  #        'coin': _coin,
  #        'coin2': _coin2,
  #      }
  #      out.append(item)

  ##上市上櫃跨市場成交資訊
  #elif code == "MIINDEX4":
  #  for _i, line in enumerate(data):
  #    print("_loop ", _i, line)
  #    if _i > 1 and len(line) == 5:
  #      #print("_loop ", _i, line)
  #      _time = line[0]
  #      format_time = _time.split("/")
  #      _coin = line[1]     #成交金額(元)
  #      _exponent = line[2]    #寶島股價指數
  #      _up_down = line[3]    #漲跌點數
  #      #print(_time, _coin, _coin2)
  #      _y = int(format_time[0]) + 1911
  #      _m = int(format_time[1])
  #      _d = int(format_time[2])
  #      _date = datetime(_y, _m, _d, 23, 59)
  #      unixtime = time.mktime(_date.timetuple())
  #      item = {
  #        'uts': unixtime,
  #        'timestamp': unixtime,
  #        'code': code,
  #        'time': _time,
  #        #'value':line[i],
  #        'coin': _coin,
  #        'exponent': _exponent,
  #        'up_down': _up_down,
  #      }
  #      out.append(item)

  ####################################
  ##臺灣就業99指數   EMP99
  ##臺灣高薪100指數  HC100
  #elif code == "EMP99" or code == "HC100":
  #  for _i, line in enumerate(data):
  #    print("_loop ", _i, line)
  #    if _i > 1 and len(line) == 4:
  #      #print("_loop ", _i, line)
  #      _time = line[0]
  #      format_time = _time.split("/")
  #      _exponent1 = line[1]    #臺灣就業99指數         #臺灣高薪100指數
  #      _exponent2 = line[2]    #臺灣就業99報酬指數     #臺灣高薪100報酬指數
  #      #print(_time, _coin, _coin2)

  #      _y = int(format_time[0]) + 1911
  #      _m = int(format_time[1])
  #      _d = int(format_time[2])
  #      _date = datetime(_y, _m, _d, 23, 59)
  #      unixtime = time.mktime(_date.timetuple())
  #      item = {
  #        'uts': unixtime,
  #        'timestamp': unixtime,
  #        'code': code,
  #        'time': _time,
  #        #'value':line[i],
  #        'exponent1': _exponent1,
  #        'exponent2': _exponent2,
  #      }
  #      out.append(item)


  ####################################
  ##發行量加權股價報酬指數   MFI94U
  #elif code == "MFI94U":
  #  for _i, line in enumerate(data):
  #    print("_loop ", _i, line)
  #    if _i > 1 and len(line) == 3:
  #      #print("_loop ", _i, line)
  #      _time = line[0]
  #      format_time = _time.split("/")
  #      _exponent1 = line[1]    #發行量加權股價報酬指數

  #      _y = int(format_time[0]) + 1911
  #      _m = int(format_time[1])
  #      _d = int(format_time[2])
  #      _date = datetime(_y, _m, _d, 23, 59)
  #      unixtime = time.mktime(_date.timetuple())
  #      item = {
  #        'uts': unixtime,
  #        'timestamp': unixtime,
  #        'code': code,
  #        'time': _time,
  #        #'value':line[i],
  #        'exponent1': _exponent1,
  #      }
  #      out.append(item)

  ##臺指槓桿及反向指數   TTDR
  #elif code == "TTDR":
  #  for _i, line in enumerate(data):
  #    print("_loop ", _i, line)
  #    if _i > 0 and len(line) == 4:
  #      #print("_loop ", _i, line)
  #      _time = line[0]
  #      format_time = _time.split("/")
  #      _exponent1 = line[1]    #臺指日報酬兩倍指數
  #      _exponent2 = line[2]    #臺指反向一倍指數

  #      _y = int(format_time[0]) + 1911
  #      _m = int(format_time[1])
  #      _d = int(format_time[2])
  #      _date = datetime(_y, _m, _d, 23, 59)
  #      unixtime = time.mktime(_date.timetuple())
  #      item = {
  #        'uts': unixtime,
  #        'timestamp': unixtime,
  #        'code': code,
  #        'time': _time,
  #        #'value':line[i],
  #        'exponent1': _exponent1,
  #        'exponent2': _exponent2,
  #      }
  #      out.append(item)
  #      
  ##發行量加權股價指數   MI_5MINS_HIST
  #elif code == "MI5MINSHIST":
  #  for _i, line in enumerate(data):
  #    print("_loop ", _i, line)
  #    if _i > 1 and len(line) == 6:
  #      pass

  #else:
  #  pass

  #return out



####################################################################
def main(*args):
  start_get_exponent_info(OTHER_EXPONENT)

if __name__ == "__main__":
  main()


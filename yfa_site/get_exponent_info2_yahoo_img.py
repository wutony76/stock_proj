#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function

import os

import time
import json
import re
import string
import time
import csv
from datetime import datetime 
import requests
import pandas as pd


def start_get_exponent_info( yahoo_url ):
  BASE_DIR = os.path.abspath(os.path.dirname(__file__))

  today = datetime.now()
  _y = today.year
  _m = today.month
  _d = today.day
  _date = "%s%02d%02d"%(_y, _m, _d)
  print(_date)
  
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
  url = yahoo_url
  req_data = {
  }

  t0 = time.time()
  rep = requests.get(url, params=req_data, headers= headers)
  if rep.status_code != 200:
    return []
  _data = rep.content
  dt = time.time() - t0
  print("DOWNLOAD dt", dt)

  #with open ('r.txt','rb') as f:
  #  f.write(_data)
  #  f.close
  str_index = url.split('=')[-1] 
  filename = "yahoo_%s_chart%s.png" % (int(time.time()), str_index) 
  #fp = os.path.join(BASE_DIR, "chromedriver")
  file_path = os.path.join(BASE_DIR, "downloads")

  if not os.path.exists(file_path):
    os.makedirs(file_path)

  save_fp = os.path.join(file_path, filename)
  with open(save_fp, 'wb') as f:
    f.write(_data)


def main(*args):
  start_get_exponent_info("https://tw.quote.finance.yahoo.net/quote/chart?t=5&s=1")
  start_get_exponent_info("https://tw.quote.finance.yahoo.net/quote/chart?t=5&s=2")
  start_get_exponent_info("https://tw.quote.finance.yahoo.net/quote/chart?t=5&s=3")
  start_get_exponent_info("https://tw.quote.finance.yahoo.net/quote/chart?t=5&s=4")

if __name__ == "__main__":
  main()


#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function

import time
import json
import requests
import pandas as pd
import re
import string
from bs4 import BeautifulSoup



def start_get_bank_rate_list(code_list):
  #print("start_get_tw50_infos")
  out = []
  t0 = time.time()
  for code in code_list:
    out = start_get_bank_rate(out, code)
  dt = time.time() - t0
  #print("DOWNLOAD dt", dt)
  print("out = ", out, len(out))
  return out


def start_get_bank_rate(out, code):
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
  #url = 'https://www.moneydj.com/ETF/X/Basic/Basic0007a.xdjhtm?etfid=0050.TW'
  url = 'https://tw.stock.yahoo.com/bank/%s'% code

  rep = requests.get(url, headers= headers)
  if rep.status_code != 200:
    return []

  out = []
  soup = BeautifulSoup(rep.text, "html.parser")
  ul_html = soup.find_all("section", class_="My($m-module)")
  #ul_html = soup.find("section", class_="My($m-module)")
  lis = ul_html[1].find_all("li")

  li_text = lis[0].getText();
  div = lis[0].find("div")
  span_list = div.find_all("span")

  buy_rate = span_list[1].getText()
  sell_rate = span_list[2].getText()
  _code = "BANKTAIWAN"

  ts = time.time()
  item = {
    'uts': ts,
    'timestamp': ts,
    'code': _code,

    #'time': "%s:%s-%s"%(_hr, _min, _sec),
    'buy_value': buy_rate,
    'sell_value': sell_rate,
  }

  #out.append((_code, buy_rate, sell_rate))
  out.append(item)
  return out



def main(*args):
  sample = ["0040000"]
  start_get_bank_rate_list(sample)


if __name__ == "__main__":
  main()




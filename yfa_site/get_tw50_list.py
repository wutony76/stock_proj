#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function

import json
import requests
import pandas as pd
import re
import string
from bs4 import BeautifulSoup


def start_get_tw50_list():
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
  #url = 'https://www.moneydj.com/ETF/X/Basic/Basic0007a.xdjhtm?etfid=0050.TW'
  url = 'https://histock.tw/global/globalclass.aspx?mid=0&id=2'
  rep = requests.get(url, headers= headers)
  if rep.status_code != 200:
    return []

  out = []
  soup = BeautifulSoup(rep.text, "html.parser")
  ul_html = soup.find("ul", class_="stock-list")
  lis = ul_html.find_all("li")
  for li in lis:
    _code = li.find("span").getText()
    _name = li.select_one("a").get("title")
    #print(_code, _name)
    out.append((_code, _name))
  return out


def main(*args):
  o = start_get_tw50_list()
  print (o, len(o))


if __name__ == "__main__":
  main()




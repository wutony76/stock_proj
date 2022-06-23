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
#import pandas as pd
from bs4 import BeautifulSoup





def start_get_exponent_info():
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
  url = 'https://www.ig.com/cn/indices/markets-indices/taiwan-index-tw'
  ts = int(time.time())
  req_data = {
    'ts':ts,
  }
  code = "TXV1"

  t0 = time.time()
  rep = requests.get(url, params=req_data, headers= headers)
  if rep.status_code != 200:
    return []

  dt = time.time() - t0
  soup = BeautifulSoup(rep.text, "html.parser")
  #df = pd.read_html(rep.text)
  #_data = rep.content
  
  print("="*30)
  print("DOWNLOAD dt", dt)
  #print ("soup ", soup.prettify())

  out = []
  prices = soup.find_all("div", class_="price-ticket__price")
  for price in prices:
    #print("price =", price)
    tag = price.get("data-field")
    #print(tag)
    if tag == "BID":
      bid = price.getText()
      print("BID = ", price.getText())

    elif tag == "OFR":
      ofr = price.getText()
      print("OFR = ", price.getText())


  h_price = soup.find_all("p", class_="price-ticket__extremums--high")
  p_heigh = h_price[0].select_one("span").getText()
  print("p_heigh = ", p_heigh)

  l_price = soup.find_all("p", class_="price-ticket__extremums--low")
  p_low = l_price[0].select_one("span").getText()
  print("p_low = ", p_low)

  item = {
    'uts': ts,
    'timestamp': ts,
    'code': code,
    "bid": bid,     #賣出
    "ofr": ofr,     #買入
    "hight": p_heigh,
    "low": p_low,
  }

  out.append(item) 
  return out 



def main(*args):
  start_get_exponent_info()


if __name__ == "__main__":
  main()




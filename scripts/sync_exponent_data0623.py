#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import time
import queue as Queue
import requests
#from fatcat.conf import settings as _settings


def main(*args):
  que = Queue.Queue()
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'} 

  
  list_url = []
  
  url1 = "http://3.35.172.98:17320/yahoo/exponent/info/all"
  url2= "http://3.35.172.98:17320/twse/eftri/exponent/info/all"
  url3 = "http://3.35.172.98:17320/twse/other/exponent/info/all"
  url4 = "http://3.35.172.98:17320/bank/rate/info/all"
  url5 = "http://3.35.172.98:17320/tw50/stock/info/all"
  #url = "http://3.115.201.240:17320/yahoo/exponent/info/all?q=1"
  #url = "%s%s"%(_settings.FDSTOCK_SITE_URL, "/yahoo/exponent/info/all?q=1")
  list_url.append( url1 ) 
  list_url.append( url2 ) 
  list_url.append( url3 ) 
  list_url.append( url4 ) 
  list_url.append( url5 ) 
  

  while True:
    print("run.")
    try:
      t0 = time.time()

      for url in list_url:
        print("url = ", url)
        rep = requests.get(url, params={}, headers= headers)
        if rep.status_code == 200:
          print("IS UPDATE.", rep.content)

      ts = time.time() - t0
        
      delay = 10 
      try:
        que.get(timeout = delay)
      except Queue.Empty:
        pass

    except:
      try:
        que.get(timeout = 20)
      except Queue.Empty:
        pass

if __name__ == "__main__":
  main()

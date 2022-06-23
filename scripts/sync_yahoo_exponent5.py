#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import time
import Queue
import requests
from fatcat.conf import settings as _settings


def main(*args):
  que = Queue.Queue()
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'} 
  
  #url = "http://3.115.201.240:17320/twse/exponent/info/all"
  #url = "http://3.115.201.240:17320/yahoo/exponent/info/all?q=1"
  url = "%s%s"%(_settings.FDSTOCK_SITE_URL, "/yahoo/exponent/info/all?q=5")
  

  while True:
    print("run.")
    try:
      t0 = time.time()
      rep = requests.get(url, params={}, headers= headers)
      if rep.status_code == 200:
        print("IS UPDATE.", rep.content)

      dt = time.time() - t0
      print("dt", dt)
      delay = 1.65 - dt
      if delay > 0:
        print("delay", delay)
        
        try:
          que.get(timeout = delay)
        except Queue.Empty:
          pass

    except:
      try:
        que.get(timeout = 1)
      except Queue.Empty:
        pass

if __name__ == "__main__":
  main()

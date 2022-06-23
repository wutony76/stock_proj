#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import Queue
import requests


def main(*args):
  que = Queue.Queue()
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'} 
  
  url = "http://3.115.201.240:17320/twse/exponent/info/all"
  while True:
    print("run.")
    rep = requests.get(url, params={}, headers= headers)
    if rep.status_code == 200:
      print("IS UPDATE.")
      
    for i in range(10):
      print("i = ", i)
      try:
        que.get(timeout = 1)
      except Queue.Empty:
        pass







if __name__ == "__main__":
  main()

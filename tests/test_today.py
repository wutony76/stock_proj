#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import Queue
import threading
import random
import json
import time
import requests
import traceback
import datetime




def main(*args):
  today = datetime.date.today()
  _y = today.year
  _m = today.month
  _d = today.day

  _date = datetime.datetime(int(_y), int(_m), int(_d), 0, 0, 0)
  ##--- server need -8hr ---#
  unixtime = int( time.mktime(_date.timetuple()) ) - 8*60*60 
  print (unixtime)

  
  

if __name__ == "__main__":
  main()



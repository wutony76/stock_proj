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


def thread_job(data, q):
  for i in range(len(data)): 
    data[i] = data[i]*2

  q.put(data)


def multithread():
  data = [[1, 2, 3], [4, 5, 6]]
  q = Queue.Queue()
  all_thread = []

  # 使用 multi-thread
  for i in range(len(data)):
    thread = threading.Thread(target=thread_job, args=(data[i], q))
    thread.start()
    all_thread.append(thread)
 
  # 等待全部 Thread 執行完畢
  for t in all_thread:
    t.join()

  # 使用 q.get() 取出要傳回的值
  result = []
  for _ in range(len(all_thread)):
    result.append(q.get())
  print(result)


def main(*args):
  multithread()


if __name__ == "__main__":
  main()



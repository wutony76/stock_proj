#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import traceback



def main(*args):
  print("test123")
  i = 2 

  try:
    if i == 1:
      raise Exception("err 1")
    else:
      print("success")

  except Exception as ex:
    traceback.print_stack()
    traceback.print_exc()
    print("ex", ex.message)

  


if __name__ == "__main__":
  main()

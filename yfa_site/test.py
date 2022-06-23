#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import collections








def main(*args):
  test = {
    "a":"aaa",
    "b":"bbb",
    "c":"ccc",
    "d":"ddd",
    "e":"eee",
    "f":"fff",
    "g":"ggg",
    "h":"hhh",
  } 

  print("test = ", len(test))

  #sample_dict = {k:v for k, v in test.items()}
  test = collections.OrderedDict(sorted(test.items()))

  print("sample_dict = ", test)
  for k, v in test.items()[0:3]:
    print (k, v)



if __name__ == "__main__":
  main()


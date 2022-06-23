#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function

import json
import requests
import pandas as pd
import re
import string




def full2half(s):
  n = []
  s = s.decode('utf-8')
  for char in s:
    num = ord(char)
    if num == 0x3000:
      num = 32
    elif 0xFF01 <= num <= 0xFF5E:
      num -= 0xfee0
    num = unichr(num)
    n.append(num)
  return ''.join(n)


def start_get_twse_list():
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
  url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
  rep = requests.get(url, headers= headers)
  print('rep', rep)

  df = pd.read_html(rep.text)[0]
  df.columns = [
    u'有價證券代號及名稱',
    u'國際證券辨識號碼(ISIN Code)', 
    u'上市日', 
    u'市場別', 
    u'產業別', 
    u'CFICode', 
    u'備註',
  ]

  #print(df)
  stackCodeDict = {}
  for code in df[u'有價證券代號及名稱']:
    pattern = "[0-9]"

    try:
      #print ("code =", code, type(code))
      stackCode = code.split()
      #print("stackCode - ", stackCode)
      if stackCode[0] and re.search(pattern, stackCode[0]) and len(stackCode[0]) == 4:
        #print( str(stackCode[0]) + stackCode[1] )
        stackCodeDict[int(stackCode[0])] = stackCode[1]

      if re.search(pattern, stackCode[0]) and len(stackCode[0]) >= 5:
        print("-- stackCode stop. --")
        print("stackCodeDict = ", stackCodeDict)
        return stackCodeDict

    except:
      print("-- err stackCode. --")
      pass





def main(*args):
  start_get_twse_list()

  #code = u"1101　台泥"
  #re_char ='[0-9 \t\n\r\f\v]'
  #name = re.sub( re_char, '',code ) 
  #print(name , len(name))

  #split_str = code.split()
  #print(split_str , len(split_str))
  #print(split_str[1] , len(split_str))


if __name__ == "__main__":
  main()




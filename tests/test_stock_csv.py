from __future__ import print_function
from datetime import datetime
import time
import pytz
from cStringIO import StringIO
import requests
import csv
import pandas as pd
import chardet
from infoex.networking import NetManager

net_manager = NetManager.get_inst()

def main(*args):

  now = datetime.now()
  date_str = now.strftime("%Y%m%d")
  
  url = "https://www.twse.com.tw/indicesReport/MI_5MINS_HIST?response=csv&date=%s" % date_str
  rep = requests.post(url)

  raw_text = rep.text
  #raw_text3 = rep.content.decode('utf-8')
  #print("raw_text3", raw_text3)
  lines = raw_text.splitlines()
  #print("lines", lines)
  rd = csv.reader(lines[2:], delimiter=',')

  tzinfo = pytz.timezone("Asia/Taipei")

  call_args = []
  for row in rd:
    print("row", row)
    #date = datetime.strptime(row[0], "%"
    d1, d2, d3 = row[0].split('/')
    d = datetime(1911+int(d1), int(d2), int(d3))
    d = d.replace(tzinfo=tzinfo)
    n1 = float(row[1].replace(',', ''))
    n2 = float(row[2].replace(',', ''))
    n3 = float(row[3].replace(',', ''))
    n4 = float(row[4].replace(',', ''))
    print(d, n1, n2, n3, n4)
    dnum = int(d.strftime('%Y%m%d'))
    ts = time.mktime(d.utctimetuple())
    info = {
      "time": ts,
      "start": n1, 
      "max": n2, 
      "min": n3, 
      "end": n4, 
    }
    call_args.append(dnum)
    call_args.append(info)


  with net_manager.infoex_route_cli_pool.connection() as infoex_route_cli:
    
    rtn = infoex_route_cli.db_call("UPDATE_STOCKINDEX_INFO", *call_args)
    print("UPDATE_STOCKINDEX_INFO", rtn)
    #infoex_route_cli.db_call("LIST_STOCKINDEX_INFO",
  


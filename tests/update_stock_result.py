from __future__ import print_function
from datetime import datetime, timedelta
import time
import pytz
import requests
import csv
from BTrees import OOBTree
from infoex.networking import NetManager
from infoex import twse_utils

net_manager = NetManager.get_inst()

def main(*args):


  row_by_date = OOBTree.OOBTree()

  with net_manager.infoex_route_cli_pool.connection() as infoex_route_cli:
    keys = infoex_route_cli.call("STOCKINDEX_INFO_KEYS", None)
    print("STOCKINDEX_INFO_KEYS",keys)
    rtn = infoex_route_cli.call("LIST_STOCKINDEX_INFO", None, *keys)
    for dkey, info in zip(keys, rtn):
      dt = datetime.fromtimestamp(info["time"]).replace(tzinfo=pytz.utc)
      dt2 = dt.astimezone(twse_utils.TZ_TW)
      row_by_date[dt2] = info


  print("=" * 100)
  rows = []
  for d1, row in row_by_date.items():
    rows.append((d1, row))
    print("row", d1, row)

  call_args = []

  rows = rows[::-1]
  for i in xrange(0, len(rows)-1, 1):
    d1, row1 = rows[i]
    d2, row2 = rows[i+1]
    print(d1, row1, d2, row2)
    dt = row1["end"] - row2["end"]

    code = 0
    if dt > 0:
      code = 1
    elif dt < 0:
      code = 2

    info = {
      "time": row1["time"],
      "end": row1["end"],
      "delta": dt,
      "code": code,
    }

    key = -int(d1.strftime('%Y%m%d'))
    
    call_args.append(key)
    call_args.append(info)

  with net_manager.infoex_route_cli_pool.connection() as infoex_route_cli:
    rtn = infoex_route_cli.call("UPDATE_STOCK_RESULT", None, *call_args)
    print("UPDATE_STOCK_RESULT", rtn)
  #  #infoex_route_cli.db_call("LIST_STOCKINDEX_INFO",
  


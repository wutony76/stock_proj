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

  date_str = args[0]

  call_args = []

  print("=" * 100)
  for d1, row in twse_utils.iter_index_rows(date_str):
    print("iter_index", d1, row)
    key = int(d1.strftime("%Y%m%d"))
    call_args.append(key)
    call_args.append(row)

  with net_manager.infoex_route_cli_pool.connection() as infoex_route_cli:
    rtn = infoex_route_cli.call("UPDATE_STOCKINDEX_INFO", None, *call_args)
    print("UPDATE_STOCKINDEX_INFO", rtn)
  #  #infoex_route_cli.db_call("LIST_STOCKINDEX_INFO",
  


from __future__ import print_function
from datetime import datetime, timedelta
import time
import pytz
import requests
import csv
from BTrees import OOBTree
from fdstock.networking import NetManager
from fdstock import twse_utils

net_mgr = NetManager.get_inst()

def main(*args):

  call_args = []

  it = twse_utils.iter_equities_rows()
  for x in it:
    cat = x[0]
    code = x[1]
    name = x[2]

    if cat == u'股票':
      print('x', x)

      info = {
        'cat_id': 1,
        'code': code,
        'name': name,
      }

      call_args.append(code)
      call_args.append(info)


  with net_mgr.db_cli_pool.connection() as db_cli:
    rtn = db_cli.call("UPDATE_EQUITY", *call_args)
    print("UPDATE_EQUITY", rtn)

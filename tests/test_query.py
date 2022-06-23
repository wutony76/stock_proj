from __future__ import print_function
from datetime import datetime, timedelta
import time
import pytz
import json
import requests
from fatcat.conf import settings as _settings
from spider.rpcclient import RPCClient
from fdpays.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw
from fdstock.networking import NetManager
from fdstock import twse_utils

net_mgr = NetManager.get_inst()

def main(*args):

  cli = RPCClient(_settings.FDSTOCK_DB_ADDR)

  now = ts_to_tz_tw(time.time())
  end = now
  start = end - timedelta(hours=24)

  start_t = int(start.strftime('%Y%m%d%H%M%S'))
  end_t = int(end.strftime('%Y%m%d%H%M%S'))

  rtn = cli.call('TIMELINE_ITEMS', None, '2330', start_t, end_t)[0]
  print('TIMELINE_ITEMS', rtn)
  counter = 0
  for info in rtn:
    counter += 1
    uts = info['uts']
    ts = uts / 1000.0
    dt = ts_to_tz_tw(ts)
    print(counter, 'uts', uts, dt)

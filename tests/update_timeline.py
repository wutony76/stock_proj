from __future__ import print_function
from datetime import datetime, timedelta
import time
import pytz
import json
import requests
import Queue
from fatcat.conf import settings as _settings
from spider.rpcclient import RPCClient
from fdpays.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw
from fdstock.networking import NetManager
from fdstock import twse_utils

net_mgr = NetManager.get_inst()

def main(*args):
  que = Queue.Queue()

  cli = RPCClient(_settings.FDSTOCK_DB_ADDR)
  equities = cli.call('ALL_EQUITY', None)



  codes = ['2330']

  for equity in equities:
    code = equity['code']
  

  now = ts_to_tz_tw(time.time())
  sec = int(now.second // 5) * 5

  dt = datetime(now.year, now.month, now.day, now.hour, now.minute, sec) 
  dt = TZ_TW.localize(dt)
  
  for i in xrange(1024):
    ts = dt_to_ts(dt)
    print('dt', dt, ts)
    dt_tz = ts_to_tz_tw(ts)
    print('dt_tz', dt_tz)

    uts = int(ts) * 1000

    print('dt', dt, 'uts', uts)

    if True:

      for code in codes:
        #code = '2330'
        #print('code', code)
        item = get_timeline_item(code, uts)

        if item is not None:
          _uts = item['uts']
          rtn = cli.call('UPDATE_TIMELINE', None, code, _uts, item)
          print('UPDATE_TIMELINE', rtn)

    dt = dt + timedelta(seconds=5)

    try:
      que.get(timeout=3)
    except Queue.Empty:
      pass




def get_timeline_item(code, q_uts):
  

  code_desc = 'tse_%s.tw' % code
  
  url = 'https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=%s&_=%s' % (code_desc, q_uts)
  key = url
  print('url', url)

  cli = RPCClient(_settings.FDSTOCK_HTML_ADDR)

  rtn = cli.call('GET_REQ', None, key)[0]
  print('GET_REQ', rtn)

  if rtn is None:

    rep = requests.get(url)

    meta = {
      'encoding': rep.encoding,
    }

    print('meta', meta, 'content', rep.content)
    rtn_ = cli.call('SET_REQ', None, key, meta, rep.content)
    print('SET_REQ', rtn_)
    rtn = meta, rep.content

    #with net_mgr.db_cli_pool.connection() as db_cli:
    #  rtn = db_cli.call("UPDATE_EQUITY", None, *call_args)
    #  print("UPDATE_EQUITY", rtn)

  meta, content = rtn
  encoding = meta['encoding']
  raw = json.loads(content)

  if raw['rtcode'] == '5000':
    return
  msg_arr = raw['msgArray']
  if len(msg_arr) == 0:
    return


  #print('loads', raw)
  data = msg_arr[0]
  uts = int(data['tlong'])
  ts = uts / 1000
  name = data['n']
  fullname = data['nf']
  code = data['c']
  last_trade_price = data.get('z', None)
  trade_volume = data.get('tv', None)
  accumulate_trade_volume = data.get('v', None)
  best_bid_price = split_best(data.get('b', None))
  best_bid_volume = split_best(data.get('g', None))
  best_ask_price = split_best(data.get('a', None))
  best_ask_volume = split_best(data.get('f', None))
  _open = data.get('o', None)
  high = data.get('h', None)
  low = data.get('l', None)

  item = {
    'uts': uts,
    'timestamp': ts,
    'name': name,
    'fullname': fullname,
    'code': code,
    'last_trade_price': last_trade_price,
    'trade_volume': trade_volume,
    'accumulate_trade_volume': accumulate_trade_volume,
    'best_bid_price': best_bid_price,
    'best_bid_volume': best_bid_volume,
    'best_ask_price': best_ask_price,
    'best_ask_volume': best_ask_volume,
    'open': _open,
    'high': high,
    'low': low,
  }

  print('ITEM', item)

  return item

def split_best(d):
  if d:
    return d.strip('_').split('_')
  return d

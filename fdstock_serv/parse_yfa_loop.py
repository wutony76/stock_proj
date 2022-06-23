from __future__ import print_function
import time
import threading
import traceback
from datetime import datetime
import random
import json
import Queue
import rwlock
from zodbpickle import pickle
from fatcat.conf import settings as _settings
from fdstock.rpcclient import RPCClientPool
from fdstock.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw
from fdpays.commit_notify import CommitNotifyManager


def spawn(func):
  th = threading.Thread(target=func)
  th.setDaemon(True)
  th.start()

class DataSet(object):
  def __init__(self, tdb):
    self.tdb = tdb
    self.schema = tdb.new_oobtree(11, max_leaf_size=1024, max_internal_size=1024)

  def commit(self):
    self.tdb.commit()

class ParseLoop(object):
  def __init__(self, tdb):
    self.lock = rwlock.RWLock()
    self.db = DataSet(tdb)
    self.txnmgr = CommitNotifyManager(self.db)

  def run(self):
    spawn(self.txnmgr.run)
    
    que = Queue.Queue()
    counter = 0
    html_cli_pool = RPCClientPool(_settings.FDSTOCK_HTML_ADDR)
    db_cli_pool = RPCClientPool(_settings.FDSTOCK_YFA_DB_ADDR)
    #db_cli_pool = RPCClientPool(_settings.FDSTOCK_DB_ADDR)

    print ("FDSTOCK_YFA_DB_ADDR = ", _settings.FDSTOCK_YFA_DB_ADDR )

    with self.txnmgr.get_request() as txn:
      with self.lock.reader_lock:
        db = txn.db
        last_key = db.schema.get('last_key', None)

    try:
      que.get(timeout=1)
    except Queue.Empty:
      pass

    #que_id = 1
    que_id = 11

    
    while True:
      #print('loop', counter, last_key)
      loop_delay = 1


      with html_cli_pool.connection() as html_cli:
        with db_cli_pool.connection() as db_cli:
          rows = html_cli.call('ITEMS_DATA', que_id, last_key, 32)
          print('ITEMS_DATA que_id=%s' % que_id, last_key, len(rows))

          if rows:
            loop_delay = 0.2
            call_args = []

            for row in rows:
              key, data = row
              last_key = key

              data = pickle.loads(data)
              meta, content = data

              print ("meta -", meta)
              #print ("content -", content)
              item = parse_timeline_item(meta, content)
              print ("item -", item)

              if item is not None:
                uts = item['uts']
                code = item['code']
                #print ("uts -", uts)
                #print ("code -", code)
                call_args.append(code)
                call_args.append(uts)
                call_args.append(item)

            print('*'*50)
            print('ITEMS_DATA', key, meta, item)

            rtn = db_cli.call('UPDATE_TIMELINE', *call_args)
            print('UPDATE_TIMELINE', rtn)

            with self.txnmgr.get_request() as txn:
              with self.lock.writer_lock:
                db = txn.db
                db.schema['last_key'] = last_key
                txn.notify_changed(0, 1)

      try:
        que.get(timeout=loop_delay)
      except Queue.Empty:
        pass



def parse_timeline_item(meta, content):

  if content == 'Forbidden':
    return

  encoding = meta['encoding']
  raw = json.loads(content)

  if raw.has_key('finance'):
    if raw['finance']['result'] == 'null':
      return

  data = raw['chart']['result'][0]
  ts = data['timestamp'][0]
  info = data['indicators']['quote'][0]

  _close = info['close'][0]
  _open = info['open'][0]
  _volume = info['volume'][0]
  _high = info['high'][0]
  _low = info['low'][0]

  item = {
    'uts': ts,
    'timestamp': ts,
    'code': int(data['meta']['symbol'].split('.')[0]),
    'regularMarketPrice': data['meta']['regularMarketPrice'],
    'chartPreviousClose': data['meta']['chartPreviousClose'],
    'priceHint': data['meta']['priceHint'],
    'currentTradingPeriod':{
      'pre':{
        'timezone':data['meta']['currentTradingPeriod']['pre']['timezone'],
        'end':data['meta']['currentTradingPeriod']['pre']['end'],
        'start':data['meta']['currentTradingPeriod']['pre']['start'],
        'gmtoffset':data['meta']['currentTradingPeriod']['pre']['gmtoffset'],
      },
      'regular':{
        'timezone':data['meta']['currentTradingPeriod']['regular']['timezone'],
        'end':data['meta']['currentTradingPeriod']['regular']['end'],
        'start':data['meta']['currentTradingPeriod']['regular']['start'],
        'gmtoffset':data['meta']['currentTradingPeriod']['regular']['gmtoffset'],
      },
      'post':{
        'timezone':data['meta']['currentTradingPeriod']['post']['timezone'],
        'end':data['meta']['currentTradingPeriod']['post']['end'],
        'start':data['meta']['currentTradingPeriod']['post']['start'],
        'gmtoffset':data['meta']['currentTradingPeriod']['post']['gmtoffset'],
      },
    },

    'close':_close,
    'open':_open,
    'volume':_volume,
    'high':_high,
    'low':_low,
  }
  



  #if raw['rtcode'] == '5000':
  #  return
  #msg_arr = raw['msgArray']
  #if len(msg_arr) == 0:
  #  return


  ##print('loads', raw)
  #data = msg_arr[0]
  #uts = int(data['tlong'])
  #ts = uts / 1000
  #name = data['n']
  #fullname = data['nf']
  #code = data['c']
  #last_trade_price = data.get('z', None)
  #trade_volume = data.get('tv', None)
  #accumulate_trade_volume = data.get('v', None)
  #best_bid_price = split_best(data.get('b', None))
  #best_bid_volume = split_best(data.get('g', None))
  #best_ask_price = split_best(data.get('a', None))
  #best_ask_volume = split_best(data.get('f', None))
  #_open = data.get('o', None)
  #high = data.get('h', None)
  #low = data.get('l', None)

  #item = {
  #  'uts': uts,
  #  'timestamp': ts,
  #  'name': name,
  #  'fullname': fullname,
  #  'code': code,
  #  'last_trade_price': last_trade_price,
  #  'trade_volume': trade_volume,
  #  'accumulate_trade_volume': accumulate_trade_volume,
  #  'best_bid_price': best_bid_price,
  #  'best_bid_volume': best_bid_volume,
  #  'best_ask_price': best_ask_price,
  #  'best_ask_volume': best_ask_volume,
  #  'open': _open,
  #  'high': high,
  #  'low': low,
  #}

  print('ITEM', item)
  return item

def split_best(d):
  if d:
    return d.strip('_').split('_')
  return d

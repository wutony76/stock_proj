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
    twse_db_cli_pool = RPCClientPool(_settings.FDSTOCK_TWSE_DB_ADDR)

    with self.txnmgr.get_request() as txn:
      with self.lock.reader_lock:
        db = txn.db
        last_key = db.schema.get('last_key', None)

    try:
      que.get(timeout=1)
    except Queue.Empty:
      pass


    que_id = 1

    
    while True:
      #print('loop', counter, last_key)
      loop_delay = 1


      with html_cli_pool.connection() as html_cli:
        with twse_db_cli_pool.connection() as db_cli:
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

              item = parse_timeline_item(meta, content)
              uts = item['uts']
              code = item['code']

              call_args.append(code)
              call_args.append(uts)
              call_args.append(item)

            rtn = db_cli.call('TIMELINE_UPDATE', *call_args)
            print('TIMELINE_UPDATE', rtn)
              #print('ITEMS_DATA', key, meta, item)

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

  #print('ITEM', item)

  return item

def split_best(d):
  if d:
    return d.strip('_').split('_')
  return d

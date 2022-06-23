from __future__ import print_function
import time
import threading
import traceback
from datetime import datetime
import random
import Queue
import rwlock
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

    self.info_by_vid = tdb.new_oobtree(21, max_leaf_size=256, max_internal_size=1024)

  def commit(self):
    self.tdb.commit()


class PendingData(object):

  def __init__(self):
    self.uts = None
    self.equity_codes = []

class CollectLoop(object):

  def __init__(self, tdb):

    self.lock = rwlock.RWLock()
    self.db = DataSet(tdb)
    self.txnmgr = CommitNotifyManager(self.db)

  def run(self):
    spawn(self.txnmgr.run)
    
    que = Queue.Queue()
    counter = 0
    cli_pool = RPCClientPool(_settings.FDSTOCK_BROKER_ADDR)

    eq_codes = [
      '2324',
      '2327',
      '2328',
      '2329',
      '2330',
    ]

    pending = PendingData()

    while True:
      loop_delay = 1

      counter += 1


      try:
        que.get(timeout=loop_delay)
      except Queue.Empty:
        pass

      now = ts_to_tz_tw(time.time())
      sec = int(now.second // 5) * 5

      dt = datetime(now.year, now.month, now.day, now.hour, now.minute, sec) 
      dt = TZ_TW.localize(dt)
      ts = dt_to_ts(dt)
      uts = int(ts*1000)

      if pending.uts != uts:
        pending.equity_codes = sorted(eq_codes, key=lambda x: random.random())
        pending.uts = uts
        
      print('loop', counter, 'dt', dt, uts)

      if len(pending.equity_codes) > 0:
        with cli_pool.connection() as cli:
          all_villager_ids = cli.call('ALL_PROTOCOL', 1)[0]
          print('ALL_PROTOCOL', all_villager_ids)
          if len(all_villager_ids) > 0:
            
            now_t = time.time()
            active_vids = []

            with self.txnmgr.get_request() as txn:
              with self.lock.reader_lock:
                db = txn.db

                for vid in all_villager_ids:
                  try:
                    info = db.info_by_vid[vid]
                  except KeyError:
                    info = None

                  last_t = 0
                  if info is not None:
                    last_t = info.get('last_t', 0)

                  qdt = now_t - last_t
                  print('vid=%s dt=%s' % (vid, qdt))
                  if qdt >= 1.6:
                    active_vids.append(vid)

            if active_vids:

              #if len(pending.equity_codes) < 1:
              #  pending.equity_codes = sorted(eq_codes, key=lambda x: random.random())

              with self.txnmgr.get_request() as txn:
                with self.lock.writer_lock:
                  db = txn.db

                  for i in xrange(4096):
                    if len(pending.equity_codes) == 0:
                      break
                    if len(active_vids) == 0:
                      break

                    vid = active_vids.pop()
                    eq_code = pending.equity_codes.pop()
                  
                    save_meta = {
                      'equity': eq_code,
                      'uts': pending.uts,
                    }
                    #url = 'http://54.95.200.135:17120/stock/api/getStockInfo.jsp?ex_ch=tse_%s.tw&_=%s' % (code, uts)
                    url = 'http://54.95.200.135:17120/stock/api/getStockInfo.jsp'
                    extra_headers = {}
                    req_data = {
                      'ex_ch': 'tse_%s.tw' % eq_code,
                      '_': uts,
                    }
                    rtn = cli.call('SEND_COMMAND_TO', vid, 'HTTP_REQ', [url, 'GET', extra_headers, req_data, 1, save_meta])

                    try:
                      info = db.info_by_vid[vid]
                    except KeyError:
                      info = {}

                    info['last_t'] = time.time()
                    db.info_by_vid[vid] = info

                  txn.notify_changed(0, 1)

           


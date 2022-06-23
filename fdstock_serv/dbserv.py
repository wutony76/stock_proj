from __future__ import print_function
import traceback
import threading
import random
import rwlock
import queue as Queue
from datetime import datetime
import time
import pytz
import msgpack

#from fatcat.conf import settings as _settings
from fcworks.conf import settings as _settings
from fdpays.commit_notify import CommitNotifyManager
from fdpays.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw


def spawn(func):
  th = threading.Thread(target=func)
  th.setDaemon(True)
  th.start()

FMT_DATA_INDEX2 = '%08x:%016x'
FMT_DATA_INDEX3 = '%08x:%016x:%016x'

class DataIndexOpts:
  SCHEMA = 1

  EQUITY_DATA = 501

  STOCK_TIMELINE_INDEX = 601
  STOCK_TIMELINE_DATA = 602

class SchemaOpts:
  LAST_SEQ = 1

class DataSet(object):
  
  def __init__(self, tdb):
    self.tdb = tdb

    self.schema = tdb.new_oobtree(11, max_leaf_size=1024, max_internal_size=1024)

    self.data_index2_128 = tdb.new_oobtree(25, max_leaf_size=128, max_internal_size=1024)
    self.data_index2_256 = tdb.new_oobtree(26, max_leaf_size=256, max_internal_size=1024)
    self.data_index2_512 = tdb.new_oobtree(27, max_leaf_size=512, max_internal_size=1024)

    self.data_index3_16 = tdb.new_oobtree(32, max_leaf_size=16, max_internal_size=1024)
    self.data_index3_32 = tdb.new_oobtree(33, max_leaf_size=32, max_internal_size=1024)
    self.data_index3_64 = tdb.new_oobtree(34, max_leaf_size=64, max_internal_size=1024)
    self.data_index3_128 = tdb.new_oobtree(35, max_leaf_size=128, max_internal_size=1024)
    self.data_index3_256 = tdb.new_oobtree(36, max_leaf_size=256, max_internal_size=1024)
    self.data_index3_512 = tdb.new_oobtree(37, max_leaf_size=512, max_internal_size=1024)
    self.data_index3_1024 = tdb.new_oobtree(38, max_leaf_size=1024, max_internal_size=1024)

    self.equity_id_by_code = tdb.new_oobtree(101, max_leaf_size=512, max_internal_size=1024)


  def commit(self):
    self.tdb.commit()

  def new_obj_id(self):
    i_k = FMT_DATA_INDEX3 % (DataIndexOpts.SCHEMA, SchemaOpts.LAST_SEQ, 0)
    obj_id = self.data_index3_512.get(i_k, 0) + 1
    self.data_index3_512[i_k] = obj_id
    return obj_id



class Request(object):
  def __init__(self, args, txn):
    self.args = args
    self.txn = txn

class Factory(object):
  def __init__(self, tdb):

    self.db = DataSet(tdb)

    self.lock = rwlock.RWLock()
    self.txnmgr = CommitNotifyManager(self.db)


  def setup(self, serverfactory):
    self.serverfactory = serverfactory

    spawn(self.txnmgr.run)


  def process_command(self, cmd_name, *cmd_args):
    #print(self, 'process_command', cmd_name, seqid, cmd_args)
    func_name = 'handle_command_%s' % cmd_name
    func = getattr(self, func_name, None)

    if func is None:
      raise Exception('no command %s' % cmd_name)

    with self.txnmgr.get_request() as txn:
      req = Request(cmd_args, txn)
      rtn = func(req)

      return rtn
  
  def handle_command_GET_EQUITY(self, req):
    out = []

    txn = req.txn
    args = req.args

    db = txn.db
    data_index = db.data_index2_256
    with self.lock.reader_lock:
      for i in xrange(0, len(args), 2):
        code = args[i]
        try:
          eqid = db.equity_id_by_code[code]
        except KeyError:
          eqid = None

        info = None

        if eqid is not None:
          i_eq = FMT_DATA_INDEX2 % (DataIndexOpts.EQUITY_DATA, eqid)
          try:
            info = data_index[i_eq]
          except KeyError:
            pass
        out.append(info)

    return out

  def handle_command_ALL_EQUITY(self, req):
    out = []

    txn = req.txn
    args = req.args

    db = txn.db
    data_index = db.data_index2_256
    with self.lock.reader_lock:
      for code, eqid in db.equity_id_by_code.items():
        print('equity_id_by_code.items', code, eqid)
        i_eq = FMT_DATA_INDEX2 % (DataIndexOpts.EQUITY_DATA, eqid)
        try:
          info = data_index[i_eq]
        except KeyError:
          info = None
        out.append(info)

    return out


  def handle_command_UPDATE_EQUITY(self, req):
    out = []

    txn = req.txn
    args = req.args

    db = txn.db
    data_index = db.data_index2_256
    with self.lock.writer_lock:
      for i in xrange(0, len(args), 2):
        code = args[i]
        data = args[i+1]
        try:
          eqid = db.equity_id_by_code[code]
        except KeyError:
          eqid = db.new_obj_id()
          db.equity_id_by_code[code] = eqid

        i_eq = FMT_DATA_INDEX2 % (DataIndexOpts.EQUITY_DATA, eqid)
        try:
          info = data_index[i_eq]
        except KeyError:
          info = {}


        data2 = dict(info)
        data2.update(data)
        data2['_id'] = eqid
         
        data_index[i_eq] = data2
        print('UPDATE_EQUITY', code, data2)
        out.append(eqid)


      txn.notify_changed(0, 1)

    return out

  ##
  def handle_command_TIMELINE_ITEMS(self, req):
    txn = req.txn
    args = req.args
    db = txn.db

    out = []
    ts_index = db.data_index3_1024
    data_index = db.data_index2_256

    print('TIMELINE_TIEMS', args)

    with self.lock.reader_lock:
      for i in xrange(0, len(args), 3):
        equity_code = args[i]
        start_time = args[i+1]
        end_time = args[i+2]

        _start = ixtime_to_tz_tw(start_time)
        _end = ixtime_to_tz_tw(end_time)
        _start_ts = dt_to_ts(_start)
        _end_ts = dt_to_ts(_end)

        _start_uts = int(_start_ts) * 1000
        _end_uts = int(_end_ts) * 1000

        print('TIMELINE_ITEMS', equity_code, _start, _end, _start_uts, _end_uts)

        try:
          eqid = db.equity_id_by_code[equity_code]
        except KeyError:
          eqid = None

        rtn = []

        if eqid is not None:
          i_start = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_INDEX, eqid, _start_uts)
          i_end = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_INDEX, eqid, _end_uts)
            
          print('TIMELINE_ITEMS cod=%s eqid=%s' % (equity_code, eqid), 'i_start=%s~%s' % (i_start, i_end))

          for k, data_id in ts_index.items(i_start, i_end):
            i_data = FMT_DATA_INDEX2 % (DataIndexOpts.STOCK_TIMELINE_DATA, data_id)
            info = data_index[i_data]
            rtn.append(info)

        out.append(rtn)

    return out

  def handle_command_UPDATE_TIMELINE(self, req):
    out = []

    txn = req.txn
    args = req.args

    db = txn.db
    #print('UPDATE_TIMELINE', args)

    ts_index = db.data_index3_1024
    data_index = db.data_index2_256

    with self.lock.writer_lock:
      for i in xrange(0, len(args), 3):
        equity_code = args[i]
        uts = args[i+1]
        info = args[i+2]

        try:
          eqid = db.equity_id_by_code[equity_code]
        except KeyError:
          eqid = None

        rtn = None

        if eqid is not None:

          i_fwd = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_INDEX, eqid, uts)
          try:
            _id = ts_index[i_fwd]
          except KeyError:
            _id = db.new_obj_id()
            ts_index[i_fwd] = _id

          i_data = FMT_DATA_INDEX2 % (DataIndexOpts.STOCK_TIMELINE_DATA, _id)
          data_index[i_data] = info

          print('UPDATE_TIMELINE code=%s eqid=%s' % (equity_code, eqid), i_fwd, i_data)
          print('info', info)

          rtn = _id

        out.append(rtn)

      txn.notify_changed(0, 1)
    return out

def ixtime_to_tz_tw(i_time):
  _s = str(i_time)
  year = int(_s[:4])
  month = int(_s[4:6])
  day = int(_s[6:8])
  hour = int(_s[8:10])
  minute = int(_s[10:12])
  sec = int(_s[12:14])
  
  dt = datetime(year, month, day, hour, minute, sec)
  dt = TZ_TW.localize(dt)
  return dt

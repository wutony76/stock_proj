from __future__ import print_function
import traceback
import threading
import random
import rwlock
import Queue
from datetime import datetime
import time
import pytz
from fatcat.conf import settings as _settings
from fdpays.commit_notify import CommitNotifyManager
from fdstock.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw, ixtime_to_tz_tw
from fdstock.seqid import SeqIDGenerator
from fdstock.rpcclient import RPCClientPool


def spawn(func):
  th = threading.Thread(target=func)
  th.setDaemon(True)
  th.start()

FMT_DATA_INDEX2 = '%08x:%016x'
FMT_DATA_INDEX3 = '%08x:%016x:%016x'
FMT_DATA_INDEX4 = '%08x:%016x:%016x:%016x'

MAX_INT64 = 0xffffffffffffffff

class DataIndexOpts:
  SCHEMA = 1


  STOCK_ROWDATA = 301

  EQUITY_DATA = 501

  STOCK_TIMELINE_INDEX = 601
  STOCK_TIMELINE_DATA = 602
  STOCK_TIMELINE_VERSION = 603


  MINUTE_VERSION = 701
  
  SYNC_MINUTE_VERSION = 702

  STOCK_MINUTE_DATA = 711

class SchemaOpts:
  LAST_SEQ = 1

class SeqType:
  OBJ_ID = 1
  ROW_ID = 2

class DataSet(object):
  
  def __init__(self, tdb):
    self.tdb = tdb

    self.seqid_gen = SeqIDGenerator(0x10a, 0)

    self.schema = tdb.new_oobtree(11, max_leaf_size=1024, max_internal_size=1024)

    self.data_index2_128 = tdb.new_oobtree(25, max_leaf_size=128, max_internal_size=1024)
    self.data_index2_192 = tdb.new_oobtree(26, max_leaf_size=192, max_internal_size=1024)
    self.data_index2_256 = tdb.new_oobtree(27, max_leaf_size=256, max_internal_size=1024)
    self.data_index2_512 = tdb.new_oobtree(28, max_leaf_size=512, max_internal_size=1024)
    self.data_index2_768 = tdb.new_oobtree(29, max_leaf_size=768, max_internal_size=1024)

    self.data_index3_16 = tdb.new_oobtree(42, max_leaf_size=16, max_internal_size=1024)
    self.data_index3_32 = tdb.new_oobtree(43, max_leaf_size=32, max_internal_size=1024)
    self.data_index3_64 = tdb.new_oobtree(44, max_leaf_size=64, max_internal_size=1024)
    self.data_index3_128 = tdb.new_oobtree(45, max_leaf_size=128, max_internal_size=1024)
    self.data_index3_192 = tdb.new_oobtree(46, max_leaf_size=192, max_internal_size=1024)
    self.data_index3_256 = tdb.new_oobtree(47, max_leaf_size=256, max_internal_size=1024)
    self.data_index3_512 = tdb.new_oobtree(48, max_leaf_size=512, max_internal_size=1024)
    self.data_index3_768 = tdb.new_oobtree(49, max_leaf_size=768, max_internal_size=1024)
    self.data_index3_1024 = tdb.new_oobtree(50, max_leaf_size=1024, max_internal_size=1024)

    self.data_index4_512 = tdb.new_oobtree(68, max_leaf_size=512, max_internal_size=1024)
    self.data_index4_768 = tdb.new_oobtree(69, max_leaf_size=768, max_internal_size=1024)
    self.data_index4_1024 = tdb.new_oobtree(70, max_leaf_size=1024, max_internal_size=1024)


    self.equity_id_by_code = tdb.new_oobtree(101, max_leaf_size=512, max_internal_size=1024)

    self.leaf_size = 128
    self.branch1_size = 512
    self.branch2_size = 512

    self.branch1_size2 = self.leaf_size * self.branch1_size
    self.branch2_size2 = self.leaf_size * self.branch1_size * self.branch2_size

    self.fwd_index = self.data_index3_1024
    self.version_index = self.data_index3_1024
    self.rowdata_index = self.data_index2_192
    self.timeline_index = self.data_index3_1024

    self.minute_version_index = self.data_index4_768
    self.sync_minute_version_index = self.data_index4_768
    self.minute_data_index = self.data_index3_192


  def commit(self):
    self.tdb.commit()

  def new_obj_id(self):
    i_k = FMT_DATA_INDEX3 % (DataIndexOpts.SCHEMA, SchemaOpts.LAST_SEQ, SeqType.OBJ_ID)
    obj_id = self.data_index3_512.get(i_k, 0) + 1
    self.data_index3_512[i_k] = obj_id
    return obj_id

  def new_row_id(self):
    i_k = FMT_DATA_INDEX3 % (DataIndexOpts.SCHEMA, SchemaOpts.LAST_SEQ, SeqType.ROW_ID)
    obj_id = self.data_index3_512.get(i_k, 0) + 1
    self.data_index3_512[i_k] = obj_id
    return obj_id



class Request(object):
  def __init__(self, args, txn):
    self.args = args
    self.txn = txn

class SyncRows(object):
  
  def __init__(self, factory):
    self.factory = factory
    self.lock = factory.lock
    self.txnmgr = factory.txnmgr
    self.cli_pool = RPCClientPool(_settings.FDSTOCK_TWSE_DB_ADDR)

  def run(self):
    change_counter = 0
    with self.cli_pool.connection() as cli:
      branch2_vsets = cli.call('ALL_BRANCH2_VSETS')
      #print('ALL_BRANCH2_VERSION_SET', branch2_vsets)
      with self.txnmgr.get_request() as txn:
        with self.lock.writer_lock:
          db = txn.db 
          for branch2_id, branch2_version in branch2_vsets:

            branch1_vsets = cli.call('GET_BRANCH1_VSETS', branch2_id)[0]
            print('GET_BRANCH1_VSETS', branch1_vsets)

            for branch1_id, branch1_version in branch1_vsets:
              i_version = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_VERSION, 1, branch1_id)
              version = db.version_index.get(i_version, None) 

              is_update = False

              if version != branch1_version:
                is_update = True

              if is_update == True:
              
                leaf_vsets = cli.call('GET_LEAF_VSETS', branch1_id)[0]
                #print('GET_LEAF_VSETS', leaf_vsets)
                _counter = self._sync_leaf(leaf_vsets, db, cli)
                change_counter += _counter

                db.version_index[i_version] = branch1_version 

                txn.notify_changed(0, 1)

                if change_counter > 16384:
                  return change_counter

    return change_counter

  def _sync_leaf(self, leaf_vsets, db, cli):
    change_counter = 0

    for leaf_id, leaf_version in leaf_vsets:
      i_version = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_VERSION, 0, leaf_id)
      version = db.version_index.get(i_version, None) 
      is_update = False
      if version != leaf_version:
        is_update = True

      if is_update == True:
        rows = cli.call('GET_LEAF_ROWS', leaf_id)[0]
        #print('leaf_id=%s version=%s/%s' % (leaf_id, version, leaf_version), 'rows', len(rows))
        for i in xrange(0, len(rows), 2):
          row_id = rows[i]
          row = rows[i+1]

          self.update_row(db, leaf_id, row_id, row)

          change_counter += 1

        db.version_index[i_version] = leaf_version 

    return change_counter

  def update_row(self, db, leaf_id, row_id, row):
    code = row['c']
    uts = int(row['tlong'])

    try:
      eqid = db.equity_id_by_code[code]
    except KeyError:
      eqid = db.new_obj_id()
      db.equity_id_by_code[code] = eqid

    #print('SYNC row_id=%s leaf_id=%s code=%s' % (row_id, leaf_id, code))
    i_row = FMT_DATA_INDEX2 % (DataIndexOpts.STOCK_ROWDATA, row_id)
    db.rowdata_index[i_row] = row

    i_timeline = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_INDEX, eqid, uts)
    db.timeline_index[i_timeline] = row_id
    
    #走勢圖
    ts = uts / 1000
    dt = ts_to_tz_tw(ts)

    t_key0 = int(dt.strftime('%Y%m%d%H%M'))
    t_key1 = int(dt.strftime('%Y%m%d%H'))
    t_key2 = int(dt.strftime('%Y%m%d'))
    t_key3 = int(dt.strftime('%Y%m'))

    keys = [
      (0, t_key0),
      (1, t_key1),
      (2, t_key2),
      (3, t_key3),
    ]

    print('SYNC row_id=%s dt' % row_id, dt, 't_key', t_key3, t_key2, t_key1, t_key0)
    for depth, _key in keys:
      i_v = FMT_DATA_INDEX4 % (DataIndexOpts.MINUTE_VERSION, depth, eqid, _key)
      db.minute_version_index[i_v] = db.seqid_gen.next_id()

class Loop(object):

  def __init__(self, factory):
    self.factory = factory
    self.lock = factory.lock
    self.txnmgr = factory.txnmgr
    self.cli_pool = RPCClientPool(_settings.FDSTOCK_TWSE_DB_ADDR)

  def __call__(self):
    que = Queue.Queue()

    sync_rows = SyncRows(self.factory)


    while True:
      loop_delay = 1

      try:
        change_counter = sync_rows.run()
        if change_counter > 0:
          loop_delay = 0.2
      except Exception as ex:
        print('ex', ex)

      self._sync_month()

      try:
        que.get(timeout=loop_delay)
      except Queue.Empty:
        pass

  def _sync_month(self):
    with self.txnmgr.get_request() as txn:
      with self.lock.writer_lock:
        db = txn.db 

        i_start = FMT_DATA_INDEX4 % (DataIndexOpts.MINUTE_VERSION, 3, 0, 0)
        i_end = FMT_DATA_INDEX4 % (DataIndexOpts.MINUTE_VERSION, 3, MAX_INT64, MAX_INT64)

        items = []

        for k, v in db.minute_version_index.items(i_start, i_end):
          a, b, c, d = k.split(':')
          eqid = int(c, 16)
          tkey = int(d, 16)

          items.append((eqid, tkey, v))

        for eqid, tkey3, version3 in items:
          i_version = FMT_DATA_INDEX4 % (DataIndexOpts.SYNC_MINUTE_VERSION, 3, eqid, tkey3)
          sync_version = db.sync_minute_version_index.get(i_version, None)

          is_update = False
          if sync_version != version3:
            is_update = True

          if is_update == True:
            print('SYNC_MINUTE eqid=%s tkey3=%s version3=%s' % (eqid, tkey3, version3))
            self._update_day(db, eqid, tkey3)
            db.sync_minute_version_index[i_version] = version3

  def _update_day(self, db, eqid, tkey3):
    
    _start = int('%s00' % tkey3)
    _end = int('%s99' % tkey3)
    
    i_start = FMT_DATA_INDEX4 % (DataIndexOpts.MINUTE_VERSION, 2, eqid, _start)
    i_end = FMT_DATA_INDEX4 % (DataIndexOpts.MINUTE_VERSION, 2, eqid, _end)
    print('update_day', _start, _end)

    items = []

    for k, v in db.minute_version_index.items(i_start, i_end):
      a, b, c, d = k.split(':')
      eqid = int(c, 16)
      tkey2 = int(d, 16)

      items.append((tkey2, v))

    for tkey2, version2 in items:
      i_version = FMT_DATA_INDEX4 % (DataIndexOpts.SYNC_MINUTE_VERSION, 2, eqid, tkey2)
      sync_version = db.sync_minute_version_index.get(i_version, None)
      is_update = False
      if sync_version != version2:
        is_update = True

      if is_update == True:
        self._update_hour(db, eqid, tkey2)
        db.sync_minute_version_index[i_version] = version2

  def _update_hour(self, db, eqid, tkey2):
    
    _start = int('%s00' % tkey2)
    _end = int('%s99' % tkey2)
    print('_update_hour eqid=%s tkey2=%s start=%s end=%s' % (eqid, tkey2, _start, _end)) 

    i_start = FMT_DATA_INDEX4 % (DataIndexOpts.MINUTE_VERSION, 1, eqid, _start)
    i_end = FMT_DATA_INDEX4 % (DataIndexOpts.MINUTE_VERSION, 1, eqid, _end)

    items = []

    for k, v in db.minute_version_index.items(i_start, i_end):
      a, b, c, d = k.split(':')
      eqid = int(c, 16)
      tkey1 = int(d, 16)

      items.append((tkey1, v))

    for tkey1, version1 in items:
      i_version = FMT_DATA_INDEX4 % (DataIndexOpts.SYNC_MINUTE_VERSION, 1, eqid, tkey1)
      sync_version = db.sync_minute_version_index.get(i_version, None)
      is_update = False
      if sync_version != version1:
        is_update = True

      if is_update == True:
        self._update_minute(db, eqid, tkey1)
        db.sync_minute_version_index[i_version] = version1

  def _update_minute(self, db, eqid, tkey1):
    _start = int('%s00' % tkey1)
    _end = int('%s99' % tkey1)


    start_dt = ixtime_to_tz_tw(str(_start))
    end_dt = ixtime_to_tz_tw(str(_end))

    print('_update_m0 eqid=%s tkey1=%s start=%s end=%s' % (eqid, tkey1, _start, _end), start_dt, end_dt) 
    i_start = FMT_DATA_INDEX4 % (DataIndexOpts.MINUTE_VERSION, 0, eqid, _start)
    i_end = FMT_DATA_INDEX4 % (DataIndexOpts.MINUTE_VERSION, 0, eqid, _end)

    items = []

    for k, v in db.minute_version_index.items(i_start, i_end):
      a, b, c, d = k.split(':')
      eqid = int(c, 16)
      tkey0 = int(d, 16)

      items.append((tkey0, v))

    for tkey0, version0 in items:
      i_version = FMT_DATA_INDEX4 % (DataIndexOpts.SYNC_MINUTE_VERSION, 0, eqid, tkey0)
      sync_version = db.sync_minute_version_index.get(i_version, None)

      is_update = False
      if sync_version != version0:
        is_update = True

      if is_update == True:

        _start = '%s00' % tkey0
        _end = '%s99' % tkey0

        start_dt = ixtime_to_tz_tw(str(_start))
        end_dt = ixtime_to_tz_tw(str(_end))
        
        start_uts = int(dt_to_ts(start_dt) * 1000)
        end_uts = int(dt_to_ts(end_dt) * 1000)

        i_start = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_INDEX, eqid, start_uts)
        i_end = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_INDEX, eqid, end_uts)
        row_ids = []
        for k, row_id in db.timeline_index.items(i_start, i_end):
          row_ids.append(row_id)
        
        #print('SYNC_MINUTE eqid=%s tkey0=%s row_ids=%s' % (eqid, tkey0, len(row_ids)), 'start_uts', start_uts, end_uts)
        if True:
          rows = []
          for row_id in row_ids:
            i_row = FMT_DATA_INDEX2 % (DataIndexOpts.STOCK_ROWDATA, row_id)
            row = db.rowdata_index[i_row]
            rows.append(row)

          rows = sorted(rows, key=lambda r: r['uts'])
          #print('SYNC_MINUTE tkey0=%s row_id=%s' % (tkey0, row_id))
          print('SYNC_MINUTE eqid=%s tkey0=%s rows=%s' % (eqid, tkey0, len(rows)), 'start_uts', start_uts, end_uts)
          last_row = rows[-1]
          last_trade_price = float(last_row['z'])
          total_trade_volume = 0
          for row in rows:
            trade_volume = float(last_row['tv'])
            total_trade_volume += trade_volume

          m_data = {
            'tkey': tkey0,
            'total_trade_volume': total_trade_volume,
            'last_trade_price': last_trade_price,
          }

          i_k = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_MINUTE_DATA, eqid, tkey0)
          db.minute_data_index[i_k] = m_data
          
        
        db.sync_minute_version_index[i_version] = version0

class Factory(object):
  def __init__(self, tdb):


    self.db = DataSet(tdb)

    self.lock = rwlock.RWLock()
    self.txnmgr = CommitNotifyManager(self.db)


  def setup(self, serverfactory):

    self.serverfactory = serverfactory
    self._loop = Loop(self)

    spawn(self.txnmgr.run)
    spawn(self._loop)


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
  
  ##
  def handle_command_ITEMS_STOCK_MINUTE_DATA(self, req):
    txn = req.txn
    args = req.args
    db = txn.db

    out = []

    print('TIMELINE_ITEMS_STOCK_MINUTE_DATA', args)

    with self.lock.reader_lock:
      for i in xrange(0, len(args), 3):
        eq_code = args[i]
        start_key = args[i+1]
        end_key = args[i+2]

        rtn = []

        try:
          eqid = db.equity_id_by_code[eq_code]
        except KeyError:
          eqid = None


        print('TIMELINE_ITEMS_STOCK_MINUTE_DATA code=%s eqid=%s' % (eq_code, eqid), start_key, end_key)

        if eqid is not None:
          i_start = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_MINUTE_DATA, eqid, start_key)
          i_end = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_MINUTE_DATA, eqid, end_key)
          for k, v in db.minute_data_index.items(i_start, i_end):
            rtn.append(v)

        out.append(rtn)

    return out

  def handle_command_TIMELINE_ITEMS(self, req):
    txn = req.txn
    args = req.args
    db = txn.db

    out = []

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

          for k, row_id in db.timeline_index.items(i_start, i_end):
            i_row = FMT_DATA_INDEX2 % (DataIndexOpts.STOCK_ROWDATA, row_id)
            row = db.rowdata_index[i_row]
            rtn.append(row)

        out.append(rtn)

    return out



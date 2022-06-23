from __future__ import print_function
import traceback
import threading
import random
import rwlock
import queue as Queue
from datetime import datetime
import time
import pytz
from fcworks.conf import settings as _settings
#from fatcat.conf import settings as _settings
from fdpays.commit_notify import CommitNotifyManager
from fdstock.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw
from fdstock.seqid import SeqIDGenerator


def spawn(func):
  th = threading.Thread(target=func)
  th.setDaemon(True)
  th.start()

FMT_DATA_INDEX2 = '%08x:%016x'
FMT_DATA_INDEX3 = '%08x:%016x:%016x'

MAX_INT64 = 0xffffffffffffffff

class DataIndexOpts:
  SCHEMA = 1

  EQUITY_DATA = 501

  STOCK_TIMELINE_INDEX = 601
  STOCK_TIMELINE_DATA = 602
  STOCK_TIMELINE_VERSION = 603

class SchemaOpts:
  LAST_SEQ = 1

class SeqType:
  OBJ_ID = 1
  ROW_ID = 2

class DataSet(object):
  
  def __init__(self, tdb):
    self.tdb = tdb

    self.schema = tdb.new_oobtree(11, max_leaf_size=1024, max_internal_size=1024)

    self.data_index2_128 = tdb.new_oobtree(25, max_leaf_size=128, max_internal_size=1024)
    self.data_index2_192 = tdb.new_oobtree(26, max_leaf_size=192, max_internal_size=1024)
    self.data_index2_256 = tdb.new_oobtree(27, max_leaf_size=256, max_internal_size=1024)
    self.data_index2_512 = tdb.new_oobtree(28, max_leaf_size=512, max_internal_size=1024)

    self.data_index3_16 = tdb.new_oobtree(32, max_leaf_size=16, max_internal_size=1024)
    self.data_index3_32 = tdb.new_oobtree(33, max_leaf_size=32, max_internal_size=1024)
    self.data_index3_64 = tdb.new_oobtree(34, max_leaf_size=64, max_internal_size=1024)
    self.data_index3_128 = tdb.new_oobtree(35, max_leaf_size=128, max_internal_size=1024)
    self.data_index3_192 = tdb.new_oobtree(36, max_leaf_size=192, max_internal_size=1024)
    self.data_index3_256 = tdb.new_oobtree(37, max_leaf_size=256, max_internal_size=1024)
    self.data_index3_512 = tdb.new_oobtree(38, max_leaf_size=512, max_internal_size=1024)
    self.data_index3_1024 = tdb.new_oobtree(39, max_leaf_size=1024, max_internal_size=1024)

    self.equity_id_by_code = tdb.new_oobtree(101, max_leaf_size=512, max_internal_size=1024)

    self.leaf_size = 128
    self.branch1_size = 512
    self.branch2_size = 512

    self.branch1_size2 = self.leaf_size * self.branch1_size
    self.branch2_size2 = self.leaf_size * self.branch1_size * self.branch2_size

    self.fwd_index = self.data_index3_1024
    self.version_index = self.data_index3_1024
    self.data_index = self.data_index2_128


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

class Factory(object):
  def __init__(self, tdb):

    self.seqid_gen = SeqIDGenerator(0x10a, 0)

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
  
  ##
  def handle_command_ALL_BRANCH2_VSETS(self, req):
    txn = req.txn
    args = req.args
    db = txn.db

    out = []
    with self.lock.reader_lock:
      i_start = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_VERSION, 2, 0)
      i_end = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_VERSION, 2, MAX_INT64)
      for k, version in db.version_index.items(i_start, i_end):
        a, b, c = k.split(':')
        branch2_id = int(c, 16)
        out.append((branch2_id, version))

    return out

  def handle_command_GET_BRANCH1_VSETS(self, req):
    txn = req.txn
    args = req.args
    db = txn.db

    out = []
    with self.lock.reader_lock:
      for i in xrange(0, len(args), 1):
        branch2_id = args[i]

        branch1_id_start = branch2_id * db.branch2_size
        branch1_id_end = branch1_id_start + db.branch2_size - 1

        i_start = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_VERSION, 1, branch1_id_start)
        i_end = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_VERSION, 1, branch1_id_end)

        rtn = []
        for k, version in db.version_index.items(i_start, i_end):
          a, b, c = k.split(':')
          branch1_id = int(c, 16)
          rtn.append((branch1_id, version))

        out.append(rtn)

    return out

  def handle_command_GET_LEAF_VSETS(self, req):
    txn = req.txn
    args = req.args
    db = txn.db

    out = []
    with self.lock.reader_lock:
      for i in xrange(0, len(args), 1):
        branch1_id = args[i]

        leaf_id_start = branch1_id    * db.branch1_size
        leaf_id_end   = leaf_id_start + db.branch1_size - 1
        print('GET_LEAF_VSETS branch1_id=%s' % branch1_id, leaf_id_start, leaf_id_end)

        i_start = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_VERSION, 0, leaf_id_start)
        i_end = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_VERSION, 0, leaf_id_end)
        rtn = []
        for k, version in db.version_index.items(i_start, i_end):
          a, b, c = k.split(':')
          leaf_id = int(c, 16)
          rtn.append((leaf_id, version))

        out.append(rtn)

    return out


  ###
  def handle_command_GET_LEAF_ROWS(self, req):
    txn = req.txn
    args = req.args
    db = txn.db

    out = []
    with self.lock.reader_lock:
      for i in xrange(0, len(args), 1):
        leaf_id = args[i]

        rtn = []

        rowid_start = leaf_id * db.leaf_size
        rowid_end = rowid_start + db.leaf_size - 1

        i_start = FMT_DATA_INDEX2 % (DataIndexOpts.STOCK_TIMELINE_DATA, rowid_start)
        i_end = FMT_DATA_INDEX2 % (DataIndexOpts.STOCK_TIMELINE_DATA, rowid_end)

        for k, info in db.data_index.items(i_start, i_end):
          a, b = k.split(':')
          row_id = int(b, 16)
          rtn.append(row_id)
          rtn.append(info)

        out.append(rtn)

    return out


  def handle_command_TIMELINE_UPDATE(self, req):
    out = []

    txn = req.txn
    args = req.args

    db = txn.db


    with self.lock.writer_lock:
      for i in xrange(0, len(args), 3):
        equity_code = args[i]
        uts = args[i+1]
        info = args[i+2]

        try:
          eqid = db.equity_id_by_code[equity_code]
        except KeyError:
          eqid = db.new_obj_id()
          db.equity_id_by_code[equity_code] = eqid

        rtn = None


        i_fwd = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_INDEX, eqid, uts)
        try:
          row_id = db.fwd_index[i_fwd]
        except KeyError:
          row_id = db.new_row_id()
          db.fwd_index[i_fwd] = row_id

        info['_id'] = row_id

        i_data = FMT_DATA_INDEX2 % (DataIndexOpts.STOCK_TIMELINE_DATA, row_id)
        db.data_index[i_data] = info

        #print('info', info)

        leaf_ids = [
          row_id // db.leaf_size,
          row_id // db.branch1_size2,
          row_id // db.branch2_size2,
        ]

        print('UPDATE_TIMELINE code=%s eqid=%s' % (equity_code, eqid), 'leaf_ids', leaf_ids)

        for depth, leaf_id in enumerate(leaf_ids):
          i_version = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_VERSION, depth, leaf_id)
          db.version_index[i_version] = self.seqid_gen.next_id()

        rtn = row_id

        out.append(rtn)

      txn.notify_changed(0, 1)
    return out


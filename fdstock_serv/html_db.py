from __future__ import print_function
import time
import traceback
import threading
import random
import rwlock
import Queue
from datetime import datetime
import time
import pytz
import requests
from zodbpickle import pickle
from fatcat.conf import settings as _settings
from fdpays.commit_notify import CommitNotifyManager
from fdstock.seqid import SeqIDGenerator, unpack_ts


def spawn(func):
  th = threading.Thread(target=func)
  th.setDaemon(True)
  th.start()

FMT_DATA_INDEX2 = '%08x:%016x'
FMT_DATA_INDEX3 = '%08x:%016x:%016x'
MAX_INT64 = 0xffffffffffffffff

class DataIndexOpts:
  SCHEMA = 1

  LINKED_STR_META = 31
  LINKED_STR_DATA = 32


  REQ_DATA = 201

class SchemaOpts:
  LAST_SEQ = 1

class DataSet(object):
  
  def __init__(self, tdb):
    self.tdb = tdb

    self.schema = tdb.new_oobtree(11, max_leaf_size=1024, max_internal_size=1024)

    self.data_index2_512 = tdb.new_oobtree(27, max_leaf_size=512, max_internal_size=1024)

    self.data_index3_16 = tdb.new_oobtree(32, max_leaf_size=16, max_internal_size=1024)
    self.data_index3_32 = tdb.new_oobtree(33, max_leaf_size=32, max_internal_size=1024)
    self.data_index3_64 = tdb.new_oobtree(34, max_leaf_size=64, max_internal_size=1024)
    self.data_index3_128 = tdb.new_oobtree(35, max_leaf_size=128, max_internal_size=1024)
    self.data_index3_256 = tdb.new_oobtree(36, max_leaf_size=256, max_internal_size=1024)
    self.data_index3_512 = tdb.new_oobtree(37, max_leaf_size=512, max_internal_size=1024)

    #self.reqid_by_key = tdb.new_oobtree(301, max_leaf_size=256, max_internal_size=1024)
    self.expire_index = tdb.new_oobtree(201, max_leaf_size=512, max_internal_size=1024)

    self.data_id_by_key_index = {}

    for qid in range(4096):
      oid = qid + 1024 
      data_id_by_key = tdb.new_oobtree(oid, max_leaf_size=512, max_internal_size=1024)
      self.data_id_by_key_index[qid] = data_id_by_key


  def commit(self):
    self.tdb.commit()

  def new_obj_id(self):
    i_k = FMT_DATA_INDEX3 % (DataIndexOpts.SCHEMA, SchemaOpts.LAST_SEQ, 0)
    obj_id = self.data_index3_512.get(i_k, 0) + 1
    self.data_index3_512[i_k] = obj_id
    return obj_id

  def get_lnkstr(self, obj_id):
    meta_index = self.data_index2_512
    data_index = self.data_index3_256
    i_meta = FMT_DATA_INDEX2 % (DataIndexOpts.LINKED_STR_META, obj_id)
    try:
      meta = meta_index[i_meta]
    except KeyError:
      meta = None
    if meta is not None:
      data_id = meta['data_id']
      i_start = FMT_DATA_INDEX3 % (DataIndexOpts.LINKED_STR_DATA, data_id, 0)
      i_end = FMT_DATA_INDEX3 % (DataIndexOpts.LINKED_STR_DATA, data_id, MAX_INT64)

      out = ''
      for k, v in data_index.items(i_start, i_end):
        out += v

      return out

  def set_lnkstr(self, obj_id, data):

    meta_index = self.data_index2_512
    data_index = self.data_index3_256

    i_meta = FMT_DATA_INDEX2 % (DataIndexOpts.LINKED_STR_META, obj_id)
    try:
      meta = meta_index[i_meta]
    except KeyError:
      meta = {}

    try:
      data_id = meta['data_id']
    except KeyError:
      data_id = None

    if data_id is not None:
      self.pop_lnkstr_data(data_id)

    data_id2 = self.new_obj_id()
    chunk_size = 512
    for i in xrange(0, len(data), chunk_size):
      chunk = data[i:i+chunk_size]
      i_chunk = FMT_DATA_INDEX3 % (DataIndexOpts.LINKED_STR_DATA, data_id2, i)
      data_index[i_chunk] = chunk

    meta['data_id'] = data_id2
    meta_index[i_meta] = meta

    return data_id2

  def pop_lnkstr(self, obj_id):
    meta_index = self.data_index2_512
    data_index = self.data_index3_256

    i_meta = FMT_DATA_INDEX2 % (DataIndexOpts.LINKED_STR_META, obj_id)
    try:
      meta = meta_index[i_meta]
    except KeyError:
      meta = None

    if meta is not None:
      meta_index.pop(i_meta)

      data_id = meta['data_id']
      self.pop_lnkstr_data(data_id)
      print('POP LNKSTR', obj_id)

  def pop_lnkstr_data(self, data_id):
    data_index = self.data_index3_256
    i_start = FMT_DATA_INDEX3 % (DataIndexOpts.LINKED_STR_DATA, data_id, 0)
    i_end = FMT_DATA_INDEX3 % (DataIndexOpts.LINKED_STR_DATA, data_id, MAX_INT64)
    keys = []
    for k, v in data_index.items(i_start, i_end):
      keys.append(k)
    for k in keys:
      data_index.pop(k)
    



class Request(object):
  def __init__(self, args, txn):
    self.args = args
    self.txn = txn

class Factory(object):
  def __init__(self, tdb):

    self.db = DataSet(tdb)
    self.seqid_gen = SeqIDGenerator(0x01, 1)

    self.lock = rwlock.RWLock()
    self.txnmgr = CommitNotifyManager(self.db)


  def setup(self, serverfactory):
    self.serverfactory = serverfactory

    spawn(self.txnmgr.run)
    spawn(self._loop)

  def _loop(self):
    
    que = Queue.Queue()

    #EXPIRE_SEC = 60*60*24*3
    EXPIRE_SEC = 60*60*1
    #EXPIRE_SEC = 60 * 10

    while True:
      try:
        que.get(timeout=5)
      except Queue.Empty:
        pass

      with self.txnmgr.get_request() as txn:
        with self.lock.writer_lock:
          db = txn.db


          now_ts = time.time()

          expire_ts = now_ts - EXPIRE_SEC

          items = []

          for k, v in db.expire_index.items():
            ts = unpack_ts(k)
            if ts > expire_ts:
              break
            print('expire k=%s ts=%s' % (k, ts))

            items.append((ts, k, v))
            if len(items) >= 256:
              break

          if items:
            print('expire items', len(items))
            for ts, _id, qid in items:
              dt = now_ts - ts

              data_id_by_key = db.data_id_by_key_index[qid]

              str_id = data_id_by_key.pop(_id)
              db.pop_lnkstr(str_id)
              db.expire_index.pop(_id)
              print('EXPIRE id=%s qid=%s lnkstr=%s dt=%s' % (_id, qid, str_id, dt))

            txn.notify_changed(0, 1)


  def process_command(self, cmd_name, *cmd_args):
    #print(self, 'process_command', cmd_name, seqid, cmd_args)
    func_name = 'handle_command_%s' % cmd_name
    func = getattr(self, func_name, None)

    if func is None:
      raise Exception('no command %s' % cmd_name)

    with self.txnmgr.get_request() as txn:
      #print('handle_command_ORDER_ADD', args)
      req = Request(cmd_args, txn)
      rtn = func(req)

      return rtn


  def handle_command_ITEMS_DATA(self, req):
    txn = req.txn
    args = req.args
    db = txn.db

    print('ITEMS_DATA', args)
    out = []

    with self.lock.reader_lock:
      i = 0
      qid = args[i]
      last_key = args[i+1]
      limit = args[i+2]

      data_id_by_key = db.data_id_by_key_index[qid] 

      for key, data_id in data_id_by_key.items(last_key, excludemin=True):
        data = db.get_lnkstr(data_id)
        out.append((key, data))
        if len(out) >= limit:
          break
        

      return out


  def handle_command_APPEND_DATA(self, req):

    txn = req.txn
    args = req.args
    db = txn.db

    out = []

    with self.lock.writer_lock:
      for i in xrange(0, len(args), 3):
        qid = args[i]
        meta = args[i+1]
        content = args[i+2]

        data_id_by_key = db.data_id_by_key_index[qid] 

        data = pickle.dumps((meta, content))

        _id = self.seqid_gen.next_id()
        data_id = db.new_obj_id()

        data_id_by_key[_id] = data_id
        db.set_lnkstr(data_id, data)

        db.expire_index[_id] = qid

        print('APPEND_DATA', _id, meta)
        out.append(_id)
      txn.notify_changed(0, 1)

      return out




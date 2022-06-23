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
from fcworks.conf import settings as _settings
#from fatcat.conf import settings as _settings
from fdpays.commit_notify import CommitNotifyManager
from fdpays.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw





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


def spawn(func):
  th = threading.Thread(target=func)
  th.setDaemon(True)
  th.start()

FMT_DATA_INDEX2 = '%08x:%016x'
FMT_DATA_INDEX3 = '%08x:%016x:%016x'

FMT_STOCK_CODE_INDEX = '%08x:%08x'
FMT_YFA_DATA_INDEX = '%08x:%08x:%016x'
MAX_INT64 = 0xffffffffffffffff

FMT_EXPONENT_CODE_INDEX = '%08x:%016x'
FMT_EXPONENT_DATA_INDEX = '%08x:%016x:%016x'


class DataIndexOpts:
  SCHEMA = 1

  EQUITY_DATA = 501

  STOCK_TIMELINE_INDEX = 601
  STOCK_TIMELINE_DATA = 602

  STOCK_YFA_INDEX = 901

  AREA_TW = 886

  TW50_LAST_UTS = 887
  EXPINFO_LAST_UTS = 888

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

    #stock
    self.stock_code_by_code = tdb.new_oobtree(103, max_leaf_size=512, max_internal_size=1024)
    self.stock_info_by_code = tdb.new_oobtree(104, max_leaf_size=512, max_internal_size=1024)

    #exponent
    self.exponent_code_by_code = tdb.new_oobtree(105, max_leaf_size=512, max_internal_size=1024)
    self.exponent_info_by_code = tdb.new_oobtree(106, max_leaf_size=512, max_internal_size=1024)

    #tw50-stock
    self.tw50_list_by_code = tdb.new_oobtree(107, max_leaf_size=512, max_internal_size=1024)
    self.tw50_info_by_code = tdb.new_oobtree(108, max_leaf_size=512, max_internal_size=1024)
    self.tw50_last_uts_index = self.data_index2_512 
    self.exp_last_uts_index = self.data_index2_512 

    #bank-rate
    self.bank_info_by_code = tdb.new_oobtree(109, max_leaf_size=512, max_internal_size=1024)


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
    cmd_name = cmd_name.decode()
    
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
    print('-'*50)
    print('handle_command_UPDATE_TIMELINE')

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

        #try:
        #  eqid = db.equity_id_by_code[equity_code]
        #except KeyError:
        #  eqid = None
        #rtn = None
        #print('eqid -', eqid)

        _yfa_index = FMT_YFA_DATA_INDEX % (DataIndexOpts.STOCK_YFA_INDEX, equity_code, uts)
        print('yfa_index = ', _yfa_index)
        try:
          _data = data_index[_yfa_index]
        except:
          _data = {}
        _data.update(info)

        data_index[_yfa_index] = _data
        rtn = _yfa_index

        #if eqid is not None:
        #  i_fwd = FMT_DATA_INDEX3 % (DataIndexOpts.STOCK_TIMELINE_INDEX, eqid, uts)
        #  try:
        #    _id = ts_index[i_fwd]
        #  except KeyError:
        #    _id = db.new_obj_id()
        #    ts_index[i_fwd] = _id

        #  i_data = FMT_DATA_INDEX2 % (DataIndexOpts.STOCK_TIMELINE_DATA, _id)
        #  data_index[i_data] = info
        #  print('UPDATE_TIMELINE code=%s eqid=%s' % (equity_code, eqid), i_fwd, i_data)
        #  print('info', info)
        #  rtn = _id
        out.append(rtn)
      txn.notify_changed(0, 1)
      print('-'*50)
      print('end')
    return out




####################################################################################
  def handle_command_STOCK_CODE(self, req):
    print('handle_command_STOCK_CODE')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db

    with self.lock.reader_lock:
      for k, v in db.stock_code_by_code.items():
        print (" k ", k)
        print (" v ", v)
        out.append(v)
      #for i in xrange(0, len(args), 1):
      #  try:
      #    # get single 
      #    stock_code = args[i]
      #    _code_index = FMT_STOCK_CODE_INDEX % (DataIndexOpts.AREA_TW, stock_code)
      #    _data = db.stock_code_by_code[_code_index]
      #    out.append(_data)
      #    
      #  except:
      #    # get all
      #    for k, v in db.stock_code_by_code.items():
      #      print("v = " ,v)
      #      out.append(v)
    return out


  def handle_command_UPDATE_STOCK_CODE(self, req):
    print('-'*50)
    print('handle_command_UPDATE_STOCK_CODE')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db

    with self.lock.writer_lock:
      for i in xrange(0, len(args), 2):
        stock_code = args[i]
        info = args[i+1]

        _code_index = FMT_STOCK_CODE_INDEX % (DataIndexOpts.AREA_TW, stock_code)
        print('code_index = ', _code_index)
        try:
          _data = db.stock_code_by_code[_code_index]
        except:
          _data = {}
        _data.update(info)

        db.stock_code_by_code[_code_index] = _data
        out.append(_code_index)

      txn.notify_changed(0, 1)
      print('-'*50)
      print('end')
    return out


  def handle_command_STOCK_INFO(self, req):
    print('handle_command_STOCK_INFO')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db

    with self.lock.reader_lock:
      for i in xrange(0, len(args), 1):
        stock_code = args[i]
        i_start = FMT_YFA_DATA_INDEX % (DataIndexOpts.AREA_TW, stock_code, 0)
        i_end = FMT_YFA_DATA_INDEX % (DataIndexOpts.AREA_TW, stock_code, MAX_INT64)

        for k, v in db.stock_info_by_code.items(i_start, i_end):
          print (" k ", k)
          print (" v ", v)
          out.append(v);
    return out


  def handle_command_UPDATE_STOCK_INFO(self, req):
    print('-'*50)
    print('handle_command_UPDATE_STOCK_INFO')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db
    with self.lock.writer_lock:
      for i in xrange(0, len(args), 1):
        stock_info = args[i]
        _yfa_index = FMT_YFA_DATA_INDEX % (DataIndexOpts.AREA_TW, stock_info['code'], stock_info['uts'])
        print('yfa_index = ', _yfa_index)
        try:
          _data = db.stock_info_by_code[_yfa_index]
        except:
          _data = {}
        _data.update(stock_info)

        db.stock_info_by_code[_yfa_index] = _data
        rtn = _yfa_index
        out.append(rtn)
      txn.notify_changed(0, 1)
      print('-'*50)
      print('end')
    return out


# start exponent #
#########################################################
  def handle_command_EXPONENT_CODE(self, req):
    print('handle_command_EXPONENT_CODE')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db

    with self.lock.reader_lock:
      for k, v in db.exponent_code_by_code.items():
        print (" k ", k)
        print (" v ", v)
        out.append(v)
    return out


  def handle_command_UPDATE_EXPONENT_CODE(self, req):
    print('-'*50)
    print('handle_command_UPDATE_EXPONENT_CODE')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db

    with self.lock.writer_lock:
      for i in xrange(0, len(args), 2):
        exponent_code = args[i]
        info = args[i+1]

        _code_36 = int( exponent_code, 36)
        _code_index = FMT_EXPONENT_CODE_INDEX % (DataIndexOpts.AREA_TW, _code_36)
        print('code_index = ', _code_index)
        try:
          _data = db.exponent_code_by_code[_code_index]
        except:
          _data = {}
        _data.update(info)


        db.exponent_code_by_code[_code_index] = _data
        out.append(_code_index)

      txn.notify_changed(0, 1)
      print('-'*50)
      print('end')
    return out


  def handle_command_EXPONENT_INFO(self, req):
    print('handle_command_EXPONENT_INFO')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db


    now_dt = datetime.now()
    _date = datetime(now_dt.year, now_dt.month, now_dt.day, 0, 0, 0)
    unixtime = int( time.mktime(_date.timetuple()) ) - 8*60*60

    with self.lock.reader_lock:
      for i in xrange(0, len(args), 1):
        exponent_code = args[i]
        _code_36 = int( exponent_code, 36)

        i_start = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, unixtime)
        i_end = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, MAX_INT64)

        for k, v in db.exponent_info_by_code.items(i_start, i_end):
          print (" k ", k)
          print (" v ", v)
          out.append(v);
    return out


  def handle_command_UPDATE_EXPONENT_INFO(self, req):
    print('-'*50)
    print('handle_command_UPDATE_EXPONENT_INFO')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db
    with self.lock.writer_lock:
      for i in xrange(0, len(args), 2):
        exponent_code = args[i]
        _code_36 = int( exponent_code, 36)
        exponent_info = args[i+1]

        _yfa_index = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, exponent_info['uts'])
        print('yfa_index = ', _yfa_index)
        try:
          _data = db.exponent_info_by_code[_yfa_index]
        except:
          _data = {}
        _data.update(exponent_info)

        db.exponent_info_by_code[_yfa_index] = _data
        rtn = _yfa_index
        out.append(rtn)
      txn.notify_changed(0, 1)
      print('-'*50)
      print('end')
    return out



  #TWSE_EXPONENT_INFO
  def handle_command_TWSE_EXPONENT_INFO(self, req):
    #print('handle_command_TWSE_EXPONENT_INFO')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db


    now_dt = datetime.now()
    _date = datetime(now_dt.year, now_dt.month, now_dt.day, 0, 0, 0)
    unixtime = int( time.mktime(_date.timetuple()) ) - 8*60*60

    with self.lock.reader_lock:
      for i in range(0, len(args), 1):
        exponent_code = args[i]
        _code_36 = int( exponent_code, 36)

        i_start = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, unixtime)
        i_end = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, MAX_INT64)

        for k, v in db.exponent_info_by_code.items(i_start, i_end):
          #print (" k ", k)
          #print (" v ", v)
          out.append(v);
    return out

  def handle_command_TWSE_EXPONENT_INFO_v2(self, req):
    #print('handle_command_TWSE_EXPONENT_INFO_v2', req.args)
    out = []
    txn = req.txn
    args = req.args
    db = txn.db


    now_dt = datetime.now()
    _date = datetime(now_dt.year, now_dt.month, now_dt.day, 0, 0, 0)
    unixtime = int( time.mktime(_date.timetuple()) ) - 8*60*60

    with self.lock.reader_lock:
      for i in xrange(0, len(args), 1):
        exponent_code = args[i]
        _code_36 = int( exponent_code, 36)

        i_last_uts = FMT_DATA_INDEX2 % (DataIndexOpts.EXPINFO_LAST_UTS, _code_36)
        try:
          last_uts = db.exp_last_uts_index[i_last_uts]
        except KeyError:
          last_uts = None
        
        v = None
        if last_uts is not None:
          i_k = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, last_uts)
          v = db.exponent_info_by_code[i_k]
        out.append(v)

        """
        i_start = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, unixtime)
        i_end = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, MAX_INT64)

        for k, v in db.exponent_info_by_code.items(i_start, i_end):
          #print (" k ", k)
          #print (" v ", v)
          out.append(v);
        """

    return out


  def handle_command_UPDATE_TWSE_EXPONENT_INFO(self, req):
    #print('-'*50)
    #print('handle_command_UPDATE_TWSE_EXPONENT_INFO')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db
    with self.lock.writer_lock:
      for i in range(0, len(args), 2):
        exponent_code = args[i]
        _code_36 = int( exponent_code, 36)
        exponent_info = args[i+1]
        print("exponent_info", exponent_info)
        uts = int(exponent_info[b'uts'])

        _yfa_index = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, uts)
        #print('yfa_index = ', _yfa_index)
        try:
          _data = db.exponent_info_by_code[_yfa_index]
        except:
          _data = {}
        _data.update(exponent_info)

        db.exponent_info_by_code[_yfa_index] = _data

        i_last_uts = FMT_DATA_INDEX2 % (DataIndexOpts.EXPINFO_LAST_UTS, _code_36)
        last_uts = db.exp_last_uts_index.get(i_last_uts, 0)
        if uts >= last_uts:
          #print("UPDATE_TWSE_EXPONENT_INFO", uts)
          db.exp_last_uts_index[i_last_uts] = uts

        rtn = _yfa_index
        out.append(rtn)
      txn.notify_changed(0, 1)
      #print('-'*50)
      #print('end')
    return out







  # --TW50-LIST  
  def handle_command_TW50_LIST(self, req):
    print('handle_command_TW50_LIST')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db
    with self.lock.reader_lock:
      for k, v in db.tw50_list_by_code.items():
        print (" k ", k)
        print (" v ", v)
        if v[b"active"] == True:
          out.append(v)
    return out


  def handle_command_TW50_LIST_KEY(self, req):
    out = []
    txn = req.txn
    args = req.args
    db = txn.db
    with self.lock.reader_lock:
      for k, v in db.tw50_list_by_code.items():
        #print("v", v)
        if v[b"active"] == True:
          out.append(v[b"code"])
    return out




  def handle_command_UPDATE_TW50_LIST(self, req):
    #print('-'*50)
    print('handle_command_UPDATE_TW50_LIST')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db

    with self.lock.writer_lock:
      for k, v in db.tw50_list_by_code.items():
        v.update({"active": False})
      for i in range(0, len(args), 2):
        stock_code = args[i]
        info = args[i+1]
        #updat active = false


        _code_index = FMT_STOCK_CODE_INDEX % (DataIndexOpts.AREA_TW, stock_code)
        print('code_index = ', _code_index)
        try:
          #_data = db.stock_code_by_code[_code_index]
          _data = db.tw50_list_by_code[_code_index]
        except:
          _data = {}
        _data.update(info)
        print('_data = ', _data)


        db.tw50_list_by_code[_code_index] = _data
        out.append(_code_index)

      txn.notify_changed(0, 1)
      #print('-'*50)
      #print('end')
    return out



  # --TW50-LIST-INFO 
  def handle_command_TW50_INFO(self, req):
    #print('handle_command_TW50_INFO')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db


    now_dt = datetime.now()
    _date = datetime(now_dt.year, now_dt.month, now_dt.day, 0, 0, 0)
    unixtime = int( time.mktime(_date.timetuple()) ) - 8*60*60

    with self.lock.reader_lock:
      for i in range(0, len(args), 1):
        exponent_code = args[i]
        print("exponent_code", exponent_code)
        _code_36 = int( exponent_code, 36)

        #i_start = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, 0)
        i_start = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, unixtime)
        i_end = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, MAX_INT64)

        for k, v in db.tw50_info_by_code.items(i_start, i_end):
          print (" k ", k)
          print (" v ", v)
          out.append(v);
    return out

  def handle_command_TW50_INFO_v2(self, req):
    #print('handle_command_TW50_INFO_v2', req.args)
    out = []
    txn = req.txn
    args = req.args
    db = txn.db


    now_dt = datetime.now()
    _date = datetime(now_dt.year, now_dt.month, now_dt.day, 0, 0, 0)
    unixtime = int( time.mktime(_date.timetuple()) ) - 8*60*60

    with self.lock.reader_lock:
      for i in xrange(0, len(args), 1):
        exponent_code = args[i]
        _code_36 = int( exponent_code, 36)

        #i_start = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, 0)
        #i_start = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, unixtime)
        #i_end = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, MAX_INT64)


        i_last_uts = FMT_DATA_INDEX2 % (DataIndexOpts.TW50_LAST_UTS, _code_36)
        rtn = None
        try:
          last_uts = db.tw50_last_uts_index[i_last_uts]
        except KeyError:
          last_uts = None

        if last_uts is not None:
          i_k = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, last_uts)
          rtn = db.tw50_info_by_code[i_k]

        out.append(rtn)
    return out


  def handle_command_UPDATE_TW50_INFO(self, req):
    #print('-'*50)
    #print('handle_command_UPDATE_TW50_INFO')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db


    with self.lock.writer_lock:
      for i in range(0, len(args), 2):
        exponent_code = args[i]
        _code_36 = int( exponent_code, 36)
        exponent_info = args[i+1]

        uts = exponent_info[b'uts']

        _yfa_index = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, uts)
        #print('yfa_index = ', _yfa_index)
        try:
          _data = db.tw50_info_by_code[_yfa_index]
        except:
          _data = {}
        _data.update(exponent_info)

        db.tw50_info_by_code[_yfa_index] = _data

        i_last_uts = FMT_DATA_INDEX2 % (DataIndexOpts.TW50_LAST_UTS, _code_36)
        last_uts = db.tw50_last_uts_index.get(i_last_uts, 0)
       # print("UPDATE_TW50_LAST_UTS", i_last_uts, uts)
        if uts >= last_uts:
          db.tw50_last_uts_index[i_last_uts] = uts
          #print("UPDATE_TW50_LAST_UTS", i_last_uts, uts)

        rtn = _yfa_index
        out.append(rtn)
      txn.notify_changed(0, 1)
      #print('-'*50)
      #print('end')
    return out


  # --Bank-rate-INFO 
  def handle_command_BANK_INFO(self, req):
    #print('handle_command_TW50_INFO')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db

    now_dt = datetime.now()
    _date = datetime(now_dt.year, now_dt.month, now_dt.day, 0, 0, 0)
    unixtime = int( time.mktime(_date.timetuple()) ) - 8*60*60

    with self.lock.reader_lock:
      for i in range(0, len(args), 1):
        exponent_code = args[i]
        _code_36 = int( exponent_code, 36)

        i_start = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, unixtime)
        i_end = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, MAX_INT64)

        for k, v in db.bank_info_by_code.items(i_start, i_end):
          #print (" k ", k)
          #print (" v ", v)
          out.append(v);
    return out


  def handle_command_UPDATE_BANK_INFO(self, req):
    #print('-'*50)
    #print('handle_command_UPDATE_TW50_INFO')
    out = []
    txn = req.txn
    args = req.args
    db = txn.db
    with self.lock.writer_lock:
      for i in range(0, len(args), 2):
        bank_code = args[i]
        _code_36 = int( bank_code, 36)
        bank_info = args[i+1]
        print ("bank_info", bank_info)

        b_uts = int(bank_info[b'uts']) 
        print("b_uts", b_uts)

        _yfa_index = FMT_EXPONENT_DATA_INDEX % (DataIndexOpts.AREA_TW, _code_36, b_uts)
        #print('yfa_index = ', _yfa_index)
        try:
          _data = db.bank_info_by_code[_yfa_index]
        except:
          _data = {}
        _data.update(bank_info)

        db.bank_info_by_code[_yfa_index] = _data
        rtn = _yfa_index
        out.append(rtn)
      txn.notify_changed(0, 1)
      #print('-'*50)
      #print('end')
    return out




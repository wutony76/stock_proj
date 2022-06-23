from __future__ import print_function
import threading
import Queue
import json
import time
import traceback
import requests
from datetime import datetime
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol

from fdstock.rpcclient import RPCClientPool
from fatcat.conf import settings as _settings

from yfa_site import yfaDict as _yfa_dict




db_cli_pool = RPCClientPool(_settings.FDSTOCK_YFA_DB_ADDR)
#print( "TWSE_EXPONENT - ", _yfa_dict.TWSE_EXPONENT )


#--- ws clinet ---#
class ServerProtocol(WebSocketServerProtocol):
  def __init__(self, id, factory, *args, **kwargs):
    super(ServerProtocol, self).__init__()
    self.id = id
    self.factory = factory
    self._send_lock = threading.Lock()

  def onConnect(self, request):
    #print("--onConnect", self)
    pass

  def onOpen(self):
    #print("--onOpen")
    #self.sendMessage(u"Hello, world!".encode('utf8'))
    a = {"text": "12346"}
    str_data = json.dumps(a)
    #print("spend data.", str_data.encode('utf8') )
    #self.sendMessage(u"Hello, world!".encode('utf8'))
    self.sendMessage( str_data.encode('utf8') )

  #-- analyze --#
  def onMessage(self, payload, isBinary):
    #print("--onMessage payload", repr(payload))
    self.factory.analyzeMessage(self.id, repr(payload))

  def onClose(self, wasClean, code, reason):
    #print("--onClose", wasClean, code, reason)
    self.factory.remove_proto(self)

  def __repr__(self):
    return "<Proto id=%s>" % self.id

  def send_data(self, data):
    #print("send_data", data)
    with self._send_lock:
      self.sendMessage( data.encode('utf8') )
      #self.sendMessage(data.encode('utf8'), True)

#--- ws clinet end. ---#



#--- ws serv ---#
class ServerFactory(WebSocketServerFactory):
  def __init__(self, *args, **kwargs):
    super(ServerFactory, self).__init__(*args, **kwargs)
    
    self._lock = threading.Lock()
    self._conn_by_id = {}
    self._last_conn_id = 0

    #data_sample = ["TW50", "EXPONENT"]
    #for sample in data_sample:
    #  loop_thread = threading.Thread(target=self.loop2, args=(sample,))
    #  loop_thread.start()

    loop_thread = threading.Thread(target=self.loop2)
    #loop_thread = threading.Thread(target=self.loop)
    loop_thread.start()
    

  def remove_proto(self, proto):
    with self._lock:
      self._conn_by_id.pop(proto.id)
      #print("REMOVE_PROTO", proto)

  def buildProtocol(self, addr):
    with self._lock:
      _id = self._last_conn_id + 1
      self._last_conn_id = _id
      proto = ServerProtocol(_id, self)
      self._conn_by_id[_id] = proto
      #print("buildProtocol", proto)
      return proto

  def analyzeMessage(self, _id, oriData):
    #print("_id ", _id)
    #print("analyzeMessage ", oriData)
    self._conn_by_id[_id].send_data( "Login success." )
    return None
    

  ### --bank rate 
  def pushBankRate(self, out):
    #print("pushBankRate")
    with db_cli_pool.connection() as db_cli:
      bank_code = "BANKTAIWAN"
      rtn = db_cli.call('BANK_INFO', bank_code)
      #print("BANK_INFO", bank_code, len(rtn))
      listSingleData = rtn[-1]
      #print("BANK_INFO", listSingleData)
      _data = {
        "code": "USDTWD",
        "ts": str(int(listSingleData["uts"])),
        "bid": str(listSingleData["buy_value"]),
        "ask": str(listSingleData["sell_value"]),
      }
      out.append( json.dumps(_data) )
    return out 



  ### --tw50 
  def pushTw50Info(self, out):
  #def pushTw50Info(self, q):
    #print("pushTw50Info")
    #out = []
    t0 = time.time()

    with db_cli_pool.connection() as db_cli:
      tw50_list_keys = db_cli.call('TW50_LIST_KEY')
      #print("tw50_list_keys", len(tw50_list_keys))
      rtn_arr = db_cli.call('TW50_INFO_v2', *tw50_list_keys)

      for key, rtn in zip(tw50_list_keys, rtn_arr):
      #for key in tw50_list_keys:
        stock_code = key
        #rtn = db_cli.call('TW50_INFO', stock_code)
        #print("tw50_info_v2", stock_code, repr(rtn))
        #listSingleData = rtn[-1]
        listSingleData = rtn

        _data = {
          "code": stock_code,
          "ts": str(listSingleData["timestamp"]),
          "bid": str(listSingleData["value"]),
          "ask": str(listSingleData["value"]),
        }
        out.append( json.dumps(_data) )

    print("pushTw50Info ", time.time() - t0)
    #q.put(out)
    return out
        
  ### --exponent 
  def pushStockInfo(self, out):
  #def pushStockInfo(self, q):
    #print("pushStockInfo")
    #out = []
    t0 = time.time()
    now_t = time.time()

    #for k, v in _yfa_dict.IG_EXPONENT.items():

    exp_codes = sorted(_yfa_dict.TWSE_EXPONENT.keys())
    with db_cli_pool.connection() as db_cli:
      rtn_arr = db_cli.call('TWSE_EXPONENT_INFO_v2', *exp_codes)

    #for k, v in _yfa_dict.TWSE_EXPONENT.items():
    for k, rtn in zip(exp_codes, rtn_arr):
      #print ( "_key ", k)
      exponent_code = k
      #print( "db_cli", db_cli )
      #rtn = db_cli.call('TWSE_EXPONENT_INFO', exponent_code)
      #print("twse_exponent_info", exponent_code, len(rtn))
      #listSingleData = rtn[-1]
      listSingleData = rtn
      if listSingleData is None:
        continue

      save_db_ts = listSingleData["_update_ts"]
      exec_dt = now_t - save_db_ts
      print(">>", k, "exec_dt", exec_dt)

      _data = {
        "code": k,
        "ts": str(listSingleData["timestamp"]),
        "bid": str(listSingleData["value"]),
        "ask": str(listSingleData["value"]),
      }
      if exponent_code == "twse01":
        #print(_data)
        pass
      out.append( json.dumps(_data) )
    print("pushStockInfo ", time.time() - t0)
    #q.put(out)
    return out


  #def loop(self):
  #  print("start LOOP. ")
  #  que = Queue.Queue()
  #  
  #  while True:
  #    loop_delay = 1 
  #    dy = datetime.now()
  #    _mod = dy.second % 5
  #    if _mod == 0:
  #      #t0 = time.time()
  #      try:
  #        print(" LOOP is run. ")
  #        print(" WS_conn_client.", len(self._conn_by_id) )
  #        for k, proto in self._conn_by_id.items():
  #          out = self.pushStockInfo()

  #          for _data in out:
  #            proto.send_data(_data)
  #      except:
  #        print("LOOP is down.")

  #      #ts = time.time() -t0
  #      #print("GET- %s"%ts)
  #    #que.get(timeout=loop_delay)      
  #    try:
  #      que.get(timeout=loop_delay)      
  #    except Queue.Empty:
  #      pass      


  def loop2(self, data_state=None):
  #def loop2(self, data_state):
    print("start LOOP2.")
    que = Queue.Queue()
    last_t = time.time()
    while True:
      _tt0 = time.time()

      dy = datetime.now()
      _mod = dy.second % 5
      #print("_mod = ",_mod,  dy)
      dt = time.time() - last_t
      last_t = time.time()
      print("loop2", dt)

      #print(" LOOP2 is run. ")
      #print(" WS_conn_client.", len(self._conn_by_id) )
      if len(self._conn_by_id) > 0:
        t0 = time.time()
        self._do_loop2_work()
        dt = time.time() - t0
        print("-" * 100)
        print("work2 dt", dt)
        #ts = time.time() - t0
        #print( "loop run ts = ", ts )

        try:
          req = requests.get( "http://3.115.201.240:9301/twse", timeout=3)
          req = requests.get( "http://3.115.201.240:9301/tw50", timeout=3)
        except:
          print(" check ws post error.")
      
      dt = time.time() - _tt0
      loop_delay = 1.0 - dt

      if loop_delay > 0:
        #print("loop_delay", loop_delay)
        try:
          que.get(timeout=loop_delay)      
        except Queue.Empty:
          pass      


  def _do_loop2_work(self):
    t0 = time.time()

    out = []
    try:
      out = self.pushTw50Info(out)
      out = self.pushStockInfo(out)
      if False:
        func_list = [self.pushTw50Info, self.pushStockInfo]
        q = Queue.Queue()
        all_thread = []

        for _func in func_list:
          thread = threading.Thread(target=_func, args=(q,))
          thread.start()
          all_thread.append(thread)

        for t in all_thread:
          t.join()

        for _ in range(len(all_thread)):
          t_list = q.get()
          for item in t_list:
            out.append( item )

      #print("result = ",out)
    except Exception as ex:
      traceback.print_stack()
      traceback.print_exc()
      print("loop_ex =", ex.message)

    try:
      out = self.pushBankRate(out)
    except:
      pass
      
    #print( "out:", out, len(out))
    #print( "Now ts:", time.time() )

    if len(out) > 0:
      with self._lock:
        conn_by_id2 = dict(self._conn_by_id)
        for k, proto in conn_by_id2.items():
          try:
            for _data in out:
              proto.send_data(_data)
          except Exception as ex:
            print( proto, "push errors." )
            traceback.print_stack()
            traceback.print_exc()
            print("push_ex =", ex.message)
            continue


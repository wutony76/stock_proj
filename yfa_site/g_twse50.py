from __future__ import print_function
import time
import json
from datetime import datetime
import random
import requests
import gevent
import gevent.lock
import gevent.queue
import msgpack
from fatcat.conf import settings as _settings
from fdstock.rpcclient import RPCClientPool
from yfa_site import yfaDict
from yfa_site.networking import RPCHttpClient


def do_yahoo_req(yahoo_url):

  #print("do_yahoo_req", yahoo_url)
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}

  url = yahoo_url
  _code = url.split('=')[-1]
  req_data = {
    #'response':'csv',
    #'date':_date,
    #'ts':time.time(),
  }

  rep = requests.get(url, params=req_data, headers= headers)
  if rep.status_code != 200:
    return None 

  _data = rep.content

  #---update
  _data.strip()
  t_index = _data.index('"tick"', 100)
  s_t = t_index
  _data = "{"+ _data[s_t:len(_data)-2]

  #-head -back
  if not _data.startswith("{"):
    while not _data.startswith("{"):
      _data = _data[1:len(_data)]
  if not _data.endswith("}"):
    while not _data.endswith("}"):
      _data = _data[0:len(_data)-1]
  load_data = json.loads( _data, strict=False )
  #---update_end

  
  #_data = _data[7:len(_data)-2]
  #load_data = json.loads(_data)
  #print ("tick = ", len( load_data["tick"] ) )

  #out = []
  analyze_data = load_data["tick"][-1]
  #print ("analyze_data = ", analyze_data )

  t = str(analyze_data["t"])
  #print ("t = ", t, len(t) )
  _y = t[0:4]
  _m = t[4:6]
  _d = t[6:8]
  _hr = t[8:10]
  _min = t[10:12]
  _sec = t[12:14]

  #print ( _y, _m, _d, _hr, _min, _sec )
  _date = datetime(int(_y), int(_m), int(_d), int(_hr), int(_min), int(_sec))
  #--- server need -8hr ---#
  unixtime = int( time.mktime(_date.timetuple()) ) - 8*60*60 
  


  #print ( "unixtime ", unixtime )
  ts = unixtime
  p = analyze_data["p"]

  item = {
    'uts': unixtime,
    'timestamp': unixtime,
    'code': _code,

    'time': "%s:%s-%s"%(_hr, _min, _sec),
    'value': p,
  }
  return item

class Main(object):


  def run(self):
    

    root_cli = RPCHttpClient(_settings.FDSTOCK_YFA_G_TWSE50_ROOT_HTTP)
    db_cli_pool = RPCClientPool(_settings.FDSTOCK_YFA_DB_ADDR)
    sample_dict = yfaDict.YAHOO_EXPONENT
    all_keys = sorted(sample_dict.keys())
    print (all_keys)


    gevent.sleep(1)

    last_t = 0

    while True:

      loop_delay = 0.5

      tt0 = time.time()

      try:
        rtn = root_cli.call("WAIT", last_t)
        print("WAIT", rtn)
      except Exception as ex:
        rtn = None
        loop_delay = 2.0
        print("ex", ex)


      if rtn == 1:
        last_t = time.time()

        arr = []

        for k in all_keys:
          v = sample_dict[k]
          url = v["yahoo_url"]

          #print("k",k, "url", url)
          a = gevent.spawn(do_yahoo_req, url)
          arr.append(a)
        
        items = []
        t0 = time.time()
        gevent.joinall(arr)
        for a in arr:
          items.append(a.value)
        dt = time.time() - t0

        print("dt", dt, "items", len(items))
        now_t = time.time()
        call_args = []
        for item in items:
          _code = item['code']
          item["_update_ts"] = now_t
          call_args.append(_code)
          call_args.append(item)

        with db_cli_pool.connection() as db_cli:
          t0 = time.time()
          rtn = db_cli.call('UPDATE_TWSE_EXPONENT_INFO', *call_args)
          dt = time.time() - t0
          print("UPDATE_TWSE_EXPONENT_INFO", dt)

      dt = time.time() - tt0
      delay = loop_delay - dt
      if delay > 0:
        print("loop delay", delay)
        gevent.sleep(delay)


class Request(object):
  
  def __init__(self, env, start_response):
    self.env = env
    self.start_response = start_response


class Root(object):

  def __init__(self):
    self._reqs = []
    self._lock = gevent.lock.Semaphore()

    gevent.spawn(self._loop)

  def _loop(self):

    gevent.sleep(2)

    while True:
      t0 = time.time()

      with self._lock:
        print("reqs", len(self._reqs))
        if len(self._reqs) > 0:
          now_t = time.time()
          for call in self._reqs:
            call.dt = now_t - call.last_t
          reqs = sorted(self._reqs, key=lambda c: c.dt)
          self._reqs = []
          call = reqs.pop()
          call.que.put(1)

          for call in reqs:
            call.que.put(None)

      dt = time.time() - t0
      delay = 1.6 - dt
      if delay > 0:
        print("loop delay", delay)
        gevent.sleep(delay)

  def handle_command_WAIT(self, req, *args):
    
    last_t = args[0]
    call = WaitCall(req, last_t)
    with self._lock:
      self._reqs.append(call)

    return call.que

  def __call__(self, env, start_response):
    req = Request(env, start_response)
    code = 0
    rtn = None
    reason = None
    try:
      _in = env["wsgi.input"]
      data = _in.read()
      pkt = msgpack.unpackb(data)
      print("call",  pkt)
      cmd, args = pkt
      func_name = "handle_command_%s" % cmd
      func = getattr(self, func_name, None)
      if func is None:
        raise Exception("no command handle %s" % cmd)
      rtn = func(req, *args)
      if isinstance(rtn, gevent.queue.Queue):
        rtn = rtn.get(timeout=60)

      code = 0
      reason = None

    except Exception as ex:
      code = 1
      rtn = None
      reason = ex.message

    rep_data = msgpack.packb([code, rtn, reason])

    start_response('200 OK', [('Content-Type', 'application/octet-stream')])
    return rep_data

class WaitCall(object):

  def __init__(self, req, last_t):
    self.req = req
    self.last_t = last_t
    self.que = gevent.queue.Queue()




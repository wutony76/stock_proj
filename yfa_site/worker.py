from __future__ import print_function
import json
import time
from datetime import datetime
import msgpack
import requests
from twisted.internet import reactor, defer
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET


ASYNC_REP = object()


class GetYahooWork(object):
  
  def __init__(self, handle):
    self.handle = handle
    self.que = defer.DeferredQueue()
    self._keys = []
    self._values = []
    self._rtn_by_ask = {}

  def add(self, k, v):
    self._keys.append(k)
    self._values.append(v)

  def start(self):
    ask = 0
    for k, v in zip(self._keys, self._values):
      #print("start GET_YAHOO", item)
      ask = ask + 1

      reactor.callInThread(self._get_yahoo, ask, k, v)

    self.que.get().addCallback(self._callback)

  def _callback(self, a):
    ask, rep = a
    #print(self, "_callback", rep)
    self._rtn_by_ask[ask] = rep

    remaining = len(self._keys) - len(self._rtn_by_ask)

    #print("callback ask=%s remaining=%s" % (ask, remaining))
    if remaining == 0:
      self.on_done()
    else:
      self.que.get().addCallback(self._callback)


  def on_done(self):
    print("[%s] DONE" % (datetime.now(),), self._keys)
    out = []
    for ask in sorted(self._rtn_by_ask.keys()):
      rep = self._rtn_by_ask[ask]
      out.append(rep)

    self.handle.response(0, out, None)



  def _get_yahoo(self, ask, k, yahoo_url):
    #print(self, "_get_yahoo",  k, yahoo_url)
    out = self._get_out(yahoo_url)
    self.que.put((ask, out))

  def _get_out(self, yahoo_url):
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


class HttpNode(Resource):

  isLeaf = True

  def handle_command_GET_YAHOO(self, handle, *args):
    #print("handle_command_GET_YAHOO", args)

    work = GetYahooWork(handle)

    for i in xrange(0, len(args), 2):
      k = args[i]
      v = args[i+1]

      work.add(k, v)

    work.start()

    return ASYNC_REP

  def render_GET(self, request):
    print("render_GET", request)
    return ""

  def process_command(self, handle, data):
    pkt = msgpack.unpackb(data)
    cmd, args = pkt
    func_name = "handle_command_%s" % cmd
    func = getattr(self, func_name, None)
    try:
      if func is None:
        raise Exception("no command %s handle" % cmd)
      rtn = func(handle, *args)
      code = 0
      reason = None
    except Exception as ex:
      code = 1
      rtn = None
      reason = ex.message

    if rtn == ASYNC_REP:
      return rtn

    rep_data = handle.make_response(code, rtn, reason)
    return rep_data

  def render_POST(self, request):
    #print("post", repr(data))

    handle = CommandHandle(request)

    data = request.content.read()
    rtn = self.process_command(handle, data)
    #print("response", repr(rtn))
    if rtn == ASYNC_REP:
      #print("NOT_DONE_YET")
      return NOT_DONE_YET


    return rtn



class CommandHandle(object):

  def __init__(self, request):
    self.request = request


  def make_response(self, code, rtn, reason):
    rep_data = msgpack.packb([code, rtn, reason])
    return rep_data

  def response(self, code, rtn, reason):
    rep_data = self.make_response(code, rtn, reason)
    #print("rep_data", repr(rep_data))
    self.request.write(rep_data)
    self.request.finish()

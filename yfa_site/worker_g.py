from __future__ import print_function
import time
import json
from datetime import datetime
import gevent
import msgpack
import requests


def do_yahoo_req(yahoo_url):

  print("do_yahoo_req", yahoo_url)
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

class App(object):

  def handle_command_GET_YAHOO(self, *args):
    
    #print("handle_command_GET_YAHOO", args)
    arr = []
    for i in xrange(0, len(args), 2):
      k = args[i]
      url = args[i+1]
      #print("k",k, "url", url)
      a = gevent.spawn(do_yahoo_req, url)
      arr.append(a)
    
    out = []
    t0 = time.time()
    gevent.joinall(arr)
    for a in arr:
      print("a", a, a.value)
      out.append(a.value)

    dt = time.time() - t0
    print("dt", dt)
    return out


  def __call__(self, env, start_response):
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
      rtn = func(*args)
      code = 0
      reason = None

    except Exception as ex:
      code = 1
      rtn = None
      reason = ex.message

    rep_data = msgpack.packb([code, rtn, reason])

    start_response('200 OK', [('Content-Type', 'application/octet-stream')])
    return rep_data

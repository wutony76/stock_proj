#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import Queue
import threading
import random
import json
import time
import requests
import traceback

from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.twisted.websocket import WebSocketClientFactory

from fdstock.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw


def spendInfo(spend_data):
  url = 'http://3.115.201.240/api/notify'
  access_key = 'OGQ5NmRhNGItN2MwMS00YzA5LTg1MjctZGY5NzNkYmE2YzUy' 
  params = {
    'access_key': access_key,
    'method': 'tg_notify',
    'message': spend_data,
  }
  requests.post(url, data={
    'params': json.dumps(params),
  })


class TestWSClientProtocol(WebSocketClientProtocol):
  def __init__(self, factory, *args, **kw):
    super(TestWSClientProtocol, self).__init__(*args, **kw)
    self.factory = factory

    self._e_time = time.time()
    self._s_time = time.time()
    self.last_e_time = -1 
    self.last_s_time = -1 

    loop_thread = threading.Thread(target=self.loop2)
    loop_thread.start()

  
  def onConnect(self, rep):
    #print("onConnect", self, rep)
    pass

  def onOpen(self):
    #print("onOpen", self)
    #t = random.uniform(1, 10)
    #reactor.callLater(t, self._on_call_later)
    pass

  def onMessage(self, payload, isBinary):
    #print("--onMessage payload", repr(payload))
    now_time = time.time()
    try:
      json_data = json.loads(payload)
      #print(json_data["code"])

      if json_data["code"] == "twse01":
        self._e_time = now_time
        self.last_e_time = int(json_data["ts"])
        #print(json_data)

      if json_data["code"] == "2330":
        self._s_time = now_time
        self.last_s_time = int(json_data["ts"])
        #print(json_data)

    except Exception as ex:
      #traceback.print_stack()
      #traceback.print_exc()
      print("onMessage_ex =", ex.message)
      #pass
    #self.factory.analyzeMessage(self.id, repr(payload))
    

  def onClose(self, wasClean, code, reason):
    #print("onClose", self, wasClean, code, reason)
    pass

  def _on_call_later(self):
    #print("on_call_later")
    self.transport.loseConnection()


  def loop2(self, data_state=None):
    print("CHECK LOOP2. ")
    que = Queue.Queue()

    while True:
      #loop_delay = 300 
      loop_delay = 600 
      check_time = 300
      now_time = time.time()
      now_dt = ts_to_tz_tw(now_time)
      hr = now_dt.hour #-tw hr


      # -working time-
      if hr >= 8 and hr <= 24:
        if now_time - self._e_time >= check_time:
          spendInfo(u"ttt-指數推送停止")
          print(" not working.")
        if now_time - self._s_time >= check_time:
          spendInfo(u"ttt-50各股推送停止")
          print("stock not working.")

        week = now_dt.strftime("%w")
        #print("week", week)
        #print("hr", hr)
        #print("last_e_time", self.last_e_time)
        #print(now_time - self.last_e_time)
        #print("last_s_time", self.last_s_time)
        #print(now_time - self.last_s_time)


        _minute = now_dt.minute
        #print("_minute = ", _minute)
        ### -Saturday Sunday is rest-
        ### -working is  9 - 13 hr.-
        if week != '6' and week != '0':
          if hr >= 9 and hr <= 13:
            if hr == 13:
              _minute = now_dt.minute
              ### -update to 13.30 end.-
              if _minute > 30:
                try:
                  que.get(timeout=loop_delay)
                except Queue.Empty:
                  pass      

                continue

            ### -refresh stock-
            if self.last_e_time > 0 and now_time - self.last_e_time > check_time:
              spendInfo(u"ttt- 指數抓取停止")
              print("not get e.")
            ### -refresh get tw50-
            if self.last_s_time > 0 and now_time - self.last_s_time > check_time:
              #spendInfo(u"ttt- 50各股抓取停止")   stop tg push message
              print("not get tw50.")
      else:
        print("not working time. %s"%hr)


      try:
        que.get(timeout=loop_delay)
      except Queue.Empty:
        pass      




class TestWebSocketClientFactory(WebSocketClientFactory):
  def __init__(self, *args, **kwargs):
    super(WebSocketClientFactory, self).__init__(*args, **kwargs)
    self._connector = None

  def buildProtocol(self, addr):
    proto = TestWSClientProtocol(self)
    return proto

  def clientConnectionLost(self, connector, reason):
    #print("clientConnectionLost", connector, reason)
    self._connector = connector
    connector.connect()





def main(*args):
  import resource
  soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
  print("RLIMIT_NOFILE", soft, hard)
  resource.setrlimit(resource.RLIMIT_NOFILE, (8192, 8192))
  soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
  print("RLIMIT_NOFILE2", soft, hard)

  host = "3.115.201.240"
  port = 17500
  ws_uri = "ws://%s:%s" % (host, port)

  #for i in xrange(2000):
  factory = TestWebSocketClientFactory(ws_uri)
  reactor.connectTCP(host, port, factory)
  #factory = TestWebSocketClientFactory(ws_uri)
  #reactor.connectTCP(host, port, factory)

  reactor.suggestThreadPoolSize(4096)
  try:
    reactor.run()
  except KeyboardInterrupt:
    reactor.run()


  #factory = WebSocketClientFactory()
  #factory.protocol = ClientProtocol
  #reactor.connectTCP("3.115.201.240", 17500, factory)
  #reactor.run()

if __name__ == "__main__":
  main()



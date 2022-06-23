from __future__ import print_function
import sys
import os
import time


def heartbeat_loop():
  print("heartbeat", time.time())

def main(ws_port):
  from twisted.internet import reactor
  from twisted.internet.task import LoopingCall
  from fatcat.conf import settings as _settings
  from wz.networking.twisted.routerepserv import RouteREPServer
  #from yfa_site.websock.server import GameServerFactory
  from yfa_site.websock.server import ServerFactory
  #from yfa_site.websock.server import GameServerFactory, WSREPFactory


  print("start aksite websocket at :%s" % ws_port)
  #route_id = "ACEKING_SITE_WS00"
  route_id = "FDSTOCK_YFA_WS00"

  reactor.suggestThreadPoolSize(4096)
  ws_url = "ws://0.0.0.0:%s" % ws_port
  #ws_factory = GameServerFactory(route_id, ws_url)
  ws_factory = ServerFactory(ws_url)
  reactor.listenTCP(ws_port, ws_factory)

  looping = LoopingCall(heartbeat_loop)
  looping.start(10)
  try:
    reactor.run()

  except KeyboardInterrupt:
    reactor.stop()



if __name__ == "__main__":
  BASE_DIR = os.path.abspath(os.path.dirname(__file__))
  ROOT_DIR = BASE_DIR
  print("ROOT_DIR", ROOT_DIR)
  sys.path.insert(0, ROOT_DIR)

  sys.path.insert(0, os.path.join(ROOT_DIR, "packages"))
  os.environ.setdefault("FATCAT_ROOT", ROOT_DIR)
  os.environ.setdefault("FATCAT_CONF", "local")

  main(17500)

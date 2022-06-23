from __future__ import print_function
import os, sys
import logging

def main():
  from twisted.internet import reactor
  from fatcat.conf import settings as _settings
  from tabby.tdb import _DB
  from tabby.stuffs._lmdb import LMDBStuff
  from fdstock_serv.brokers import ServerFactory, Server


  port = 17103


  server = Server()

  serverfactory = ServerFactory(0x10a, 11, server)

  server.setup(serverfactory)

  reactor.listenTCP(port, serverfactory, backlog=50)

  print('listen fdstock broker :%s' % port)

  reactor.suggestThreadPoolSize(4096)

  try:
    reactor.run()
  except KeyboardInterrupt:
    reactor.stop()


if __name__ == "__main__":
  BASE_DIR = os.path.abspath(os.path.dirname(__file__))
  #ROOT_DIR = os.path.dirname(BASE_DIR)
  ROOT_DIR = BASE_DIR
  print("ROOT_DIR", ROOT_DIR)

  sys.path.insert(0, ROOT_DIR)
  sys.path.insert(0, os.path.join(ROOT_DIR, "packages"))
  os.environ.setdefault("FATCAT_ROOT", ROOT_DIR)
  os.environ.setdefault("FATCAT_CONF", "local")
  main()

from __future__ import print_function
import os, sys
import logging

def main():
  from twisted.internet import reactor
  from fcworks.conf import settings as _settings
  #from fatcat.conf import settings as _settings
  from tabby.tdb import _DB
  from tabby.stuffs._lmdb import LMDBStuff
  from fdstock.serverfactory import ServerFactory
  from fdstock_serv.yfa_dbserv import Factory
  #from fdstock_serv.dbserv import Factory

  root = logging.getLogger()
  root.setLevel(logging.DEBUG)
  handler = logging.StreamHandler(sys.stdout)
  handler.setLevel(logging.DEBUG)
  root.addHandler(handler)

  storage_name = "fdstock_yfa_db"
  port = 17301
  #port = 17101

  fp = os.path.join(_settings.DATA_DIR, "%s.zodb" % storage_name)
  stuff = LMDBStuff(fp, map_size=2**36)
  tdb = _DB(0x02, stuff, cache_size=512)
  
  print("run db", storage_name)
  server = Factory(tdb)
  serverfactory = ServerFactory(0x10a, 1, server)
  server.setup(serverfactory)

  reactor.listenTCP(port, serverfactory, backlog=50)
  print("listenTCP", port)
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
  os.environ.setdefault("FC_ROOT", ROOT_DIR)
  os.environ.setdefault("FC_CONF", "local")
  main()

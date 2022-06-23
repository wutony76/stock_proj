from __future__ import print_function
import os, sys
import logging

def main():
  from twisted.internet import reactor
  from fatcat.conf import settings as _settings
  from tabby.tdb import _DB
  from tabby.stuffs._lmdb import LMDBStuff
  from fdstock_serv.collect_loop import CollectLoop


  storage_name = "fdstock_collect"

  fp = os.path.join(_settings.DATA_DIR, "%s.zodb" % storage_name)
  stuff = LMDBStuff(fp, map_size=2**36)
  tdb = _DB(0x02, stuff, cache_size=512)

  collect = CollectLoop(tdb)
  collect.run()



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

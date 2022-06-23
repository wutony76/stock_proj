from __future__ import print_function
import os
import sys


def main():

  from gevent.pywsgi import WSGIServer
  from gevent import monkey
  from yfa_site.g_twse50 import Main

  monkey.patch_all()

  main = Main()

  main.run()


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

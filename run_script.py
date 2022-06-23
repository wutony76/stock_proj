from __future__ import print_function
import os, sys

def main():
  BASE_DIR = os.path.abspath(os.path.dirname(__file__))
  ROOT_DIR = BASE_DIR
  print("BASE_DIR", BASE_DIR)
  print("ROOT_DIR", ROOT_DIR)

  sys.path.insert(0, os.path.join(ROOT_DIR, "packages"))

  os.environ.setdefault("FATCAT_ROOT", ROOT_DIR)
  os.environ.setdefault("FATCAT_CONF", "local")

  argv = list(sys.argv)
  argv.pop(0)

  import imp

  srcpath = argv.pop(0)
  print(srcpath)
  
  mod = imp.load_source("test", srcpath)
  mod.main(*argv)

if __name__ == "__main__":
  main()

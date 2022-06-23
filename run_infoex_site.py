from __future__ import print_function
import sys
import os
import random
import threading
from optparse import OptionParser 

def setup():
  BASE_DIR = os.path.abspath(os.path.dirname(__file__))
  ROOT_DIR = BASE_DIR

  sys.path.insert(0, os.path.join(ROOT_DIR, "packages"))
  sys.path.insert(0, os.path.join(ROOT_DIR, "infoex_site"))

  os.environ.setdefault("FATCAT_ROOT", ROOT_DIR)
  os.environ.setdefault("FATCAT_CONF", "local")

  os.environ["DJANGO_SETTINGS_MODULE"] = "infoex_site.settings"

  import django
  django.setup()



def main(port):

  from django.core.handlers.wsgi import WSGIHandler
  from twisted.web import server
  from twisted.web.wsgi import WSGIResource
  from twisted.python.threadpool import ThreadPool
  from twisted.application import service, strports
  from twisted.internet import reactor
  import plotly

  plotly.io.orca.config.executable = '/var/orca'
  plotly.io.orca.config.save()

  opt_parser = OptionParser()
  opt_parser.add_option("-p", "--port", dest="port")

  opts, args = opt_parser.parse_args()

  if opts.port is not None:
    port = int(opts.port)

  reactor.suggestThreadPoolSize(4096)

  application = WSGIHandler()

  wsgi_resource = WSGIResource(reactor, reactor.getThreadPool(), application)

  site = server.Site(wsgi_resource)
  reactor.listenTCP(port, site)

  print("start infoex site at :%s" % port)

  try:
    reactor.run()

  except KeyboardInterrupt:
    reactor.stop()
  


if __name__ == '__main__':
  setup()
  main(17106)

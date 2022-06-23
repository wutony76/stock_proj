from __future__ import print_function


def main():

  from gevent.pywsgi import WSGIServer
  from gevent import monkey
  from yfa_site.worker_g import App

  monkey.patch_all()


  addr = ('0.0.0.0', 17322)
  app = App()

  serv = WSGIServer(addr, application=app)
  try:
    serv.serve_forever()
  except KeyboardInterrupt:
    pass


if __name__ == "__main__":
  main()

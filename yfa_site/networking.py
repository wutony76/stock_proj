from __future__ import print_function
import msgpack
import requests

class RPCHttpClient(object):

  def __init__(self, uri):
    self.uri = uri


  def call(self, cmd, *args):
    pkt = [cmd, args]
    data = msgpack.packb(pkt)
    #print("post", repr(data))

    rep = requests.post(self.uri, data=data)
    rep = msgpack.unpackb(rep.content)
    #print("rep", rep)
    code, rtn, reason = rep
    if code == 0:
      return rtn
    raise Exception(reason)

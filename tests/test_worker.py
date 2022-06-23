from __future__ import print_function
import time
import collections
import msgpack
import requests
from fatcat.conf import settings as _settings
from yfa_site import yfaDict
from yfa_site.networking import RPCHttpClient



def main(*args):
  
  uri = _settings.FDSTOCK_YFA_WORKER_HTTP
  uri = "http://10.0.0.117:17321"
  cli = RPCHttpClient(uri)

  sample_dict = yfaDict.YAHOO_EXPONENT
  sample_dict = collections.OrderedDict(sorted(sample_dict.items()))

  call_args = []

  for k, v in sample_dict.items()[0:16]:
    print("start_get_yahoo_exponent_infos>>", k, v["yahoo_url"])
    call_args.append(k)
    call_args.append(v["yahoo_url"])
  
  t0 = time.time()
  rtn = cli.call("GET_YAHOO", *call_args)
  dt = time.time() - t0
  print("rtn", rtn)
  print("dt", dt)


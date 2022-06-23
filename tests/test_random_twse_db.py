from __future__ import print_function
import time
import random
from datetime import datetime
import pytz
from BTrees import OOBTree
from fatcat.conf import settings as _settings
from fdstock.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw
from fdstock.networking import NetManager
from fdstock.rpcclient import RPCClient
from fdstock_test.twse_faker import Faker

net_mgr = NetManager.get_inst()

def main(*args):

  faker = Faker()

  codes = faker.get_all_codes()

  #start_ts = time.time() - random.randint(2**26, 2**30)
  start_ts = time.time() - random.randint(2**15, 2**17)

  ts = start_ts

  cli = RPCClient(_settings.FDSTOCK_TWSE_DB_ADDR)


  for i in xrange(2**27):

    ts = ts + random.randint(2, 5)

    uts = int(ts*1000)

    call_args = []

    for code in codes:
      
      data = faker.gen(code, uts)
      #print('data', data)
      uts = int(data['tlong'])

      data['uts'] = uts
      data.pop('n')
      data.pop('nf')


      call_args.append(code)
      call_args.append(uts)
      call_args.append(data)

    rtn = cli.call('TIMELINE_UPDATE', *call_args)
    print('TIMELINE_UPDATE', rtn)

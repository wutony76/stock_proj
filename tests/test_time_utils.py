from __future__ import print_function
import time
from datetime import datetime
from fdstock import time_utils

def main(*args):

  ts = time.time()

  now = time_utils.ts_to_tz_tw(ts)
  print('now', ts, now)

  sec = int(now.second // 5) * 5
  dt2 = datetime(now.year, now.month, now.day, now.hour, now.minute, sec) 

  ts2 = time_utils.dt_to_ts(dt)
  print('ts2', ts2)
  

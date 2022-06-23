from __future__ import print_function
from datetime import datetime, timedelta
import time
import pytz
import requests
import csv
from BTrees import OOBTree
from infoex.networking import NetManager
from infoex import twse_utils

net_manager = NetManager.get_inst()

def main(*args):

  it = twse_utils.iter_equities_rows()
  rows = list(it)
  for x in rows:
    print('x', x)

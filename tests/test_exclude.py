from __future__ import print_function
from datetime import datetime
import time
import pytz
from cStringIO import StringIO
import requests
import csv
import pandas as pd
import chardet
from infoex.networking import NetManager

net_manager = NetManager.get_inst()

def main(*args):

  
  url = "https://www.cnyes.com/economy/indicator/GlobalRest/GlobalRest_Major.aspx?code=TWSE&id=8&lv=0"
  rep = requests.post(url)

  print(rep.text)

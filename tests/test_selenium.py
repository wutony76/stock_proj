from __future__ import print_function
import os
from datetime import datetime
import time
import pytz
import requests
import pandas as pd
import chardet
from fatcat.conf import settings as _settings
from infoex.networking import NetManager

net_manager = NetManager.get_inst()

def main(*args):
  from selenium import webdriver

  opts = webdriver.ChromeOptions()
  opts.add_argument("--no-sandbox")

  fp = os.path.join(_settings.ROOT_DIR, "chromedriver")
  driver = webdriver.Chrome(fp, chrome_options=opts)
  driver.get("https://www.cnyes.com/economy/indicator/GlobalRest/GlobalRest_Major.aspx?code=TWSE&id=8&lv=0")
  print("driver", driver)
  print(dir(driver))
  print("data", driver.page_source)

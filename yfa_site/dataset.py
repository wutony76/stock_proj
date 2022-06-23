from __future__ import print_function
import random
from datetime import datetime
import pytz
from BTrees import OOBTree
from fdpays.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw

class DataSet(object):
  def __init__(self):
    
    self.info_by_code = OOBTree.OOBTree({
      '2228': {
        'fullname': '劍麟',
        'name': '劍麟',
      },
      '2231': {
        'fullname': '為升',
        'name': '為升',
      },
      '2236': {
        'fullname': '百達-KY',
        'name': '百達-KY',
      },
      '2239': {
        'fullname': '英利-KY',
        'name': '英利-KY',
      },
      '2243': {
        'fullname': '宏旭-KY',
        'name': '宏旭-KY',
      },
      '2301': {
        'fullname': '光寶科',
        'name': '光寶科',
      },
      '2302': {
        'fullname': '麗正',
        'name': '麗正',
      },
      '2303': {
        'fullname': '聯電',
        'name': '聯電',
      },
      '2305': {
        'fullname': '全友',
        'name': '全友',
      },
      '2308': {
        'fullname': '台達電',
        'name': '台達電',
      },
      '2312': {
        'fullname': '金寶',
        'name': '金寶',
      },
      '2313': {
        'fullname': '華通',
        'name': '華通',
      },
      '2314': {
        'fullname': '台揚',
        'name': '台揚',
      },
      '2316': {
        'fullname': '楠梓電',
        'name': '楠梓電',
      },
      '2317': {
        'fullname': '鴻海',
        'name': '鴻海',
      },
      '2321': {
        'fullname': '東訊',
        'name': '東訊',
      },
      '2323': {
        'fullname': '中環',
        'name': '中環',
      },
      '2324': {
        'fullname': '仁寶電腦工業股份有限公司',
        'name': '仁寶',
      },
      '2327': {
        'fullname': '國巨',
        'name': '國巨',
      },
      '2328': {
        'fullname': '廣宇',
        'name': '廣宇',
      },
      '2329': {
        'fullname': '華泰電子股份有限公司',
        'name': '華泰',
      },
      '2330': {
        'fullname': '台灣積體電路製造股份有限公司',
        'name': '台積電',
      },
    })

    self.data_index = OOBTree.OOBTree()

    self.last_data_by_key = OOBTree.OOBTree()

  def gen_stock_info(self, code, uts):
    try:
      info = self.info_by_code[code]
    except KeyError:
      return

    ts = uts / 1000.0

    dt = ts_to_tz_tw(ts)
    sec = int(dt.second // 5) * 5
    dt2 = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, sec) 
    dt2 = TZ_TW.localize(dt2)
    ts2 = dt_to_ts(dt2)
    uts_key = int(ts2 * 1000.0)
    dt4 = dt2.astimezone(pytz.utc)
    print('dt2=%s uts=%s ts=%s uts_key=%s ts2=%s' % (dt2, uts, ts, uts_key, ts2), 'dt4', dt4)

    try:
      index = self.data_index[code]
    except KeyError:
      index = OOBTree.OOBTree()
      self.data_index[code] = index

    try:
      data = index[uts_key]
    except KeyError:
      data = None

    if data is None:

      trade_volume = random.randint(3800, 4200)
      last_trade_price = '%.4f' % random.randint(500, 700)
      
      low = random.randint(400, 500)
      high = low + random.randint(1, 100)
      _open = random.randint(low, high)

      data = {
        "tv": str(trade_volume),
        "ps":"3803","pz":"613.0000","bp":"0","fv":"177","oa":"612.0000","ob":"611.0000","a":"614.0000_615.0000_616.0000_617.0000_618.0000_","b":"613.0000_612.0000_611.0000_610.0000_609.0000_",
        "c": str(code),
        "d":"20210901","ch":"2330.tw","ot":"14:30:00",
        "tlong": str(uts_key),
        "f":"2094_2308_1325_991_4963_","ip":"0","g":"91_780_259_543_414_","mt":"000000","ov":"68045",
        "o": '%.4f' % _open,
        "h": '%.4f' % high,
        "l": '%.4f' % low,
        "i":"24","it":"12","oz":"611.0000",
        "p":"0","ex":"tse","s":"3838","t":"13:30:00","u":"675.0000","v":"29847","w":"553.0000",
        "n": info['name'],
        "nf": info['fullname'],
        "y":"614.0000",
        "z": last_trade_price,
        "ts": "0"
      }
      index[uts_key] = data

    return data


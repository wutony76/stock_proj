from __future__ import print_function
from fatcat.conf import settings as _settings
from fdstock.rpcclient import RPCClientPool
from yfa_site import yfaDict as _yfa_dict


def main(*args):
  db_cli_pool = RPCClientPool(_settings.FDSTOCK_YFA_DB_ADDR)

  with db_cli_pool.connection() as db_cli:


    exp_codes = sorted(_yfa_dict.TWSE_EXPONENT.keys())
    with db_cli_pool.connection() as db_cli:
      rtn_arr = db_cli.call('TWSE_EXPONENT_INFO_v2', *exp_codes)

    #for k, v in _yfa_dict.TWSE_EXPONENT.items():
    for k, rtn in zip(exp_codes, rtn_arr):
      print("TWSE_EXPONENT_INFO_v2", k, rtn)


    return



    tw50_list_keys = db_cli.call('TW50_LIST_KEY')
    #print("tw50_list_keys", len(tw50_list_keys))
    rtn_arr = db_cli.call('TW50_INFO_v2', *tw50_list_keys)

    
    for key, rtn in zip(tw50_list_keys, rtn_arr):
    #for key in tw50_list_keys:
      stock_code = key
      #rtn = db_cli.call('TW50_INFO', stock_code)
      print("tw50_info_v2", stock_code, repr(rtn))

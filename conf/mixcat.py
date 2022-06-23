from __future__ import print_function
import os 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.dirname(BASE_DIR))
DATA_DIR = os.path.join(ROOT_DIR, 'data')

FDSTOCK_DB_ADDR = ('10.0.0.17', 17101)
FDSTOCK_HTML_ADDR = ('54.95.200.135', 17102)

FDSTOCK_BROKER_ADDR = ('54.95.200.135', 17103)
FDSTOCK_TWSE_DB_ADDR = ('10.0.1.100', 17105)
FDSTOCK_TWSE_INDEX_ADDR = ('10.0.1.100', 17106)

from __future__ import print_function
import os 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.dirname(BASE_DIR))
DATA_DIR = os.path.join(ROOT_DIR, 'data')

#FDSTOCK_DB_ADDR = ('10.0.0.17', 17101)
#FDSTOCK_HTML_ADDR = ('10.0.0.17', 17102)
FDSTOCK_YFA_DB_ADDR = ('21.0.1.18', 17301)
FDSTOCK_SITE_URL = "http://35.75.172.197:17320"

#FDSTOCK_BROKER_ADDR = ('10.0.0.17', 17103)
#FDSTOCK_TWSE_DB_ADDR = ('10.0.1.100', 17105)
#FDSTOCK_TWSE_INDEX_ADDR = ('10.0.1.100', 17106)

FDSTOCK_YFA_WORKER_HTTP = "http://21.0.0.87:17321"
FDSTOCK_YFA_WORKER_HTTP2 = "http://21.0.0.87:17322"

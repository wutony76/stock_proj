from __future__ import print_function
import os 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.dirname(BASE_DIR))
DATA_DIR = os.path.join(ROOT_DIR, "data")


WZ_ROUTE_USER_DB = "WZ_USER_DB"
WZ_ROUTE_TRANS = "WZ_USER_TRANS"
WZ_ROUTE_LOGIN = "WZ_LOGIN"
WZ_ROUTE_NPCIDLE = "WZ_NPCIDLE"


WZ_ROUTER_FRONTEND_URIS = [
  "tcp://11.0.1.148:13031",
  "tcp://11.0.1.218:13033",
  "tcp://11.0.1.218:13035",
]

WZ_ROUTE_USER_ITEMS = [
  "WZ_USER_ITEM00",
  "WZ_USER_ITEM01",
  "WZ_USER_ITEM02",
  "WZ_USER_ITEM03",
  "WZ_USER_ITEM04",
  "WZ_USER_ITEM05",
  "WZ_USER_ITEM06",
  "WZ_USER_ITEM07",
  "WZ_USER_ITEM08",
  "WZ_USER_ITEM09",
  "WZ_USER_ITEM10",
  "WZ_USER_ITEM11",
  "WZ_USER_ITEM12",
  "WZ_USER_ITEM13",
  "WZ_USER_ITEM14",
  "WZ_USER_ITEM15",
]

WZ_ROUTE_USER_ITEM_BRANCH = 16

#####

INFOEX_ZODB_LOG_DIR = os.path.join(DATA_DIR, "log")
INFOEX_ZODB_DATA_DIR = os.path.join(DATA_DIR, "zodb")

INFOEX_ROUTE_DB = "INFOEX_DB"

INFOEX_ROUTER_FRONTEND_URIS = [
  "tcp://11.0.1.148:13031",
  "tcp://11.0.1.218:13033",
  "tcp://11.0.1.218:13035",
]

INFOEX_ROUTER_NODE = {
  "node1": ("tcp://11.0.1.148:13031", "tcp://11.0.1.148:13032"),
  "node2": ("tcp://11.0.1.218:13033", "tcp://11.0.1.218:13034"),
  "node3": ("tcp://11.0.1.218:13035", "tcp://11.0.1.218:13036"),
}

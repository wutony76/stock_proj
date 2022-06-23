#!/usr/bin/python
# -*- coding: UTF-8 -*-
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views
from . import ig_views
from . import tw50_views
from . import bank_rate_views


urlpatterns = [
  url(r'^$', views.index, name="index"),
  url(r'^stock/api/getStockInfo.jsp$', views.get_stock_info_view),


  #stock
  url(r'^stock/list$', views.stock_list, name="stock_list"),
  url(r'^stock/list/get$', views.get_stock_list, name="refresh_stock_list"),
  url(r'^stock/info$', views.stock_info, name="stock_info"),
  url(r'^stock/info/get$', views.get_stock_info, name="refresh_stock_info"),
  url(r'^stock/info/all$', views.update_stock_info, name="update_stock_info"),
  #exponent
  url(r'^exponent/list$', views.exponent_list, name="exponent_list"),
  url(r'^exponent/list/get$', views.get_exponent_list, name="refresh_exponent_list"),
  url(r'^exponent/info$', views.exponent_info, name="exponent_info"),
  url(r'^exponent/info/get$', views.get_exponent_info, name="refresh_exponent_info"),
  url(r'^exponent/info/all$', views.update_exponent_info, name="update_exponent_info"),


  #twse_exponent
  url(r'^twse/exponent/list$', views.twse_exponent_list, name="twse_exponent_list"),
  url(r'^twse/exponent/info$', views.twse_exponent_info, name="twse_exponent_info"),
  url(r'^twse/exponent/info/all$', views.update_twse_exponent_info, name="update_twse_exponent_info"),

  # --yahoo update
  url(r'^yahoo/exponent/info/all$', views.update_yahoo_exponent_info, name="update_yahoo_exponent_info"),
  url(r'^yahoo/exponent/info/all2$', views.update_yahoo_exponent_info2, name="update_yahoo_exponent_info2"),


  #電子類指數及金融保險類指數列表
  url(r'^twse/eftri/exponent/info$', views.twse_exponent_info_eftri, name="twse_exponent_info_eftri"),
  url(r'^twse/eftri/exponent/info/all$', views.update_twse_exponent_info_eftri, name="update_twse_exponent_info_eftri"),

  #電子類報酬指數及金融保險類報酬指數列表
  url(r'^twse/other/exponent/info$', views.twse_exponent_info_other, name="twse_exponent_info_other"),
  url(r'^twse/other/exponent/info/all$', views.update_twse_exponent_info_other, name="update_twse_exponent_info_other"),

  #ig_exponent
  url(r'^ig/exponent/list$', ig_views.ig_exponent_list, name="ig_exponent_list"),
  url(r'^ig/exponent/info$', ig_views.ig_exponent_info, name="ig_exponent_info"),
  url(r'^ig/exponent/info/all$', ig_views.update_ig_exponent_info, name="update_ig_exponent_info"),


  #tw50_stock
  url(r'^tw50/stock/list$', tw50_views.tw50_list, name="tw50_list"),
  url(r'^tw50/stock/list/get$', tw50_views.update_tw50_list, name="refresh_tw50_list"),
  url(r'^tw50/stock/info$', tw50_views.tw50_info, name="tw50_info"),
  url(r'^tw50/stock/info/all$', tw50_views.update_tw50_info, name="update_tw50_info"),

  
  #bank_taiwan
  url(r'^bank/list$', bank_rate_views.bank_rate_list, name="bank_list"),
  url(r'^bank/rate/info$', bank_rate_views.bank_rate_info, name="bank_info"),
  url(r'^bank/rate/info/all$', bank_rate_views.update_bank_rate_info, name="update_bank_info"),
  #url(r'^bank/list$', bank_rate_views.bank_rate_list, name="bank_list"),
]

urlpatterns += staticfiles_urlpatterns()

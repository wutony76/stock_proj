from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
  url(r'^$', views.index, name="index"),
  url(r'^stock/api/getStockInfo.jsp$', views.get_stock_info_view),
]

urlpatterns += staticfiles_urlpatterns()

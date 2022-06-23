from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
  url(r'^$', views.index, name="index"),
  url(r'^equities$', views.equity_list_view),
  url(r'^timeline$', views.timeline_view),
  url(r'^bc$', views.bc_view),
]

urlpatterns += staticfiles_urlpatterns()

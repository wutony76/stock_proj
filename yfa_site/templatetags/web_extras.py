# -*- coding: UTF-8 -*-
import os

from django.urls import reverse as reverse_url
from django.template import Library, Node, TemplateSyntaxError
from django.utils.safestring import mark_safe
from fcworks.conf import settings as _settings
from django.templatetags.static import static as reverse_static_url

from fdstock.time_utils import TZ_TW, dt_to_ts, ts_to_tz_tw

from datetime import datetime
from datetime import timedelta

#from akgames.networking import NetManager
#from office_site.tools import read_url_img
#from office_site.static_data import Data 




register = Library()
#net_manager = NetManager.get_inst()


class RangeNode(Node):
  def __init__(self, num, context_name):
    self.num, self.context_name = num, context_name

  def render(self, context):
    context[self.context_name] = range(int(self.num))
    return ""
        
@register.tag
def num_range(parser, token):
  print( "split_contents token", token )
  print( "split_contents", token.split_contents() )

  #try:
  #  fnctn, num, trash, context_name = token.split_contents()

    #print( "split_contents fnctn", fnctn )
    #print( "split_contents num", num )
    #print( "split_contents trash", trash )
    #print( "split_contents context_name", context_name )
    
  #except ValueError:
    #raise TemplateSyntaxError, "%s takes the syntax %s number_to_iterate as context_variable" % (fnctn, fnctn)

  #if not trash == 'as':
    #raise TemplateSyntaxError, "%s takes the syntax %s number_to_iterate as context_variable" % (fnctn, fnctn)
  #return RangeNode(num, context_name)



#--- key to base64 img ---
@register.simple_tag
def web_get_img( img_key, **kwargs ):
  return read_url_img(img_key)
#--- key to base64 img end ---

@register.simple_tag
def web_list_index( arr, value ):
  return arr.index(value) + 1

@register.simple_tag
def list_index( arr, value ):
  return arr.index(value)

@register.simple_tag
def web_get_nickname( account ):
  print( "account", account )
  with net_manager.aksite_route_cli_pool.connection() as aksite_route_cli:
    nickname = aksite_route_cli.db_call( "GET_MEMBER_NICKNAME", account )
    if len(nickname) > 0:
      nickname = nickname[0]
  return nickname 





#--- ADMIN ---#
@register.simple_tag
def admin_question_type(type_id):
  print( "type_id", type_id )
  data = {
      1:u"常見問題",
      2:u"遊戲問題",
      3:u"會員問題",
      4:u"遊戲問題",
      }
  return data[type_id] 
#--- ADMIN END ---#

#--- STATIC MEMBER ---#
@register.simple_tag
def static_member_photo(photo):
  #member = Member.get_inst( account )
  #member = static_data.get_member(account)
  #print ( "BASE_DIR -----------------" , Data.BASE_DIR )


  path = "assets/images/avatar/avatar_%02d.png" % int(photo)
  #static_path = os.path.join(_settings.AKSITE_STATIC_DIR, "static", path)
  redirect_to = reverse_static_url(path)
  #print( "redirect_to ", redirect_to )
  return redirect_to
  #return HttpResponseRedirect(redirect_to)

  #return static_path
  #return os.path.join(Data.BASE_DIR, "static/assets/images/avatar/avatar_%02d.png" % int(photo)) 



@register.simple_tag
def check_ranking():
  with net_manager.aksite_route_cli_pool.connection() as aksite_route_cli:
    conf = aksite_route_cli.db_call("GET_SITE_CONF")
    if conf.get("ranking", None) == 'open':
      output = u'<li><a href="%s">封測排行</a></li>' % reverse_url("web_ranking")
      return mark_safe(u"".join(output))
    

@register.simple_tag
def check_ranking_phone():
  with net_manager.aksite_route_cli_pool.connection() as aksite_route_cli:
    conf = aksite_route_cli.db_call("GET_SITE_CONF")
    if conf.get("ranking", None) == 'open':
      output = u'<li> <a href="%s" class="item"> <div class="icon-box bg-pink"> <ion-icon name="podium-outline"></ion-icon> </div> <div class="in">封測排行</div> </a> </li>'% reverse_url("web_ranking")
      return mark_safe(u"".join(output))



#################################################################



@register.simple_tag
def uts_to_date(ts):
  #print("uts_to_datets ---------")
  utc_time = datetime.utcfromtimestamp(ts)
  time2 = utc_time + timedelta(hours=8)
  return time2.strftime("%Y-%m-%d %H:%M:%S")
  #return ts_to_tz_tw( ts ).strftime("%Y-%m-%d %H:%M:%S")


#@register.simple_tag
#def static_member_nickname(account):
#  member = static_data.get_member(account)
#  return member.nickname
#
#@register.simple_tag
#def static_member_coins(account):
#  #member = Member.get_inst( account )
#  member = static_data.get_member(account)
#  return member.coins
#
#@register.simple_tag
#def static_member_invite_code(account):
#  #member = Member.get_inst( account )
#  member = static_data.get_member(account)
#  return member.invite_code
#
#@register.simple_tag
#def static_member_invite_png(account):
#  #member = Member.get_inst( account )
#  member = static_data.get_member(account)
#  return member.invite_qr_png
#--- STATIC MEMBER END ---#



@register.filter
def index(indexable, i):
  return indexable[i]

@register.filter
def list_index_from_value(list_, value):
    print( "--list_", list_ )
    print( "--value", value )
    return list_.index(value)


@register.filter()
def range(min=5):
    return range(min)



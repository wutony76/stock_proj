from __future__ import print_function
import threading
import traceback
import requests
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from fatcat.conf import settings as _settings
from fdstock.protocols import BaseProtocol, PacketOpts
from fdstock.exceptions import LogicError
from fdstock.rpcclient import RPCClientPool


class Villager(object):

  def __init__(self):
    self.html_cli_pool = RPCClientPool(_settings.FDSTOCK_HTML_ADDR)


  def setup(self, addr):
    
    print(self, 'setup', addr)
    cli_fac = ClientFactory(self)

    host, port = addr

    reactor.connectTCP(host, port, cli_fac)

  def process_command(self, proto, cmd_name, *cmd_args):
    #print(self, 'process_command', cmd_name, seqid, cmd_args)
    func_name = 'handle_command_%s' % cmd_name
    func = getattr(self, func_name, None)

    if func is None:
      raise Exception('no command %s' % cmd_name)

    #with self.txnmgr.get_request() as txn:
      #print('handle_command_ORDER_ADD', args)
    req = Request(proto, cmd_args, None)
    rtn = func(req)

    return rtn

  def handle_command_HTTP_REQ(self, req):
    
    out = []
    args = req.args
    print('handle_command_HTTP_REQ', args)
    for i in xrange(0, len(args), 6):
      url = args[i]
      method = args[i+1]
      extra_headers = args[i+2]
      data = args[i+3]
      que_id = args[i+4]
      extra_meta = args[i+5]

      if method == 'GET':
        ### ttt ###
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        ### ttt end. ###
        headers.update(extra_headers)

        rep = requests.get(url, params=data, headers=headers)
        print('req', url, method, extra_headers, data)
        print('rep', rep.status_code)

        if rep.status_code != 200:
          return

        print('rep', rep.content)
        meta = dict(extra_meta)
        meta.update({
          'encoding': rep.encoding,
          'status_code': rep.status_code,
        })

        with self.html_cli_pool.connection() as cli:
          cli.call('APPEND_DATA', que_id, meta, rep.content)
      

    return out



class Request(object):
  def __init__(self, proto, args, txn):
    self.proto = proto
    self.args = args
    self.txn = txn


class ClientProtocol(BaseProtocol):
  def __init__(self, id, factory):
    super(ClientProtocol, self).__init__()
    self.id = id
    self.factory = factory

  def __repr__(self):
    return "<ClientProtocol>"
  

  def send_command(self, name, *cmd_args):
    ask = self.next_ask()
    packet = [name, cmd_args]
    self.send_packet(PacketOpts.OP_COMMAND_REQ, ask, packet)

  def process_command(self, cmd_name, *cmd_args):
    print('process_command', cmd_name, cmd_args)
    reactor.callInThread(self.factory.process_command, self, cmd_name, cmd_args)

  def process_command_response(self, ask, packet):
    print('process_command_response', ask, packet)

  def connectionMade(self):
    print("connectionMade", self)
    self.send_command('LOGIN', 1)

  def connectionLost(self, reason):
    print("connectionLost", reason)

class ClientFactory(ReconnectingClientFactory):

  def __init__(self, handler):
    self.handler = handler
    self._last_id = 0


  def process_command(self, proto, cmd_name, cmd_args):
    
    code = 0
    rtn = None
    reason = None

    try:
      self.handler.process_command(proto, cmd_name, *cmd_args)

    except Exception as ex:
      _err = {
        'message': ex.message, 
        'ex': traceback.format_exc(),
      }

      if isinstance(ex, LogicError):
        pass
      else:
        traceback.print_stack()
        traceback.print_exc()
        print('ex', ex.message)

      code = 1
      rtn = None
      reason = ex.message

    out = (code, rtn, reason)
    ask = proto.next_ask()
    #print('process_command', 'out', out)
    proto.send_packet(PacketOpts.OP_COMMAND_REP, ask, out)


  def startedConnecting(self, connector):
    print('Started to connect.')

  def buildProtocol(self, addr):
    print('Connected.')
    print('Resetting reconnection delay')
    self.resetDelay()
    id = self._last_id + 1
    self._last_id = id
    proto = ClientProtocol(id, self)

    return proto

  def clientConnectionLost(self, connector, reason):
    print('Lost connection.  Reason:', reason)
    ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

  def clientConnectionFailed(self, connector, reason):
    print('Connection failed. Reason:', reason)
    ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

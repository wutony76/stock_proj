from __future__ import print_function
import time
import threading
import traceback
import struct
import Queue
import rwlock
import msgpack
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.task import LoopingCall
from fdstock.protocols import BaseProtocol, PacketOpts
from fdstock.exceptions import LogicError
from fdstock.seqid import SeqIDGenerator


class Identity:
  VILLAGER = 1


def spawn(func):
  th = threading.Thread(target=func)
  th.setDaemon(True)
  th.start()

class Request(object):
  def __init__(self, proto, args, txn):
    self.proto = proto
    self.args = args
    self.txn = txn

class Server(object):

  def __init__(self):
    self.lock = rwlock.RWLock()


  def setup(self, serverfactory):
    self.serverfactory = serverfactory

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

  def handle_command_SEND_COMMAND_TO(self, req):
    out = []
    args = req.args
    print('handle_command_SEND_COMMAND_TO', args)
    with self.lock.reader_lock:
      for i in xrange(0, len(args), 3):
        proto_id = args[i]
        cmd_name = args[i+1]
        cmd_args = args[i+2]

        proto = self.serverfactory.get_proto(proto_id)
        if proto is not None:
          proto.send_command(cmd_name, *cmd_args)

  def handle_command_ALL_PROTOCOL(self, req):
    out = []
    args = req.args
    print('handle_command_ALL_PROTOCOL', args)
    with self.lock.reader_lock:

      protos = self.serverfactory.get_all_protos()

      for i in xrange(0, len(args), 1):
        identity = args[i]

        rtn = []

        for proto in protos:
          if proto.identity == identity:
            rtn.append(proto.id)

        out.append(rtn)


    return out

  def handle_command_LOGIN(self, req):
    
    out = []
    args = req.args
    print('handle_command_LOGIN', args)
    with self.lock.writer_lock:
      identity = args[0]
      req.proto.identity = identity

    return out


class ServerProtocol(BaseProtocol):

  def __init__(self, id, serverfactory):
    #Protocol.__init__(self)
    super(ServerProtocol, self).__init__()
    self.id = id
    self.serverfactory = serverfactory
    self.identity = None

  def __repr__(self):
    return "<ServerProtocol id=%s identity=%s>" % (self.id, self.identity)

  def connectionMade(self):
    print("connectionMade", self)

  def connectionLost(self, reason):
    self.serverfactory.connection_lost(self, reason)

  def process_command(self, cmd_name, *cmd_args):
    #print('>> process_command', cmd_name, seqid, cmd_args)
    reactor.callInThread(self.serverfactory.process_command, self, cmd_name, cmd_args)

  def process_command_response(self, ask, packet):
    print('process_command_response', ask, packet)

  def send_command(self, cmd_name, *cmd_args):

    ask = self.next_ask()
    packet = [cmd_name, cmd_args]
    self.send_packet(PacketOpts.OP_COMMAND_REQ, ask, packet)



class ServerFactory(Factory):
  def __init__(self, prefix, mac_id, server):
    self._lock = threading.Lock()
    self._last_id = 0
    self._proto_by_id = {}
    self.seqid_gen = SeqIDGenerator(prefix, mac_id)
    self.server = server


  def get_all_protos(self):
    with self._lock:
      return self._proto_by_id.values()

  #######

  def connection_lost(self, proto, reason):
    with self._lock:
      self._proto_by_id.pop(proto.id)

  def get_proto(self, proto_id):
    with self._lock:
      proto = self._proto_by_id.get(proto_id, None)
      return proto

  def buildProtocol(self, addr):
    with self._lock:
      _id = self.seqid_gen.next_id()
      proto = ServerProtocol(_id, self)
      self._proto_by_id[_id] = proto
      return proto


  def process_command(self, proto, cmd_name, cmd_args):
    

    code = 0
    rtn = None
    reason = None

    try:
      rtn = self.server.process_command(proto, cmd_name, *cmd_args)
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



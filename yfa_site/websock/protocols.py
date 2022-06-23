from __future__ import print_function
import struct
from struct import Struct
import threading
import traceback
import json
from twisted.internet import reactor, defer
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol

PACKET_HEADER = Struct('>HI')

WZ_OP_COMMAND = 0x0101
WZ_OP_ANSWER = 0x0102
WZ_OP_MESSAGE = 0x0103

WZ_DATATYPE_JSON = 0x01
WZ_DATATYPE_BLOB = 0x02

NOT_DONE_YET = -2**64



class ServerProtocol(WebSocketServerProtocol):
  def __init__(self, id, factory, addr, *args, **kwargs):
    super(ServerProtocol, self).__init__()

    self.id = id
    self.factory = factory

    self._send_lock = threading.Lock()
    self._recv_lock = threading.Lock()
    self._unpacker_lock = threading.Lock()
    self._recv_arr = []

    self._unpacker = Unpacker()
    self._ask_lock = threading.Lock()
    self._last_ask = 0

    self._readed_total_bytes  = 0


  def __repr__(self):
    return "<ServerProtocol id=%s>" % self.id

  def onConnect(self, request):
    print("onConnect", self)
    pass

  def onClose(self, wasClean, code, reason):
    print("onClose", wasClean, code, reason)
    self.factory.remove_proto(self)

  def send_packet(self, op_code, data):
    with self._send_lock:
      send_data = PACKET_HEADER.pack(op_code, len(data)) + data
      #print("send_packet", "op", op_code, "len", len(data))
      self.sendMessage(send_data, True)

  def send_command(self, command_name, data):
    #print self, "send_command", command

    ask = self._last_ask + 1
    self._last_ask = ask

    command_data = json.dumps(data)
    data = struct.pack('>IBB', ask, WZ_DATATYPE_JSON, len(command_name)) + command_name + command_data    

    self.send_packet(WZ_OP_COMMAND, data)


  def onMessage(self, payload, isBinary):
    assert isBinary

    self._readed_total_bytes += len(payload)

    with self._recv_lock:
      self._recv_arr.append(payload)

    reactor.callInThread(self._do_onMessage, payload)

  def _do_onMessage(self, payload):
    with self._recv_lock:
      if len(self._recv_arr) <= 0:
        return
      while len(self._recv_arr) > 0:
        payload = self._recv_arr.pop(0)
        with self._unpacker_lock:
          self._unpacker.append(payload)

    with self._unpacker_lock:
      try:
        for op, pkt in self._unpacker:
          #print "op=%s ask=%s" % (op, ask)
          if op == WZ_OP_COMMAND: 
            hdr = pkt[:6]
            ask, dtype, cmd_name_len = struct.unpack('>IBB', hdr)
            #, pkt[5:]
            cmd_name_end = 6+cmd_name_len
            command_name = pkt[6:cmd_name_end]
            data = pkt[cmd_name_end:]

            #print("Command=%s ask=%s" % (command_name, ask), [data])

            if dtype == WZ_DATATYPE_JSON:
              data = json.loads(data)

            func_name = "handle_command_%s" % command_name

            func = getattr(self, func_name, None)
            if func is None:
              print("no command handle ", func_name)
            if func is not None:
              #data = packet["Data"]

              try:
                rep = func(ask, data)

              except Exception as ex:
                rep = {"Reason": str(ex)}

                traceback.print_stack()
                traceback.print_exc()
                print( ex)

              #print("rep", func_name, type(rep))
              if rep == NOT_DONE_YET:
                pass
              elif isinstance(rep, defer.Deferred):
                pass
              else:
                self.send_answer(ask, rep)

      except StopIteration:
        print("StopIteration")
      except Exception as ex:
        traceback.print_stack()
        traceback.print_exc()
        print(ex)

  def send_answer(self, ask, rep):
    rep_type = None
    if isinstance(rep, dict):
      rep_type = WZ_DATATYPE_JSON
      rep = json.dumps(rep)
      #print("rep", rep)
    elif isinstance(rep, str):
      rep_type = WZ_DATATYPE_BLOB
      #print "rep blob", len(rep)
    
    #print(self, "send_answer ask", ask, "rep_type", rep_type, rep)
    assert isinstance(ask, int)
    rep = struct.pack('>IB', ask, rep_type) + rep
    self.send_packet(WZ_OP_ANSWER, rep)

class ServerFactory(WebSocketServerFactory):

  PROTOCOL = ServerProtocol

  def __init__(self, *args, **kwargs):
    super(ServerFactory, self).__init__(*args, **kwargs)
    self._lock = threading.Lock()
    self._last_proto_id = 0
    self._proto_by_id = {}

  def new_proto(self, addr, proto_class):
    with self._lock:
      _id = self._last_proto_id + 1
      self._last_proto_id = _id

      proto = proto_class(_id, self, addr)
      self._proto_by_id[_id] = proto

      return proto

  def buildProtocol(self, addr):
    proto = self.new_proto(addr, self.PROTOCOL)
    return proto


  def remove_proto(self, proto):
    with self._lock:
      if self._proto_by_id.has_key(proto.id):
        del self._proto_by_id[proto.id]

class Unpacker(object):
  STATE_HEADER = 0
  STATE_BODY = 1
  HEADER_SIZE = 6

  def __init__(self):
    self._state = 0
    self._buf = ""

    self._hdr_set = None

  def append(self, data):
    self._buf += data
    #print "Unpacker append", len(data)


  def __iter__(self):

    while True:

      if self._state == self.STATE_HEADER:
        if len(self._buf) < self.HEADER_SIZE:
          raise StopIteration

        hdr, self._buf = self._buf[:self.HEADER_SIZE], self._buf[self.HEADER_SIZE:]

        op, pkt_len = PACKET_HEADER.unpack(hdr)

        self._hdr_set = (op, pkt_len)
        self._state = self.STATE_BODY

        continue

        #print "next op", self._op, "next ask", ask, "next len", self._pkt_len

      if self._state == self.STATE_BODY:
        op, pkt_len = self._hdr_set
        if len(self._buf) < pkt_len:
          raise StopIteration


        pkt, self._buf = self._buf[:pkt_len], self._buf[pkt_len:]
        self._state = self.STATE_HEADER

        yield op, pkt
        continue

      raise StopIteration


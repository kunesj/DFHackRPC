#!/usr/bin/env python3
# encoding: utf-8
from .proto import proto_db
from .default_methods import DEFAULT_METHODS

import socket
import struct
import time
import json
import google.protobuf.json_format
import logging

_logger = logging.getLogger(__name__)


class DFHackRPC(object):
    """
    Most important methods:

        open_connection, close_connection,
        bind_method, bind_all_methods,
        call_method, call_method_dict, run_command

    If you are getting "In RPC server: I/O error in receive header." messages in DFHack,
    check that you didn't forget to close API connection with dfhack_rpc.close_connection().


    Protocol description:

     1. Handshake

       Client initiates connection by sending the handshake
       request header. The server responds with the response
       magic. Currently both versions must be 1.

     2. Interaction

       Requests are done by exchanging messages between the
       client and the server. Messages consist of a serialized
       protobuf message preceded by RPCMessageHeader. The size
       field specifies the length of the protobuf part.

       NOTE: As a special exception, RPC_REPLY_FAIL uses the size
             field to hold the error code directly.

       Every callable function is assigned a non-negative id by
       the server. Id 0 is reserved for BindMethod, which can be
       used to request any other id by function name. Id 1 is
       RunCommand, used to call console commands remotely.

       The client initiates every call by sending a message with
       appropriate function id and input arguments. The server
       responds with zero or more RPC_REPLY_TEXT:CoreTextNotification
       messages, followed by RPC_REPLY_RESULT containing the output
       of the function if it succeeded, or RPC_REPLY_FAIL with the
       error code if it did not.

     3. Disconnect

       The client terminates the connection by sending an
       RPC_REQUEST_QUIT header with zero size and immediately
       closing the socket.
    """

    def __init__(self, dfhack_host='localhost', dfhack_port=5000, sock_timeout=0.000000001, sock_buff_size=10000,
                 response_timeout=5):
        """
        :param dfhack_host: Address of computer running DF
        :param dfhack_port: DFHack API port
        :param sock_timeout: Max time between reads from socket
        :param sock_buff_size:
        :param response_timeout: How long we will wait for data from DFHack API before raising exception
        """
        self.dfhack_host = dfhack_host
        self.dfhack_port = dfhack_port
        self.sock = None
        self.sock_timeout = sock_timeout
        self.sock_buff_size = sock_buff_size
        self.response_timeout = response_timeout

        # bound methods
        self.bound_methods = {}
        for method, input_msg, output_msg, plugin, assigned_id in DEFAULT_METHODS:
            self.bound_methods[method] = {
                'method': method,
                'input_msg': input_msg,
                'output_msg': output_msg,
                'plugin': plugin,
                'assigned_id': assigned_id,
            }

    # API calls

    def open_connection(self):
        _logger.info('Opening connection')
        if self.sock:
            _logger.debug('Connection already opened')
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.dfhack_host, self.dfhack_port))

        assert self.sock_timeout > 0
        self.sock.settimeout(self.sock_timeout)

        # handshake
        resp = self.rpc_call(self.build_handshake())
        self.parse_handshake(resp)  # raises exception if any problems

    def close_connection(self):
        _logger.info('Closing connection')
        if not self.sock:
            _logger.debug('Connection already closed')
            return

        self.sock.sendall(self.build_message(b'', -4))
        self.sock.close()
        self.sock = None

    def rpc_call(self, data):
        if not self.sock:
            self.open_connection()

        self.sock.sendall(data)
        start_time = time.time()

        fragments = []
        while True:
            try:
                chunk = self.sock.recv(self.sock_buff_size)
                fragments.append(chunk)
            except socket.timeout:
                if len(fragments) > 0:
                    break
            if len(fragments) == 0 and (time.time() > start_time + self.response_timeout):
                raise Exception('No API response detected')
        resp = b''.join(fragments)

        return resp

    def rpc_messages(self, messages):
        """
        Sends messages via RPC and returns returned messages
        :param messages: binary string or list of binary strings
        :return: list of binary strings
        """
        messages = b''.join(messages) if isinstance(messages, list) else messages
        resp = self.rpc_call(messages)

        output = []
        offset = 0
        while offset < len(resp):
            _, _, size = self.parse_message(resp[offset:])
            output.append(resp[offset:offset+size])
            offset += size

        return output

    def parse_handshake(self, data):
        if len(data) < 12:
            data = data + b'\x00' * (12 - len(data))
        magic = data[:8]
        version = struct.unpack('i', data[8:12])[0]

        assert magic in [b'DFHack?\n', b'DFHack!\n']
        assert 1 <= version <= 255
        return magic, version, 12

    def build_handshake(self, magic=b'DFHack?\n', version=1):
        """
        :param magic: b'DFHack?\n' for request, b'DFHack!\n' for response
        :param version: 1
        :return: RPC handshake request/response
        """
        assert magic in [b'DFHack?\n', b'DFHack!\n']
        assert 1 <= version <= 255

        data = magic + struct.pack('i', version)
        return data

    def parse_header(self, data):
        if len(data) < 8:
            data = data + b'\x00' * (8 - len(data))
        id = struct.unpack('h', data[:2])[0]
        size = struct.unpack('i', data[4:8])[0]
        return id, size, 8

    def build_header(self, id, size):
        """
        :param id: message id
            0 - request
            -1 - result
            -2 - fail
            -3 - text
            -4 - request quit
            ? - bound method ID
        :param size: size of message data
        :return: message header
        """
        return struct.pack('h', id) + struct.pack('h', 0) + struct.pack('i', size)

    def parse_message(self, data):
        id, size, read_size = self.parse_header(data)
        return data[read_size:read_size+size], id, (read_size+size)

    def build_message(self, data, id=0):
        """
        :param data: message data
        :param id: message id
        :return: message header + data
        """
        return self.build_header(id, len(data)) + data

    # Proto
    # https://developers.google.com/protocol-buffers/docs/reference/python/index.html

    @classmethod
    def get_proto(cls, full_name):
        return proto_db.GetSymbol(full_name)

    @classmethod
    def proto2dict(cls, data_obj, including_default_value_fields=True):
        data_json = google.protobuf.json_format.MessageToJson(
            data_obj, including_default_value_fields=including_default_value_fields
        )
        return json.loads(data_json)

    @classmethod
    def dict2proto(cls, full_name, data_dict):
        data_cls = cls.get_proto(full_name)
        data_json = json.dumps(data_dict)
        return google.protobuf.json_format.Parse(data_json, data_cls())

    # Tools

    def call_method(self, method, data_obj=None):
        _logger.debug('Calling method "{}"'.format(method))

        if method not in self.bound_methods or self.bound_methods[method]['assigned_id'] is None:
            raise Exception('method not bound')
        data_obj = data_obj or self.get_proto(self.bound_methods[method]['input_msg'])()
        assert self.bound_methods[method]['input_msg'] == data_obj.DESCRIPTOR.full_name

        data_msg = self.build_message(data_obj.SerializeToString(), id=self.bound_methods[method]['assigned_id'])
        resp_msgs = self.rpc_messages(data_msg)

        resp_cls = self.get_proto(self.bound_methods[method]['output_msg'])
        resp_obj = resp_cls()
        resp_text = b''

        for resp_msg in resp_msgs:
            resp, id, _ = self.parse_message(resp_msg)
            if id == -1:
                resp_obj.ParseFromString(resp)
            elif id == -2:
                raise Exception('RPC fail')
            elif id == -3:
                resp_text += resp
            else:
                raise Exception('Unexpected message id {}'.format(id))

        return resp_obj, resp_text

    def call_method_dict(self, method, data_dict=None):
        if method not in self.bound_methods or self.bound_methods[method]['assigned_id'] is None:
            raise Exception('method not bound')

        data_obj = self.dict2proto(self.bound_methods[method]['input_msg'], data_dict or {})
        resp_obj, text = self.call_method(method, data_obj)
        resp_dict = self.proto2dict(resp_obj)

        return resp_dict, text

    def bind_method(self, method, input_msg=None, output_msg=None, plugin=None):
        _logger.info('Binding method "{}"'.format(method))

        # check if method is already bound
        if self.bound_methods.get(method, {}).get('assigned_id') is not None:
            _logger.debug('Method is already bound')
            return self.bound_methods[method]

        # load input and output type
        if method in self.bound_methods:
            input_msg = input_msg if input_msg else self.bound_methods[method]['input_msg']
            output_msg = output_msg if output_msg else self.bound_methods[method]['output_msg']
            plugin = plugin if plugin else self.bound_methods[method]['plugin']

        # validate types, throws exception if failure
        self.get_proto(input_msg)
        self.get_proto(output_msg)

        # send and receive
        data_cls = self.get_proto('dfproto.CoreBindRequest')
        data_obj = data_cls(method=method, input_msg=input_msg, output_msg=output_msg, plugin=plugin)
        resp_obj, resp_text = self.call_method('BindMethod', data_obj)

        # save bound method and it's id to cache
        self.bound_methods[method] = {
            'method': method,
            'input_msg': input_msg,
            'output_msg': output_msg,
            'plugin': plugin,
            'assigned_id': resp_obj.assigned_id,
        }

        return self.bound_methods[method]

    def bind_all_methods(self):
        for method in self.bound_methods:
            if self.bound_methods[method]['assigned_id'] is not None:
                continue
            self.bind_method(method)

    def run_command(self, command, arguments=None):
        arguments = arguments or []
        _logger.info('Running command "{}" with arguments "{}"'.format(command, arguments))

        data_cls = self.get_proto('dfproto.CoreRunCommandRequest')
        data_obj = data_cls(command=command, arguments=arguments)

        return self.call_method('RunCommand', data_obj)

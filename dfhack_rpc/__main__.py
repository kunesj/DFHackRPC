#!/usr/bin/env python3
# encoding: utf-8
from . import DFHackRPC

import logging

_logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig()
    _logger = logging.getLogger()
    _logger.setLevel(logging.INFO)

    rpc = DFHackRPC()
    rpc.bind_all_methods()

    # Print versions

    print('DFHack version: ', end='')
    resp, text = rpc.call_method('GetVersion')
    print(resp.value)

    print('DF version: ', end='')
    resp, text = rpc.call_method('GetDFVersion')
    print(resp.value)

    print('RemoteFortressReader version: ', end='')
    resp, text = rpc.call_method('GetVersionInfo')
    print(resp.remote_fortress_reader_version)

    # Method parameter example: proto
    # TODO

    # Method parameter example: dict
    resp, text = rpc.call_method_dict('GetEmbarkTile', {'wantX': 2, 'wantY': 0})

    # close connection
    rpc.close_connection()

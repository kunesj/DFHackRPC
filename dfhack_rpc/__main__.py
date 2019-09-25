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
    EmptyMessage = rpc.get_proto('dfproto.EmptyMessage')

    print(rpc.bind_method('GetVersion'))
    print(rpc.call_method('GetVersion', EmptyMessage()))
    print('--------------------------------------------------------------------')

    print(rpc.bind_method('GetDFVersion'))
    print(rpc.call_method('GetDFVersion', EmptyMessage()))
    print('--------------------------------------------------------------------')

    print(rpc.bind_method('GetWorldInfo'))
    print(rpc.call_method('GetWorldInfo', EmptyMessage()))
    print('--------------------------------------------------------------------')

    print(rpc.run_command('RemoteFortressReader_version'))
    print('--------------------------------------------------------------------')

    rpc.bind_all_methods()
    print('--------------------------------------------------------------------')

    # print(rpc.call_method('GetWorldMap', EmptyMessage()))
    # print(rpc.call_method('GetRegionMaps', EmptyMessage()))
    # print(rpc.call_method('GetMapInfo', EmptyMessage()))
    # print(rpc.call_method('GetMaterialList', EmptyMessage()))
    # print('--------------------------------------------------------------------')

    # close connection
    rpc.close_connection()

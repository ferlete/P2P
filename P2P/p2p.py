__version__ = "0.1"

import argparse
import os
import sys
import threading

from .client import Client
from .info import Info
from .peer import Peer
from .server import Server
from .fileIO import FileIO

MUSIC_FOLDER = "/music/"
byte = 1
kilobyte = byte * 1024
megabyte = kilobyte * 1024
BLOCK_SIZE = int(1 * megabyte)  # file block size in bytes


def main():
    default_port = 9999
    server_ip = '127.0.0.1'
    info = Info('authors', 'ferlete@gmail.com', 'P2P FACOM')
    transport = "TCP"

    parser = argparse.ArgumentParser(description=info.get_app_name())
    parser.add_argument('--type', '-t', dest="type", help='choice server or client',
                        default='server')  # server or client
    parser.add_argument('--tcp', dest="tcp", action='store_true', help='use TCP for transport', default=True,
                        required=False)  # User default TCP for transport
    parser.add_argument('--udp', dest="udp", action='store_true', help='use UDP for transport', default=False,
                        required=False)  # User default TCP for transport
    parser.add_argument('--port', '-p', dest="port", help='server port', type=int, default=default_port)  # port Server
    parser.add_argument('--version', '-v', action='version', version=info.get_app_name() + __version__)  # show version
    parser.add_argument('--debug', help='increase output verbosity')

    args = parser.parse_args()
    if args.tcp:
        transport = "TCP"
    if args.udp:
        transport = "UDP"

    try:

        if args.type == 'server':
            # start server
            Server(server_ip, args.port, transport, MUSIC_FOLDER, BLOCK_SIZE)

        if args.type == 'client':
            filename = input('Informe nome do arquivo: ')
            peer = Peer()
            for node_peer in peer.get_list_peer():
                #print(node_peer.strip())
                ip, port = node_peer.strip().split(':')
            Client(str(ip), int(port), filename, 1)
    except Exception as ex:
        print(ex)




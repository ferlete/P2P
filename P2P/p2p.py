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
from .music import Music
from .progress import Progress
from P2P.constants import *


def main():
    default_port = 9000
    default_ip = '192.168.25.7'
    info = Info('authors', 'ferlete@gmail.com', 'P2P FACOM')
    policy = SEQUENCIAL_POLICY

    parser = argparse.ArgumentParser(description=info.get_app_name())
    parser.add_argument('--type', '-t', dest="type", help='choice server or client',
                        default='server')  # server or client
    parser.add_argument('--policy', '-m', dest="policy", help='transmission policy', type=str,
                        default=policy)  # transmission policy
    parser.add_argument('--ip', '-i', dest="ip", help='server IP', type=str, default=default_ip)  # IP Server
    parser.add_argument('--port', '-p', dest="port", help='server port', type=int, default=default_port)  # port Server
    parser.add_argument('--version', '-v', action='version', version=info.get_app_name() + __version__)  # show version
    parser.add_argument('--debug', action='store_true',  help='increase output verbosity')

    args = parser.parse_args()
    if args.policy == RANDOM_POLICY:
        policy = RANDOM_POLICY

    #if args.debug:
    #    print("debug True")

    try:

        if args.type == 'server':
            # start server
            Server(args.ip, args.port, policy)

        if args.type == 'client':
            filename = input('Informe nome do arquivo: ')
            peer = Peer()
            for seeder in peer.get_list_seeder():
                # print(seeder.strip())
                ip, port = seeder.strip().split(':')
            print("ip %s port %s" % (ip,port))

            Client(str(ip), int(port), filename, args.debug)

    except Exception as ex:
        print(ex)

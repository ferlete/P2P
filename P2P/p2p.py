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
    default_ip = '127.0.0.1'
    info = Info('authors', 'ferlete@gmail.com', 'P2P FACOM')
    policy = SEQUENCIAL_POLICY
    seeder_alive = []
    show_statistics = False
    show_graphic = False
    parallel = False

    parser = argparse.ArgumentParser(description=info.get_app_name())
    parser.add_argument('--type', '-t', dest="type", help='choice server or client',
                        default='server')  # server or client
    parser.add_argument('--policy', '-m', dest="policy", help='transmission policy (sequencial, random, semi-random)',
                        type=str,
                        default=policy)  # transmission policy
    parser.add_argument('--ip', '-i', dest="ip", help='server IP', type=str, default=default_ip)  # IP Server
    parser.add_argument('--port', '-p', dest="port", help='server port', type=int, default=default_port)  # port Server
    parser.add_argument('--version', '-v', action='version', version=info.get_app_name() + __version__)  # show version
    parser.add_argument('--statistic', action='store_true', help='show statistics only localhost server and client')
    parser.add_argument('--graphic', action='store_true', help='Show Grafic only localhost server and client')
    parser.add_argument('--parallel', action='store_true', help='Make parallel download')

    args = parser.parse_args()

    # policy transfer file
    if args.policy == RANDOM_POLICY:
        policy = RANDOM_POLICY
    if args.policy == SEMI_RANDOM_POLICY:
        policy = SEMI_RANDOM_POLICY

    try:

        # optional parameters
        if args.graphic:
            show_graphic = True
        if args.statistic:
            show_statistics = True
        if args.parallel:
            parallel = True

        if args.type == 'server':
            # start server
            Server(args.ip, args.port, policy)

        if args.type == 'client':
            # get seeder alive
            peer = Peer()
            for seeder in peer.get_list_seeder():
                ip, port = seeder.strip().split(':')
                if peer.check_seeder_alive(str(ip), int(port)):
                    seeder_alive.append(seeder)

            if len(seeder_alive) == 0:
                print("[-] P2P network does not have an active seeder. See file %s" % SEEDER_LIST)
                sys.exit()
            else:
                print("[+] P2P seeders alive % s" % seeder_alive)

            # connects to the first active seeder
            ip, port = seeder_alive[0].strip().split(':')
            filename = input('[+] Informe nome do arquivo: ')
            Client(str(ip), int(port), filename, seeder_alive, parallel, show_statistics, show_graphic)

    except Exception as ex:
        print(ex)

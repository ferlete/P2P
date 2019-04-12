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
from P2P.constants import *


def main():
    default_port = 9999
    server_ip = '127.0.0.1'
    info = Info('authors', 'ferlete@gmail.com', 'P2P FACOM')
    policy = 'sequential'

    parser = argparse.ArgumentParser(description=info.get_app_name())
    parser.add_argument('--type', '-t', dest="type", help='choice server or client',
                        default='server')  # server or client
    parser.add_argument('--policy', '-m', dest="policy", help='transmission policy', type=str,
                        default=policy)  # transmission policy
    parser.add_argument('--port', '-p', dest="port", help='server port', type=int, default=default_port)  # port Server
    parser.add_argument('--version', '-v', action='version', version=info.get_app_name() + __version__)  # show version
    parser.add_argument('--debug', help='increase output verbosity')

    args = parser.parse_args()
    if args.policy == 'randon':
        policy = 'randon'

    try:

        if args.type == 'server':
            # start server
            Server(server_ip, args.port, MUSIC_FOLDER, BLOCK_SIZE, policy)

        if args.type == 'client':
            filename = input('Informe nome do arquivo: ')
            peer = Peer()
            for seeder in peer.get_list_seeder():
                # print(seeder.strip())
                ip, port = seeder.strip().split(':')

            Client(str(ip), int(port), filename)
            #music = Music()
            #music.play_audio_segment()

            #music.convert_to_music(preview)

    except Exception as ex:
        print(ex)

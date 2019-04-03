__version__ = "0.1"

# import from python
import sys
import argparse
import threading
import time
from random import randint

# import from project P2P
from .info import Info
from .server import Server
from .client import Client
from .fileIO import FileIO


list_hosts_peers = [] # list of hosts servers
list_port_peers = [] # list of ports servers

BYTE_SIZE = 1024
PEER_BYTE_DIFFERENTIATOR = b'\x11'
RAND_TIME_START = 1
RAND_TIME_END = 2
REQUEST_STRING = "req"

 # make ourself the default peer
peers = ['127.0.0.1:8889']

def main():

    default_port = 8889
    server_ip = '127.0.0.1'
    info = Info('Andre, Patrik e Valter', 'ferlete@gmail.com')

    parser = argparse.ArgumentParser(description='P2P tester')
    parser.add_argument('--type', '-t', help='choice server or client', default='server')  # server or client
    parser.add_argument('--port', '-p', help='server port', type=int, default=default_port)  # port Server
    parser.add_argument('--version', '-v', action='version', version='P2P ' + __version__) # show version
    parser.add_argument('--debug', help='increase output verbosity')

    args = parser.parse_args()
    file = FileIO
    msg = file.convert_to_bytes()

    if args.type == 'server':
        # become the server
        try:
            Server(server_ip, args.port, msg)
        except KeyboardInterrupt:
            sys.exit()

    if args.type == 'client':
        print("-" * 21 + "Trying to connect" + "-" * 21)
        for peer in peers:
            print(peer)
            try:
                ip, port = peer.strip().split(':')
                Client(ip, port)

            except KeyboardInterrupt:
                sys.exit(0)
            except:
                pass


def loadpeers():
    with open('list_server.txt', 'r') as peers:
        for peer in peers:
            ip, port = peer.strip().split(':')
            list_hosts_peers.append(ip)
            list_port_peers.append(port)

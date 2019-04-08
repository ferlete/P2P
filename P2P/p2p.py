__version__ = "0.1"

# import from python
import sys, os
import argparse
import threading

# import from project P2P
from .info import Info
from .server import Server
from .client import Client
from .peer import Peer


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
            Server(server_ip, args.port, transport)

        if args.type == 'client':
            peer = Peer()
            for node_peer in peer.get_list_peer():
                #print(node_peer.strip())
                ip, port = node_peer.strip().split(':')
            Client(str(ip), int(port), "test.txt")


    except Exception as ex:
        print(ex)




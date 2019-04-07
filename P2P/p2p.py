__version__ = "0.1"

# import from python
import sys
import argparse
import threading

# import from project P2P
from .info import Info
from .server import Server
from .client import Client

list_hosts_peers = []  # list of hosts servers
list_port_peers = []  # list of ports servers

PEER_BYTE_DIFFERENTIATOR = b'\x11'
RAND_TIME_START = 1
RAND_TIME_END = 2


def main():
    default_port = 9999
    server_ip = '127.0.0.1'
    info = Info('Andre, Patrik e Valter', 'ferlete@gmail.com')
    msg = "Server Hello"
    transport = "TCP"

    parser = argparse.ArgumentParser(description='P2P tester')
    parser.add_argument('--type', '-t', dest="type", help='choice server or client',
                        default='server')  # server or client
    parser.add_argument('--tcp', dest="tcp", action='store_true', help='use TCP for transport', default=True,
                        required=False)  # User default TCP for transport
    parser.add_argument('--udp', dest="udp", action='store_true', help='use UDP for transport', default=False,
                        required=False)  # User default TCP for transport
    parser.add_argument('--port', '-p', dest="port", help='server port', type=int, default=default_port)  # port Server
    parser.add_argument('--version', '-v', action='version', version='P2P tester version ' + __version__)  # show version
    parser.add_argument('--debug', help='increase output verbosity')

    args = parser.parse_args()
    if args.tcp:
        transport = "TCP"
    if args.udp:
        transport = "UDP"

    print("P2P tester version " + __version__)
    print(info.get_authors())

    try:
        if args.type == 'server':
            Server(server_ip, args.port, transport, msg)

        if args.type == 'client':
            loadpeers()
            #for i in range(len(list_hosts_peers)):
            Client(str(list_hosts_peers[0]), int(list_port_peers[0]))


    except Exception as ex:
        print(ex)


def loadpeers():
    with open('list_server.txt', 'r') as peers:
        for peer in peers:
            ip, port = peer.strip().split(':')
            list_hosts_peers.append(ip)
            list_port_peers.append(port)

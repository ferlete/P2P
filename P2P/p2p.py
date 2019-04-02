__version__ = "0.1"

# import from python
import sys
import argparse
import threading

# import from project P2P
from .info import Info
from .server import Server


def main():

    default_port = 9999
    server_ip = '127.0.0.1'

    info = Info('Andre, Patrik e Valter', 'ferlete@gmail.com')

    parser = argparse.ArgumentParser(description='P2P tester')
    parser.add_argument('--type', '-t', help='choice server or client', default='server')  # server or client
    parser.add_argument('--port', '-p', help='server port', type=int, default=default_port)  # port Server
    parser.add_argument('--version', '-v', action='version', version='P2P ' + __version__) # show version
    parser.add_argument('--debug', help='increase output verbosity')

    args = parser.parse_args()

    try:
        if args.type == 'server':
            server = Server(server_ip, args.port)
            server.run()

        if args.type == 'client':
            print("Not implemented")



    except Exception as ex:
        print(ex)




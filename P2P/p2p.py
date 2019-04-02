__version__ = "0.1"

# import from python
import sys
import argparse
import threading

# import from project P2P
from .info import Info
from .server import Server


def main():

    inital_port = 9999
    info = Info('Andre, Patrik e Valter', 'ferlete@gmail.com')

    parser = argparse.ArgumentParser(description='P2P tester')
    parser.add_argument('--type', '-t', help='choice server or client', default='server')  # server or client
    parser.add_argument('--instance', '-i', help='number of instances', type=int, default=1)  # number of instances of server
    parser.add_argument('--version', '-v', action='version', version='P2P ' + __version__) # show version
    parser.add_argument('--debug', help='increase output verbosity')

    args = parser.parse_args()

    try:
        if args.type == 'server':
            server = Server(inital_port)
            server.run()

        if args.type == 'client':
            print("Not implemented")



    except Exception as ex:
        print(ex)




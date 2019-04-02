__version__ = "0.1"

import sys
from .info import Info
from .server import Server


def main():
    info = Info('Andre, Patrik e Valter', '1')
    print("P2P version %s" % __version__)
    print("Authors %s" % info.author)

    try:
       server = Server(9998)
       server.run()

    except Exception as ex:
        print(ex)




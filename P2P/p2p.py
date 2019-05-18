__version__ = "0.1"

import argparse
import sys
from PyQt5.QtWidgets import QApplication

from P2P.constants import *
from P2P.info import Info
from P2P.leecher import Leecher
from P2P.seeder import Seeder


def main():
    """
        main function.

        The main function of the application

        Returns
        -------
        nothing

    """
    default_port = 9000
    default_ip = '127.0.0.1'
    info = Info('authors', 'ferlete@gmail.com', 'P2P FACOM')
    policy = SEQUENCIAL_POLICY  # defaul policy

    parser = argparse.ArgumentParser(description=info.get_app_name())
    parser.add_argument('--type', '-t', dest="type", help='Escolha seeder ou leecher',
                        default='seeder')  # Seeder or Leecher
    parser.add_argument('--policy', '-m', dest="policy",
                        help='Politica de transmissão (sequencial, random, semi-random)',
                        type=str,
                        default=policy)  # transmission policy
    parser.add_argument('--ip', '-i', dest="ip", help='IP do Seeder', type=str, default=default_ip)  # IP Seeder
    parser.add_argument('--port', '-p', dest="port", help='Porta do Seeder', type=int,
                        default=default_port)  # port Server
    parser.add_argument('--version', '-v', action='version', version=info.get_app_name() + __version__)  # Show version

    args = parser.parse_args()

    # policy transfer file
    if args.policy == RANDOM_POLICY:
        policy = RANDOM_POLICY
    if args.policy == SEMI_RANDOM_POLICY:
        policy = SEMI_RANDOM_POLICY

    try:

        if args.type == 'seeder':
            # start server
            Seeder(args.ip, args.port, policy)

        if args.type == 'leecher':
            # starts the graphical user interface
            app = QApplication(sys.argv)
            form = Leecher()
            form.show()
            sys.exit(app.exec_())

    except Exception as ex:
        print(ex)

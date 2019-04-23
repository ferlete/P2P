import socket
import sys, os
import threading
import errno
from socket import error as socket_error

from P2P.constants import *


class Peer:

    def __init__(self):
        cwd = os.getcwd()
        self.list_peers = []
        self.filename_seeder = cwd + "/" + 'list_seeder.txt'

    """
        reads seeder from file
    """
    def get_list_seeder(self):
        if os.path.isfile(self.filename_seeder):
            with open(self.filename_seeder, 'r') as peers:
                for peer in peers:
                    self.list_peers.append(peer)

        else:
            print("[-] list seeder not found")
            sys.exit()

        return self.list_peers

    """
        saves in file information of ip and port of the new seeder
    """
    def save_new_seeder(self, ip, port):
        if os.path.isfile(self.filename_seeder):
            if not str(ip) + ":" + str(port) in open(self.filename_seeder).read():
                with open(self.filename_seeder, 'a') as outfile:
                    outfile.write(str(ip) + ":" + str(port) + "\n")
                outfile.close()
        else:
            with open(self.filename_seeder, 'a') as outfile:
                outfile.write(str(ip) + ":" + str(port) + "\n")
            outfile.close()

    """
        Check if seeder is active
    """
    def check_seeder_alive(self, ip, port):
        try:
            server_address = (ip, port)

            # Create a UDP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # allow python to use recently closed socket
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            s.connect(server_address)
            s.settimeout(0.001)
            s.sendto(PING_REQUEST.encode(), server_address)
            data, server = s.recvfrom(BUFFER_SIZE)
            if data[:4].decode() == PONG_REQUEST:
                return True
            else:
                return False

        except socket_error as serr:
            if serr.errno != errno.ECONNREFUSED:
                return False

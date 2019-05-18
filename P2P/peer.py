import errno
import os
import socket
import sys
import threading
import time
from socket import error as socket_error

from P2P.constants import *


class Peer:

    def __init__(self):
        """
            class initialization.

            initializes the Peer class

            Parameters
            ----------
            nothing

            Returns
            -------
            nothing

        """

        self.list_peers = []
        self.count_seeders = 0

    def get_list_seeder(self):
        """
            Reads seeder from file.

            this function reads from the file the seeder list

            Parameters
            ----------
            nothing

            Returns
            -------
            list
                list of seeder

        """
        if os.path.isfile(FILENAME_SEEDER):
            with open(FILENAME_SEEDER, 'r') as peers:
                for peer in peers:
                    self.list_peers.append(peer)
                    self.count_seeders += 1

        else:
            print("[-] list seeder not found")
            sys.exit()

        return self.list_peers

    def save_new_seeder(self, ip, port):
        """
           Saves in file information of ip and port of the new seeder.

            This function saves the ip and port on file when the seeder is started

            Parameters
            ----------
            ip : str
                server ip
            port: int
                server port

            Returns
            -------
            nothing

        """
        if os.path.isfile(FILENAME_SEEDER):
            if not str(ip) + ":" + str(port) in open(FILENAME_SEEDER).read():
                with open(FILENAME_SEEDER, 'a') as outfile:
                    outfile.write(str(ip) + ":" + str(port) + "\n")
                outfile.close()
        else:
            with open(FILENAME_SEEDER, 'a') as outfile:
                outfile.write(str(ip) + ":" + str(port) + "\n")
            outfile.close()

    def check_seeder_alive(self, ip, port):
        """
           Check if seeder is active.

            this function checks if this asset is seeder

            Parameters
            ----------
            ip : str
                server ip
            port: int
                server port

            Returns
            -------
            bool
                true if seeder is alive or false if seeder is down

        """
        try:
            server_address = (ip, port)

            # Create a UDP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # allow python to use recently closed socket
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            s.connect(server_address)
            s.settimeout(TIMEOUT_CONNECT)
            s.sendto(PING_REQUEST.encode(), server_address)
            data, server = s.recvfrom(BUFFER_SIZE)
            s.close()

            if data[:4].decode() == PONG_RESPONSE:
                return True
            else:
                return False

        except socket_error as serr:
            if serr.errno != errno.ECONNREFUSED:
                return False

    def get_policy_seeder(self, ip, port):
        """
           Get policy of seeder.

            this function sends a UDP packet to seeder requesting the policy that the server
            is working

            Parameters
            ----------
            ip : str
                server ip
            port: int
                server port

            Returns
            -------
            str
                policy seeder

        """
        try:
            server_address = (ip, port)

            # Create a UDP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # allow python to use recently closed socket
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            s.connect(server_address)
            s.settimeout(TIMEOUT_CONNECT)
            s.sendto(POLICY_REQUEST.encode(), server_address)
            data, server = s.recvfrom(BUFFER_SIZE)
            s.close()

            return data.decode()

        except socket_error as serr:
            if serr.errno != errno.ECONNREFUSED:
                return None

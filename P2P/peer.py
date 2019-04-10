import socket
import sys, os
import threading


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
        pass
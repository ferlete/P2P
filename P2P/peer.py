import socket
import sys, os
import threading


class Peer:

    def __init__(self):
        cwd = os.getcwd()
        self.list_peers = []
        self.filename_peer = cwd + "/" + 'list_peer_servers.txt'

    """
        reads peer file
    """
    def get_list_peer(self):
        if os.path.isfile(self.filename_peer):
            with open(self.filename_peer, 'r') as peers:
                for peer in peers:
                    self.list_peers.append(peer)
                    #ip, port = peer.strip().split(':')

        else:
            print("[-] list peer not found")
            sys.exit()

        return self.list_peers

    """
        saves in file information of ip and port of the new server
    """
    def save_new_peer_server(self, ip, port):
        if os.path.isfile(self.filename_peer):
            if not str(ip) + ":" + str(port) in open(self.filename_peer).read():
                with open(self.filename_peer, 'a') as outfile:
                    outfile.write(str(ip) + ":" + str(port) + "\n")
                outfile.close()
        else:
            with open(self.filename_peer, 'a') as outfile:
                outfile.write(str(ip) + ":" + str(port) + "\n")
            outfile.close()

    """
        Check if host is active
    """
    def check_peer_alive(self, ip, port):
        pass
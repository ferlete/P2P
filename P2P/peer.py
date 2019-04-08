import socket
import sys, os
import threading

class Peer:

    list_peers = []

    def get_list_peer(self):
        cwd = os.getcwd()
        path_to_list_peer = cwd + "/list_peer_servers.txt"
        if os.path.isfile(path_to_list_peer):
            with open(path_to_list_peer, 'r') as peers:
                for peer in peers:
                    self.list_peers.append(peer)
                    #ip, port = peer.strip().split(':')

        else:
            print("[-] list peer not found")
            sys.exit()

        return self.list_peers

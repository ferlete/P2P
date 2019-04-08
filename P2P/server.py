import select, socket, sys, os
import threading
import numpy

from .peer import Peer


class Server:
    connections = []
    msg = ""
    protocol = 'TCP'
    REQUEST_STRING = "GET FILE"
    BUFFER_SIZE = 1024
    BLOCK_SIZE = 1024
    music_folder = "/music/"

    def __init__(self, ip, port, protocol):
        try:
            self.protocol = protocol

            if self.protocol == 'TCP':
                # define a socket TCP
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if self.protocol == 'UDP':
                # define a socket UDP
                self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.connections = []

            # make a list of peers
            self.peers = []

            # bind the socket
            self.s.bind((ip, port))

            if self.protocol == 'TCP':
                # listen for connection
                self.s.listen(1)

            print("[*] Server listen on %s %s:%d" % (protocol, ip, port))

            # save peer server node to file
            peer = Peer()
            peer.save_new_peer_server(ip, port)


            self.run()

        except Exception as e:
            print(e)
        sys.exit()

    def slice_file(self, filename, number_peers, part_number):
        if os.path.isfile(filename):
            fo = open(filename, "wt")
            size_file = os.path.getsize(filename)
            size_per_node = int(size_file / number_peers)
            fo.seek(0, 0)
            str = fo.read(25)
            print(size_file)
            print(size_per_node)



    def handler_tcp(self, connection, a):
        filename = connection.recv(self.BUFFER_SIZE)

        cwd = os.getcwd()
        path_to_file = cwd + self.music_folder + filename.decode('utf-8').strip()

        self.slice_file(path_to_file, 3, 1)

        print("[*] request filename: %s " % path_to_file)
        if os.path.isfile(path_to_file):
            response = "EXISTS " + str(os.path.getsize(path_to_file))
            connection.send(response.encode())
            userResponse = connection.recv(self.BUFFER_SIZE)
            if userResponse[:2].decode() == "OK":
                print("[+] sending file...")
                with open(path_to_file, 'rb') as f:
                    bytesToSend = f.read(self.BLOCK_SIZE)
                    connection.send(bytesToSend)
                    while bytesToSend != "":
                        bytesToSend = f.read(self.BLOCK_SIZE)
                        connection.send(bytesToSend)
            print("[+] upload completed")
        else:
            connection.send("ERR".encode())
        self.disconnect(connection,a)

    def handler_udp(self, client, udp_data):
        # seek for "GET FILE"
        if udp_data and udp_data.decode('utf-8').strip() == self.REQUEST_STRING:
            # send file data
            print("-" * 3 + " UPLOADING file NOT IMPLEMENTED for UDP" + "-" * 3)
            self.s.sendto(self.msg, client)
        else:
            pass

    def run(self):
        # constantly listeen for connections
        connection = []
        data = []
        if self.protocol == 'TCP':
            while True:
                connection, a = self.s.accept()
                # append to the list of peers
                self.peers.append(a)
                print("[+] Peers client are: {}".format(self.peers))
                # self.send_peers()

                # create a thread for a TCP connection
                c_thread = threading.Thread(target=self.handler_tcp, args=(connection, a))
                c_thread.daemon = True
                c_thread.start()
                self.connections.append(connection)

        if self.protocol == 'UDP':
            while True:
                data, client = self.s.recvfrom(1024)
                if data:
                    print('[*] Received data from client %s: %s' % client, data.decode('utf-8'))
                    # create a thread for a UDP connection
                    c_thread = threading.Thread(target=self.handler_udp, args=(client, data))
                    c_thread.daemon = False
                    c_thread.start()
                    print("-" * 50)

    """
        This method is run when the user disconencts
    """
    def disconnect(self, connection, a):
        self.connections.remove(connection)
        self.peers.remove(a)
        connection.close()
        #self.send_peers()
        print("[-] disconnected {}".format(a))






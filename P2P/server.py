import select, socket, sys, os
import threading
import numpy

from .peer import Peer
from .fileIO import FileIO


class Server:
    connections = []
    REQUEST_FILE = "GET FILE:"
    BUFFER_SIZE = 1024
    BLOCK_SIZE = 1024
    SEQUENCIAL_POLICY = 'sequencial'

    def __init__(self, ip, port, protocol, music_folder, block_size, policy):
        try:

            self.protocol = protocol
            self.policy = policy
            self.music_folder = music_folder
            self.block_size = block_size

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

            print("[*] Server listen on %s %s:%d method %s" % (protocol, ip, port, policy))

            # save peer server node to file
            peer = Peer()
            peer.save_new_seeder(ip, port)

            self.run()

        except Exception as e:
            print(e)
        sys.exit()

    def handler_tcp(self, connection, a):
        filename = connection.recv(self.BUFFER_SIZE)

        cwd = os.getcwd()
        path_to_file = cwd + self.music_folder + filename.decode('utf-8').strip()

        print("[*] request filename: %s " % path_to_file)
        if os.path.isfile(path_to_file):
            response = "EXISTS"
            connection.send(response.encode())
            userResponse = connection.recv(self.BUFFER_SIZE)
            if userResponse[:5].decode() == "SLICE":
                slice = userResponse[5:].decode()
                #print("slice %s" % slice)
                file = FileIO(self.music_folder, self.block_size)
                if file.slice_exists(filename.decode('utf-8').strip(),int(slice)):
                    bytesToSend = file.get_slice_file(filename.decode('utf-8').strip(), int(slice))
                    #print(bytesToSend) for debug
                    response = "LEN" + str(len(bytesToSend))
                    connection.send(response.encode())
                    print("[+] sending slice %s" % slice)
                    connection.send(bytesToSend)
                    print("[+] upload slice completed")
                else:
                    response = "LEN0"
                    bytesToSend = ''
                    connection.send(response.encode())
                    print("[-] slice %s not found" % slice)
        else:
            connection.send("ERR".encode())
        self.disconnect(connection,a)

    def handler_udp(self, client, udp_data):
        # "GET FILE:"
        if udp_data[:9].decode('utf-8').strip() == self.REQUEST_FILE:
            # send file data
            filename = udp_data[9:].decode('utf-8').strip()
            print("[*] Leecher request filename: %s " % filename)
            file = FileIO(self.music_folder, self.block_size)
            if file.file_exists(filename):
                responde = 'EXISTS ' + str(file.get_file_size(filename))
                self.s.sendto(responde.encode('utf-8'), client)
                if self.policy == self.SEQUENCIAL_POLICY:
                       self.send_file_sequencial(filename, client)
            else:
                self.s.sendto("FILE NOT FOUND".encode('utf-8'), client)
        else:
            pass

    def send_file_sequencial(self, filename, socket):
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
                print("[+] Leechers are: {}".format(self.peers))
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
                    #print('[*] Received data from leecher %s: %s' % client, data.decode('utf-8'))
                    # create a thread for a UDP connection
                    c_thread = threading.Thread(target=self.handler_udp, args=(client, data))
                    c_thread.daemon = False
                    c_thread.start()

    """
        This method is run when the user disconencts
    """
    def disconnect(self, connection, a):
        self.connections.remove(connection)
        self.peers.remove(a)
        connection.close()
        #self.send_peers()
        print("[-] disconnected {}".format(a))






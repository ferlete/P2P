import select, socket, sys, os
import threading
import numpy
import time

from .peer import Peer
from .fileIO import FileIO
from P2P.constants import *


class Server:
    connections = []

    def __init__(self, ip, port, music_folder, block_size, policy):
        try:
            self.policy = policy
            self.music_folder = music_folder
            self.block_size = block_size
            self.filename = ''

            #define a socket UDP
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.connections = []

            # make a list of peers
            self.peers = []

            # bind the socket
            self.s.bind((ip, port))

            print("[*] Server listen on UDP %s:%d method %s" % (ip, port, policy))

            # save peer server node to file
            peer = Peer()
            peer.save_new_seeder(ip, port)

            self.run()

        except Exception as e:
            print(e)
        sys.exit()

    def handler_udp(self, client, udp_data):
        try:
            # "GET FILE:"
            if udp_data[:9].decode('utf-8').strip() == GET_FILE_STRING:
                # Request File
                self.filename = udp_data[9:].decode('utf-8').strip()
                print("[*] Leecher %s request filename: %s " % (client, self.filename))
                file = FileIO(self.music_folder, self.block_size)
                if file.file_exists(self.filename):
                    response = EXISTS_STRING + str(file.get_file_size(self.filename))
                    self.s.sendto(response.encode('utf-8'), client)
                else:
                    self.s.sendto(NOT_FOUND_STRING.encode('utf-8'), client)
            if udp_data[:14].decode('utf-8').strip() == DOWNLOAD_STRING:
                # Request download File
                print("[*] Leecher {} request download".format(client))
                if self.policy == SEQUENCIAL_POLICY:
                    self.send_file_sequencial(self.filename, client)
        except Exception as ex:
            print(ex)

    def send_file_sequencial(self, filename, client):
        try:
            file = FileIO(self.music_folder, self.block_size)
            file_size = file.get_file_size(filename)
            num_of_packet = int(self.calc_number_chunk(file_size))
            for i in range(num_of_packet):
                data = file.get_slice_file(filename, i)
                new_data = bytes(self.make_header(i), encoding='utf8') + data
                print("[+] Sending packet %d to %s" % (i,client))
                self.s.sendto(new_data, client)
                time.sleep(.1)  #delay 20 miliseconds
        except Exception as ex:
            print(ex)
        except KeyboardInterrupt:
            self.s.close()

    def run(self):
        try:
            # constantly listeen for connections
            while True:
                data, client = self.s.recvfrom(1024)
                if data:
                    # create a thread for a UDP connection
                    c_thread = threading.Thread(target=self.handler_udp, args=(client, data))
                    c_thread.daemon = True
                    c_thread.start()
        except Exception as ex:
            print(ex)
        except KeyboardInterrupt:
            self.s.close()

    """
        calculate the number of chunks to be created
    """
    def calc_number_chunk(self, bytes):
        noOfChunks = int(bytes) / BLOCK_SIZE
        if (bytes % BLOCK_SIZE):
            noOfChunks += 1
        return noOfChunks

    def make_header(self, packet_number):
        return '%05d' % packet_number

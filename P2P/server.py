import select, socket, sys, os
import threading
import numpy
import time
import random
import binascii

from .peer import Peer
from .fileIO import FileIO
from .progress import Progress
from P2P.constants import *


class Server:
    connections = []

    def __init__(self, ip, port, policy):
        try:
            self.policy = policy
            self.filename = ''
            self.filelog = FileIO()
            self.packet_send_time = []  # array with timestamp packet send
            self.progress = Progress()

            # define a socket UDP
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
                file = FileIO()
                if file.file_exists(self.filename):
                    response = EXISTS_STRING + str(file.get_file_size(self.filename))
                    self.s.sendto(response.encode('utf-8'), client)
                else:
                    self.s.sendto(NOT_FOUND_STRING.encode('utf-8'), client)
            # "DOWNLOAD FILE:"
            if udp_data[:14].decode('utf-8').strip() == DOWNLOAD_STRING:
                # Request download File
                print("[*] Leecher {} request download".format(client))
                if self.policy == SEQUENCIAL_POLICY:
                    self.send_file_sequencial(self.filename, client)
                if self.policy == RANDOM_POLICY:
                    self.send_file_randon(self.filename, client)

            # "PING REQUEST:"
            if udp_data[:4].decode('utf-8').strip() == PING_REQUEST:
                self.s.sendto(PONG_REQUEST.encode('utf-8'), client)

        except Exception as ex:
            print(ex)

    def send_file_randon(self, filename, client):
        try:
            print("[+] Sending file %s to Leecher %s" % (filename, client))
            i = 0
            data = []  # binary data chunk file
            file = FileIO()
            total_packet = int(file.get_num_packet(filename))

            self.packet_send_time = [None] * total_packet

            # list of packet random
            list_packets = random.sample(range(0, total_packet), total_packet)

            data = file.get_file_array(filename)

            for packet_id in list_packets:
                # print("send packet %d " % int(packet_id))
                # if int(packet_id) == 0:
                #    print("send packet %d " % int(packet_id))
                #    print(data[int(packet_id)])
                # sys.exit()
                new_data = bytes(self.make_header(packet_id), encoding='utf8') + data[int(packet_id)]

                if self.s.sendto(new_data, client):
                    ts = time.time()  # time stamp departure
                    self.packet_send_time[packet_id] = ts
                    time.sleep(DELAY_FOR_SEND)  # Give receiver a bit time to send packet
                    self.progress.printProgressBar(i, total_packet - 1, prefix='[+] Progress:', suffix='Complete',
                                                   length=60)
                i += 1
            self.filelog.save_log_send(self.packet_send_time)

        except Exception as ex:
            print(ex)
        except KeyboardInterrupt:
            self.s.close()

    def send_file_sequencial(self, filename, client):
        try:
            print("[+] Sending file %s to Leecher %s" % (filename, client))
            packet_id = 0
            file = FileIO()
            total_packet = int(file.get_num_packet(filename))
            filename = CURRENT_DIR + MUSIC_FOLDER + filename

            self.packet_send_time = [None] * total_packet

            f = open(filename, "rb")
            data = f.read(BLOCK_SIZE)
            while data:
                new_data = bytes(self.make_header(packet_id), encoding='utf8') + data
                if self.s.sendto(new_data, client):
                    ts = time.time()  # time stamp departure
                    self.packet_send_time[packet_id] = ts
                    data = f.read(BLOCK_SIZE)
                    time.sleep(DELAY_FOR_SEND)  # Give receiver a bit time to send packet
                    self.progress.printProgressBar(packet_id, total_packet - 1, prefix='[+] Progress:',
                                                   suffix='Complete', length=60)
                packet_id += 1

            # self.s.close()
            f.close()
            self.filelog.save_log_send(self.packet_send_time)

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
        generate header with packet number
    """
    def make_header(self, packet_number):
        return '%05d' % packet_number

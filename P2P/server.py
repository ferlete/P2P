import select, socket, sys, os
import threading
import numpy
import time
import random

from .peer import Peer
from .fileIO import FileIO
from P2P.constants import *


class Server:
    connections = []

    def __init__(self, ip, port, policy):
        try:
            self.policy = policy
            self.filename = ''
            self.packet_send_time = []  # array with timestamp packet send

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
                file = FileIO(MUSIC_FOLDER, BLOCK_SIZE)
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
                if self.policy == RANDON_POLICY:
                    self.send_file_randon(self.filename,client)
        except Exception as ex:
            print(ex)

    def send_file_randon(self, filename, client):
        print("[+] Sending file %s to Leecher %s" % (filename, client))
        packet_id = 0
        file = FileIO(MUSIC_FOLDER, BLOCK_SIZE)
        total_packet = int(file.get_num_packet(filename))
        print(total_packet)
        list = random.sample(range(0, total_packet), total_packet)
        #print(lista)
        data = file.get_file_array(filename)
        print(data[0])


    def send_file_sequencial(self, filename, client):
        try:
            print("[+] Sending file %s to Leecher %s" % (filename, client))
            packet_id = 0
            file = FileIO(MUSIC_FOLDER, BLOCK_SIZE)
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
                    self.printProgressBar(packet_id, total_packet-1, prefix='[+] Progress:', suffix='Complete', length=60)
                packet_id += 1

            #self.s.close()
            f.close()
            self.save_log_send()

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
        save log time send packets
    """
    def save_log_send(self):
        filename_send_time = "time.log"
        f_send = open(filename_send_time, 'w')
        for i in range(len(self.packet_send_time)):
            f_send.write(str(i) + ':' + str(self.packet_send_time[i]) + '\n')
        f_send.close()

    """
        calculate the number of chunks to be created
    """
    def calc_number_chunk(self, bytes):
        noOfChunks = int(bytes) / BLOCK_SIZE
        if (bytes % BLOCK_SIZE):
            noOfChunks += 1
        return noOfChunks

    """
        generate header with packet number
    """
    def make_header(self, packet_number):
        return '%05d' % packet_number

    """ 
        Print iterations progress
    """
    def printProgressBar(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
        # Print New Line on Complete
        if iteration == total:
            print()

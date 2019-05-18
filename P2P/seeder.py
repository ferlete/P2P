import numpy
import random
import socket
import sys
import threading
import time

from P2P.constants import *
from .fileIO import FileIO
from .peer import Peer
from .progress import Progress


class Seeder:
    connections = []
    __abort = False

    def __init__(self, ip, port, policy):
        """
            class initialization.

            initializes the server class

            Parameters
            ----------
            ip : str
                server ip
            port: int
               server port
            policy: str
                policy server

            Returns
            -------
            nothing

        """
        try:
            self.policy = policy
            self.filename = ''
            self.filelog = FileIO()
            self.progress = Progress()

            # define a socket UDP
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.connections = []

            # make a list of peers
            self.peers = []

            # bind the socket
            self.s.bind((ip, port))

            print("[*] Seeder listen on UDP %s:%d method %s" % (ip, port, policy))

            # save peer server node to file
            peer = Peer()
            peer.save_new_seeder(ip, port)

            self.run()

        except Exception as e:
            print(e)
        sys.exit()

    def handler_udp(self, client, udp_data):
        """
            handle UDP request.

           treats client UDP request

            Parameters
            ----------
            client : str
                client info (ip and port)
            udp_data: str
               UDP request data

            Returns
            -------
            nothing

        """
        try:
            # GET FILE REQUEST
            if udp_data[:9].decode('utf-8').strip() == GET_FILE_REQUEST:
                # Request File
                self.filename = udp_data[9:].decode('utf-8').strip()
                print("[*] Leecher %s consulted the filename: %s " % (client, self.filename))
                file = FileIO()
                if file.file_exists(self.filename):
                    response = EXISTS_RESPONSE + str(file.get_file_size(self.filename))
                    self.s.sendto(response.encode('utf-8'), client)
                else:
                    self.s.sendto(NOT_FOUND_RESPONSE.encode('utf-8'), client)

            # SLICE REQUEST
            if udp_data[:6].decode('utf-8').strip() == SLICE_REQUEST:
                self.__abort = False
                initial, finish, filename = udp_data[6:].decode('utf-8').strip().split(':')
                print("[*] Leecher %s request the filename: %s slice %d to %d  " % (
                    client, filename, int(initial), int(finish)))
                if int(initial) == int(finish):  # retransmit
                    self.send_slice(client, initial, filename)
                else:
                    self.send_file(client, initial, finish, filename, self.policy)
            # PING REQUEST
            if udp_data[:4].decode('utf-8').strip() == PING_REQUEST:
                self.s.sendto(PONG_RESPONSE.encode(), client)

            # POLICY REQUEST
            if udp_data[:6].decode('utf-8').strip() == POLICY_REQUEST:
                response = self.policy
                self.s.sendto(response.encode(), client)

            # KILL REQUEST
            if udp_data[:4].decode('utf-8').strip() == KILL_REQUEST:
                self.__abort = True

        except Exception as ex:
            print(ex)

    def send_slice(self, client, packet_id, filename):
        """
                    Send slice to leecher.

                    sends the slice requested by the client

                    Parameters
                    ----------
                    client : str
                        client info (ip and port)
                    packet_id: int
                        the packet number to be sent from the
                    filename: str
                        file name

                    Returns
                    -------
                    nothing

                """
        try:
            print("[+] Retransmitindo slice %s file %s to Leecher %s" % (packet_id, filename, client))

            file_array = FileIO()

            # data file
            data = file_array.get_file_array(filename)

            new_data = bytes(self.make_header(packet_id), encoding='utf8') + data[int(packet_id)]

            if self.s.sendto(new_data, client):
                time.sleep(DELAY_FOR_SEND)  # Give receiver a bit time to send packet

        except Exception as ex:
            print(ex)
        except KeyboardInterrupt:
            self.s.close()

    def send_file(self, client, initial, finish, filename, policy):
        """
            Send file to leecher.

            sends the file requested by the client

            Parameters
            ----------
            client : str
                client info (ip and port)
            initial: int
                the starting number of the packet to be sent from the
            finish: int
                Finish number of the packet to be sent from the file
            policy: str
                shipping policy

            Returns
            -------
            nothing

        """
        try:
            print("[+] Sending slice %s of %s file %s to Leecher %s" % (initial, finish, filename, client))
            i = 0
            total_packet = int(finish) - int(initial)
            file_array = FileIO()

            # data file
            data = file_array.get_file_array(filename)

            if policy == SEQUENCIAL_POLICY:
                for packet_id in range(int(initial), int(finish)):

                    if self.__abort:
                        print("[-] download canceled by Leecher")
                        break

                    new_data = bytes(self.make_header(packet_id), encoding='utf8') + data[int(packet_id)]

                    if self.s.sendto(new_data, client):
                        time.sleep(DELAY_FOR_SEND)  # Give receiver a bit time to send packet
                        self.progress.printProgressBar(i, total_packet - 1, prefix='[+] Progress:',
                                                       suffix='Complete',
                                                       length=60)
                    i += 1
            if policy == RANDOM_POLICY:
                # list of packet random
                list_packets = random.sample(range(int(initial), int(finish)), total_packet)

                for packet_id in list_packets:

                    if self.__abort:
                        print("[-] download canceled by Leecher")
                        break

                    new_data = bytes(self.make_header(packet_id), encoding='utf8') + data[int(packet_id)]
                    if self.s.sendto(new_data, client):
                        time.sleep(DELAY_FOR_SEND)  # Give receiver a bit time to send packet
                        self.progress.printProgressBar(i, total_packet - 1, prefix='[+] Progress:', suffix='Complete',
                                                       length=60)
                    i += 1
            if policy == SEMI_RANDOM_POLICY:
                half = int(total_packet / 2)

                # first 50% packets
                for packet_id in range(int(initial), int(initial) + half):

                    if self.__abort:
                        print("[-] download canceled by Leecher")
                        break

                    new_data = bytes(self.make_header(packet_id), encoding='utf8') + data[int(packet_id)]
                    if self.s.sendto(new_data, client):
                        time.sleep(DELAY_FOR_SEND)  # Give receiver a bit time to send packet
                        self.progress.printProgressBar(i, total_packet - 1, prefix='[+] Progress:',
                                                       suffix='Complete', length=60)
                    i += 1

                # last 50% packets
                initial = (int(initial) + half) + 1
                total = int(finish) - initial
                # list of packet random
                list_packets = random.sample(range(initial, int(finish)), total)

                for packet_id in list_packets:

                    if self.__abort:
                        print("[-] download canceled by Leecher")
                        break

                    new_data = bytes(self.make_header(packet_id), encoding='utf8') + data[int(packet_id)]

                    if self.s.sendto(new_data, client):
                        time.sleep(DELAY_FOR_SEND)  # Give receiver a bit time to send packet
                        self.progress.printProgressBar(i, total_packet - 1, prefix='[+] Progress:', suffix='Complete',
                                                       length=60)
                    i += 1

        except Exception as ex:
            print(ex)
        except KeyboardInterrupt:
            self.s.close()

    def run(self):
        """
            main loop

            main server loop, constantly listen for connections

            Returns
            -------
            nothing

        """
        try:
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

    def make_header(self, packet_number):
        """
            generate the header.

            generate header with packet number and time departure with 20 bytes(6 packet_id, 1 to separator and
            13 timestamp departure)

            Parameters
            ----------
            packet_number : int
                packet number

            Returns
            -------
            str
                header to UDP packet. Ex: 000001:1557778187085

        """
        milliseconds = int(round(time.time() * 1000))  # timestamp in ms departure
        header = '%06d' % int(packet_number)
        header += ":"
        header += str(milliseconds)
        return header

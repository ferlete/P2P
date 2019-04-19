import socket
import sys
import threading
import os
import time
import io
import matplotlib.pyplot as plt
import csv

from datetime import datetime
from pydub import AudioSegment
from pydub.playback import play


from .fileIO import FileIO
from .music import Music
from P2P.constants import *


class Client:

    def __init__(self, ip, port, filename):
        self.filename = filename
        self.server_address = (ip, port)
        self.packet = [] # array with packet lost or received
        self.packet_received_time = []  # array with timestamp packet received
        self.num_of_packet = 0
        try:

            # Create a UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # allow python to use recently closed socket
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Connect the socket to the port where the server is listening
            print('[+] Connecting to %s:%s' % self.server_address)
            self.socket.connect(self.server_address)

            # create to work on a different thread
            i_thread = threading.Thread(target=self.retr_file)
            i_thread.daemon = False
            i_thread.start()


        except Exception as e:
            print(e)
        sys.exit()

    def retr_file(self):
        print("[+] Resquest filename %s" % self.filename)
        request = GET_FILE_STRING + self.filename
        self.socket.sendto(request.encode(), self.server_address)
        data, server = self.socket.recvfrom(BUFFER_SIZE)
        if data[:7].decode() == EXISTS_STRING:
            file_size = int(data[7:].decode())

            self.num_of_packet = int(self.calc_number_chunk(file_size))
            
            self.packet = [False] * self.num_of_packet
            #self.packet_send_time = [None] * self.num_of_packet
            self.packet_received_time = [None] * self.num_of_packet

            request = DOWNLOAD_STRING + self.filename
            self.socket.sendto(request.encode(), self.server_address)

            new_filename = "new_" + self.filename
            f = open(new_filename, 'wb')
            data, addr = self.socket.recvfrom(BUFFER_SIZE)
            #print("[+] Received packet %d from seeder %s" % (int(data[:5].decode()), addr))
            print("[+] Receiving filename %s from % s" % (self.filename, addr))
            self.buffer_data = data # buffer for play

            # create to work on a different thread for play audio on download
            #t = threading.Timer(1.0, self.play_music_on_download, args=[new_filename])
            #t.start()

            try:
                while(data):
                    packet_id = int(data[:5].decode()) # five bytes for header
                    f.write(data[5:]) # save in disk packet bytes
                    self.socket.settimeout(1)
                    data, addr = self.socket.recvfrom(BUFFER_SIZE)
                    self.packet[packet_id] = self.simulation_layer_loss_and_delay() # simulation delay and loss

                    ts = time.time()  # timestamp in ms arrival
                    self.packet_received_time[packet_id] = ts
                    self.buffer_data += data[5:]
                    #print("[+] Received packet %d from seeder %s" % (int(data[:5].decode()), addr))

            except socket.timeout:
                f.close

                self.socket.close()
                print("[+] File Downloaded")
                self.save_log_received()
                self.show_statistics()
        else:
            print("[-] File does not Exists")
            self.socket.close()

    def save_log_received(self):
        filename_log_time = "time.log"
        f_received = open(filename_log_time, 'r')
        data = [item for item in csv.reader(f_received, delimiter=':')]
        f_received.close()
        new_data = []
        for i, item in enumerate(data):
            if self.packet_received_time[int(i)] == None:
                item.append(0)
            else:
                item.append(self.packet_received_time[int(i)])
            new_data.append(item)
        f = open(filename_log_time, 'w')
        csv.writer(f, delimiter=':').writerows(new_data)
        f.close()

    """
        Esta funcao deve retornar um booleano indicando se pacote chegou o foi perdido
    """
    def simulation_layer_loss_and_delay(self):
        return True

    def play_music_on_download(self, new_filename):
        try:
            # wait for 256Kb for play audio
            buffer_play = int(256 * kilobyte)

            print("[+] Buffering... wait %d bytes" % buffer_play)
            while len(self.buffer_data) <= buffer_play:
                pass

            print("[+] Play Buffer")
            # seg = AudioSegment(  # raw audio data (bytes)
            #     data=raw_data,
            #     # 2 byte (16 bit) samples
            #     sample_width=16,
            #     # 44.1 kHz frame rate
            #     frame_rate=44100,
            #     # stereo
            #     channels=2).set_frame_rate(16000)
            seg = AudioSegment.from_file(io.BytesIO(self.buffer_data), format="mp3")
            #
            # print("Information:")
            # print("Channels:", seg.channels)
            # print("Bits per sample:", seg.sample_width * 8)
            # print("Sampling frequency:", seg.frame_rate)
            print("Length:", seg.duration_seconds, "seconds") # da para fazer um calculo de quando segundos baixou para
            # #saber a taxa de perda e pacotes reproduzidos
            #

            play(seg) # toca  segmento

        except Exception as ex:
            print(ex)
            sys.exit()

    """
        calculate the number of chunks to be created
    """
    def calc_number_chunk(self, bytes):
        noOfChunks = int(bytes) / BLOCK_SIZE
        if (bytes % BLOCK_SIZE):
            noOfChunks += 1
        return noOfChunks

    def show_statistics(self):
        print(30*"-"+"Statistics"+30*"-")
        print("Total of packet %d" % self.num_of_packet)
        # using enumerate() + list comprehension
        # to return true indices.
        res = [i for i, val in enumerate(self.packet) if val]
        print("Num Packet received: %d" % len(res))
        lost = self.num_of_packet - len(res)
        print("Num Packet lost %d" % lost)

    def plot_grafic(self):
        plt.plotfile('send_time.log', delimiter=':', cols=(0, 1),
                     names=('Time', 'Packet Number'), marker='.')
        plt.show()

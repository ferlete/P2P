import socket
import sys
import threading
import os
import time
import io
import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime
from pydub import AudioSegment
from pydub.playback import play

from .fileIO import FileIO
from .progress import Progress
from .music import Music
from P2P.constants import *


class Client:

    def __init__(self, ip, port, filename, debug):
        self.filename = filename
        self.server_address = (ip, port)
        self.packet = []  # array with packet lost or received
        self.packet_received_time = []  # array with timestamp packet received
        self.num_of_packet = 0
        self.buffer_data = []
        self.progress = Progress()
        self.debug = debug
        self.logfile = FileIO()
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
            self.packet_received_time = [None] * self.num_of_packet
            self.buffer_data = [None] * self.num_of_packet

            request = DOWNLOAD_STRING + self.filename
            self.socket.sendto(request.encode(), self.server_address)

            data, addr = self.socket.recvfrom(BUFFER_SIZE)
            print("[+] Receiving filename %s from % s" % (self.filename, addr))
            packet_id = int(data[:5].decode())  # five bytes for header
            self.buffer_data[packet_id] = data[5:]  # buffer for play

            # create to work on a different thread for play audio on download
            # t = threading.Timer(1.0, self.play_music_on_download, args=[new_filename])
            # t.start()

            # teste recebimento do primeiro pacote
            # packet_id = int(data[:5].decode()) # five bytes for header
            # self.buffer_data[packet_id] = data[5:]
            # print("packet_id % d" % packet_id)
            # print(data[5:])
            # sys.exit()

            try:
                while (data):
                    self.socket.settimeout(1)
                    data, addr = self.socket.recvfrom(BUFFER_SIZE)
                    self.packet[packet_id] = self.simulation_layer_loss_and_delay()  # simulation delay and loss

                    packet_id = int(data[:5].decode())  # five bytes for header
                    self.progress.printProgressBar(packet_id, self.num_of_packet - 1, prefix='[+] Progress:',
                                                   suffix='Complete', length=60)

                    ts = time.time()  # timestamp in ms arrival
                    self.packet_received_time[packet_id] = ts
                    self.buffer_data[packet_id] = data[5:]

            except socket.timeout:
                self.socket.close()
                print("[+] File Downloaded")
                self.save_audio_file()
                if self.debug:
                    self.logfile.save_log_received(self.packet_received_time)
                    self.show_statistics()
                    self.plot_grafic_times()
        else:
            print("[-] File does not Exists")
            self.socket.close()

    def save_audio_file(self):
        new_filename = CURRENT_DIR + MUSIC_FOLDER + "new_" + self.filename
        f = open(new_filename, 'wb')
        for i in range(len(self.buffer_data)):
            if self.buffer_data[i] != None:
                f.write(self.buffer_data[i])  # save in disk packet bytes
        f.close()

    """
        Esta funcao deve retornar um booleano indicando se pacote chegou o foi perdido e aplicar delay
    """

    def simulation_layer_loss_and_delay(self):
        time.sleep(DELAY_FOR_TO_RECEIVE)  # Give receiver a bit time to received packet
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
            print("Length:", seg.duration_seconds, "seconds")  # da para fazer um calculo de quando segundos baixou para
            # #saber a taxa de perda e pacotes reproduzidos
            #

            play(seg)  # toca  segmento

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
        print(30 * "-" + "Statistics" + 30 * "-")
        print("Total of packet %d" % self.num_of_packet)
        # using enumerate() + list comprehension
        # to return true indices.
        res = [i for i, val in enumerate(self.packet) if val]
        print("Num Packet received: %d" % len(res))
        lost = self.num_of_packet - len(res)
        print("Num Packet lost %d" % lost)

    def plot_grafic(self):
        x, y, z = np.loadtxt('time.log', comments='#', delimiter=':', unpack=True)
        # TODO mark missing packet in chart
        # when the packet is lost the receiving time is matched with sending time
        for i in x:
            if z[int(i)] == 0:
                z[int(i)] = y[int(i)]

        fig = plt.figure()
        ax1 = fig.add_subplot(1, 2, 1)
        ax2 = fig.add_subplot(1, 2, 2)

        ax1.plot(x, y, label='Transmitted', color='green')
        ax2.plot(x, z, label='Received', color='red')

        ax1.set_xlabel('Time')
        ax1.set_ylabel('Packet')
        ax1.set_title('Transmitted')

        ax2.set_xlabel('Time')
        ax2.set_ylabel('Packet')
        ax2.set_title('Received')

        plt.show()

    def plot_grafic_times(self):
        x, y, z = np.loadtxt('time.log', comments='#', delimiter=':', unpack=True)
        # TODO mark missing packet in chart
        # when the packet is lost the receiving time is matched with sending time
        for i in x:
            if z[int(i)] == 0:
                z[int(i)] = y[int(i)]

        plt.plot(x, y, label='transmitted', linewidth=1.0)
        plt.plot(x, z, label='Received', linewidth=0.5)
        plt.xlabel('Time')
        plt.ylabel('Packet')
        plt.title('Tradeoff')
        plt.legend()
        plt.show()

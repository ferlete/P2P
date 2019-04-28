import socket
import sys
import threading
from threading import Thread, Condition
import os
import time
import io
import matplotlib.pyplot as plt
import numpy as np
import random

from datetime import datetime
from pydub import AudioSegment
from pydub.playback import play

from .fileIO import FileIO
from .progress import Progress
from .music import Music
from P2P.constants import *


class Client:

    def __init__(self, ip, port, filename, seeder_alive, show_statistics, show_graphic):
        self.filename = filename
        self.seeder_alive = seeder_alive
        self.server_address = (ip, port)
        self.packet = []  # array with packet lost or received
        self.packet_received_time = []  # array with timestamp packet received
        self.num_of_packet = 0
        self.buffer_data = []
        self.progress = Progress()
        self.show_statistics = show_statistics
        self.show_graphic = show_graphic
        self.logfile = FileIO()
        self.queue = []
        self.condition = Condition()

        try:

            # Create a UDP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # allow python to use recently closed socket
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Connect the socket to the port where the server is listening
            print('[+] Connecting to %s:%s' % self.server_address)
            s.connect(self.server_address)

            # create to work on a different thread
            self.i_thread = threading.Thread(target=self.retr_file, args=[s])
            self.i_thread.daemon = False
            self.i_thread.start()

        except Exception as e:
            print(e)
        sys.exit()

    def retr_file(self, s):
        print("[+] Request filename %s" % self.filename)
        # i = 0
        request = GET_FILE_STRING + self.filename
        s.sendto(request.encode(), self.server_address)
        data, server = s.recvfrom(BUFFER_SIZE)
        if data[:7].decode() == EXISTS_STRING:
            file_size = int(data[7:].decode())
            self.num_of_packet = int(self.calc_number_chunk(file_size))

            self.packet = [False] * self.num_of_packet
            self.packet_received_time = [None] * self.num_of_packet
            self.buffer_data = [None] * self.num_of_packet

            request = DOWNLOAD_STRING + self.filename
            s.sendto(request.encode(), self.server_address)

            data, addr = s.recvfrom(BUFFER_SIZE)
            print("[+] Receiving filename %s from % s" % (self.filename, addr))
            packet_id = int(data[:5].decode())  # five bytes for header
            self.buffer_data[packet_id] = data[5:]  # buffer for play
            self.buffer = data[5:]  # buffer for play

            # create to work on a different thread for play audio on download
            t = threading.Timer(1.0, self.play_music_on_download)
            t.start()
            try:
                while (data):
                    self.condition.acquire()
                    if len(self.queue) == MAX_PACKET_BUFFER: # buffer full
                        self.condition.wait() # Space in buffer, Consumer notified the producer

                    s.settimeout(1)
                    data, addr = s.recvfrom(BUFFER_SIZE)
                    self.packet[packet_id] = self.simulation_layer_loss_and_delay()  # simulation delay and loss
                    packet_id = int(data[:5].decode())  # five bytes for header
                    # self.progress.printProgressBar(i, self.num_of_packet - 1, prefix='[+] Progress:',
                    #                               suffix='Complete', length=60)

                    ts = time.time()  # timestamp in ms arrival
                    self.packet_received_time[packet_id] = ts
                    self.buffer_data[packet_id] = data[5:]

                    #queue packet audio for play
                    self.queue.append(packet_id)
                    self.condition.notify()
                    self.condition.release()
                    #time.sleep(random.random())

            except socket.timeout:
                s.close()
                print("[+] File Downloaded")
                self.save_audio_file()
                if self.show_statistics:
                    self.logfile.save_log_received(self.packet_received_time)
                    self.display_statistics()

                if self.show_graphic:
                    self.plot_grafic_times()
                    #self.plot_grafic_side_by_side()

                sys.exit(0)
        else:
            print("[-] File does not Exists")
            s.close()

    def save_audio_file(self):
        try:
            new_filename = CURRENT_DIR + MUSIC_FOLDER + "new_" + self.filename
            f = open(new_filename, 'wb')
            for i in range(len(self.buffer_data)):
                if self.buffer_data[i] != None:
                    f.write(self.buffer_data[i])  # save in disk packet bytes
                #else:
                #    print("lost packet %d" %i)
            f.close()
        except Exception as ex:
            print(ex)

    """
        Esta funcao deve retornar um booleano indicando se pacote chegou o foi perdido e aplicar delay
    """

    def simulation_layer_loss_and_delay(self):
        time.sleep(DELAY_FOR_TO_RECEIVE)  # Give receiver a bit time to received packet
        return True

    def play_audio(self, filename):
        print("[+] Real player...")
        seg = AudioSegment.from_file(filename, format="mp3")
        print("Length:", seg.duration_seconds, "seconds")
        play(seg)  # toca  musica

        # seg = AudioSegment(  # raw audio data (bytes)
        #     data=raw_data,
        #     # 2 byte (16 bit) samples
        #     sample_width=16,
        #     # 44.1 kHz frame rate
        #     frame_rate=44100,
        #     # stereo
        #     channels=2).set_frame_rate(16000)
        # seg = AudioSegment.from_file(io.BytesIO(bytes_of_values), format="mp3")
        #
        # print("Information:")
        # print("Channels:", seg.channels)
        # print("Bits per sample:", seg.sample_width * 8)
        # print("Sampling frequency:", seg.frame_rate)
        # print("Length:", seg.duration_seconds, "seconds")  # da para fazer um calculo de quando segundos baixou para
        # #saber a taxa de perda e pacotes reproduzidos
        #

        # play(seg)  # toca  segmento

    def play_music_on_download(self):
        try:
            while True:
                self.condition.acquire()
                if not self.queue:  # Buffer empty
                    self.condition.wait() # Producer added something to queue and notified the consumer
                num = self.queue.pop(0)
                #print("[-] Play packet %d" % num)
                self.condition.notify()
                self.condition.release()
                #time.sleep(random.random())

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

    def display_statistics(self):
        try:
            print(30 * "-" + "Statistics" + 30 * "-")
            print("Total of packet %d" % self.num_of_packet)
            # using enumerate() + list comprehension to return true indices.
            res = [i for i, val in enumerate(self.packet) if val]
            print("Num Packet received: %d" % len(res))
            lost = self.num_of_packet - len(res)
            print("Num Packet lost %d" % lost)
        except Exception as ex:
            print(ex)

    def plot_grafic_side_by_side(self):
        try:
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
        except Exception as ex:
            print(ex)

    def plot_grafic_times(self):
        try:

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
        except Exception as ex:
            print(ex)

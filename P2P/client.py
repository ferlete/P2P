import socket
import sys
import threading
import os
import time
import io
import matplotlib.pyplot as plt
import numpy as np
import random

from threading import Thread, Condition
from datetime import datetime, timedelta
from pydub import AudioSegment
from pydub.playback import play

from .fileIO import FileIO
from .progress import Progress
from .music import Music
from P2P.constants import *


class Client:

    def __init__(self, ip, port, filename, seeder_alive, parallel, show_statistics, show_graphic, play_audio):
        self.filename = filename
        self.seeder_alive = seeder_alive
        self.server_address = (ip, port)
        self.packet = []  # array with packet lost or received
        self.packet_received_time = []  # array with timestamp packet received
        self.packet_expected_time = []  # array with timestamp packet expected
        self.packet_reproduced_time = []  # array with timestamp packet reproduced
        self.packet_lost = []  # array with packet lost
        self.num_of_packet = 0
        self.buffer_data = []
        self.parallel = parallel
        self.play_audio = play_audio
        self.progress = Progress()
        self.show_statistics = show_statistics
        self.show_graphic = show_graphic
        self.file_io = FileIO()
        self.queue = []
        self.condition = Condition()
        self.parallel_finish = 0
        self.filename_download = ''

        try:
            # parallel donwload
            if self.parallel and len(self.seeder_alive) > 1:
                print("[+] Starting parallel download")
                # Create a UDP socket for first Seeder
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                # allow python to use recently closed socket
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                # Connect the socket to the port where the server is listening
                print('[+] Connecting to %s:%s' % self.server_address)
                s.connect(self.server_address)

                print("[+] Request filename %s" % self.filename)
                # i = 0
                request = GET_FILE_STRING + self.filename
                s.sendto(request.encode(), self.server_address)
                data, server = s.recvfrom(BUFFER_SIZE)
                s.close()

                if data[:7].decode() == EXISTS_STRING:
                    file_size = int(data[7:].decode())
                    self.num_of_packet = self.calc_number_chunk(file_size)

                    self.packet = [False] * self.num_of_packet
                    self.packet_received_time = [None] * self.num_of_packet
                    self.packet_reproduced_time = [None] * self.num_of_packet
                    self.buffer_data = [None] * self.num_of_packet

                    start = finish = 0
                    packet_by_seeder = int(self.num_of_packet / len(self.seeder_alive))
                    jobs = []
                    for host in self.seeder_alive:
                        ip, port = host.strip().split(':')
                        server_address = (str(ip), int(port))
                        # print(self.server_address)

                        # Create a UDP sockett
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                        # allow python to use recently closed socket
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                        finish = start + packet_by_seeder
                        if finish + 1 == self.num_of_packet:
                            finish += 1

                        # Connect the socket to the port where the server is listening
                        s.connect(server_address)

                        # make thread
                        thread = threading.Thread(target=self.retr_file_parallel,
                                                  args=[s, server_address, start, finish, self.filename])
                        jobs.append(thread)

                        start = finish

                    # Start the threads (i.e. parallel download)
                    for j in jobs:
                        j.start()

                    # Ensure all of the threads have finished
                    for j in jobs:
                        j.join()

                    print("[+] Download complete!")
                    # save packets and display statistics
                    self.filename_download = self.file_io.save_audio_file(self.filename, self.buffer_data)
                    if self.show_statistics:
                        self.file_io.save_log_received(self.packet_received_time, self.packet_expected_time,
                                                       self.packet_reproduced_time)
                        self.display_statistics()
                    if self.show_graphic:
                        self.plot_grafic_times()

                    if self.play_audio:
                        self.play_music(self.filename_download)

                    s.close()
                    sys.exit()

                else:
                    print("[-] File does not Exists")
                    s.close()

            # single downalod
            else:
                # Create a UDP sockett
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                # allow python to use recently closed socket
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                # Connect the socket to the port where the server is listening
                print('[+] Connecting to %s:%s' % self.server_address)
                s.connect(self.server_address)

                # create to work on a different thread
                self.i_thread = threading.Thread(target=self.retr_file, args=[s])
                self.i_thread.daemon = True
                self.i_thread.start()

                self.i_thread.join()

        except Exception as e:
            print(e)
        sys.exit()

    def retr_file_parallel(self, s, server_address, start, finish, filename):
        print('[+] Receiving from %s slice %d:%d' % (server_address, start, finish))
        try:
            request = SLICE_REQUEST + str(start) + ":" + str(finish) + ":" + filename
            s.sendto(request.encode(), server_address)
            data, addr = s.recvfrom(BUFFER_SIZE)

            while (data):
                s.settimeout(1)  # set time out
                packet_id = int(data[:5].decode())  # five bytes for header
                self.packet[packet_id] = self.simulation_layer_loss_and_delay()  # simulation delay and loss

                # check lost by timestamp
                milliseconds = int(round(time.time() * 1000))  # timestamp in ms arrival

                self.packet_received_time[packet_id] = milliseconds
                self.buffer_data[packet_id] = data[5:]

                # self.progress.printProgressBar(i, self.num_of_packet - 1, prefix='[+] Progress:',
                #                               suffix='Complete', length=60)
                data, addr = s.recvfrom(BUFFER_SIZE)

        except socket.timeout:
            s.close()

    def retr_file(self, s):
        print("[+] Request filename %s" % self.filename)
        # i = 0
        request = GET_FILE_STRING + self.filename
        s.sendto(request.encode(), self.server_address)
        data, server = s.recvfrom(BUFFER_SIZE)
        if data[:7].decode() == EXISTS_STRING:
            file_size = int(data[7:].decode())
            self.num_of_packet = self.calc_number_chunk(file_size)

            self.packet = [False] * self.num_of_packet
            self.packet_received_time = [None] * self.num_of_packet
            self.packet_expected_time = [None] * self.num_of_packet
            self.packet_reproduced_time = [None] * self.num_of_packet
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
            # expected_packet_id = 1
            # self.total_lost = 0

            milliseconds = int(round(time.time() * 1000))  # timestamp in ms arrival

            self.make_expected_sequential_time(milliseconds)

            try:
                last_time = int(round(time.time() * 1000))  # timestamp in ms arrival
                while (data):
                    s.settimeout(1)  # set time out
                    self.condition.acquire()
                    if len(self.queue) == MAX_PACKET_BUFFER:  # buffer full
                        self.condition.wait()  # Space in buffer, Consumer notified the producer
                    packet_id = int(data[:5].decode())  # five bytes for header
                    if packet_id == PACKET_ID_EOF:  # EOF
                        print("[+] File Downloaded")
                        break
                    else:
                        # check lost by packet_id only for method sequencial
                        # if expected_packet_id != packet_id:
                        #     while expected_packet_id <= packet_id:
                        #         print("[-] Lost packet_id %d" % expected_packet_id)
                        #         expected_packet_id += 1
                        #         #self.total_lost += 1
                        # else:
                        #     expected_packet_id += 1

                        self.packet[packet_id] = self.simulation_layer_loss_and_delay()  # simulation delay and loss

                        milliseconds = int(round(time.time() * 1000))  # timestamp in ms arrival
                        # check lost by timestamp
                        # diff = (milliseconds - last_time)

                        # time most RTT, display warning
                        # if diff > 40:
                        #     print("[-] Delay %d ms packet_id %d" %(diff, packet_id))
                        # last_time = milliseconds

                        self.packet_received_time[packet_id] = milliseconds
                        self.buffer_data[packet_id] = data[5:]

                        # self.progress.printProgressBar(i, self.num_of_packet - 1, prefix='[+] Progress:',
                        #                               suffix='Complete', length=60)

                        # queue packet audio for play
                        self.queue.append(packet_id)
                        self.condition.notify()
                        self.condition.release()
                        # time.sleep(random.random())

                        data, addr = s.recvfrom(BUFFER_SIZE)

            except socket.timeout:
                s.close()
                print("[-] Socket Time out, Seeder stopped sending or lost EOF")

            # save packets and display statistics
            self.filename_download = self.file_io.save_audio_file(self.filename, self.buffer_data)
            if self.show_statistics:
                self.file_io.save_log_received(self.packet_received_time, self.packet_expected_time,
                                               self.packet_reproduced_time)
                self.display_statistics()

            if self.show_graphic:
                self.plot_grafic_times()

            if self.play_audio:
                self.play_music(self.filename_download)

            s.close()
            sys.exit()
        else:
            print("[-] File does not Exists")
            s.close()

    def make_expected_sequential_time(self, initial_time):
        for i in range(len(self.packet_expected_time)):
            self.packet_expected_time[i] = initial_time
            initial_time = int(round(initial_time + DELAY_FOR_TO_RECEIVE * 1000))

    """
        Esta funcao deve retornar um booleano indicando se pacote chegou o foi perdido e aplicar delay
    """

    def simulation_layer_loss_and_delay(self):
        time.sleep(DELAY_FOR_TO_RECEIVE)  # Give receiver a bit time to received packet
        return True

    """
        calculate the number of chunks to be created
    """

    def calc_number_chunk(self, bytes):
        noOfChunks = int(bytes) / BLOCK_SIZE
        if (bytes % BLOCK_SIZE):
            noOfChunks += 1
        return int(noOfChunks)

    def play_music(self, filename):

        seg = AudioSegment.from_file(filename, format="mp3")
        print("[+] Audio Information")
        print("[+] Channels:", seg.channels)
        print("[+] Bits per sample:", seg.sample_width * 8)
        print("[+] Sampling frequency:", seg.frame_rate)
        print("[+] Length:", seg.duration_seconds, "seconds")
        play(seg)  # play audio

    def play_music_on_download(self):
        try:
            while True:
                self.condition.acquire()
                if not self.queue:  # Buffer empty
                    self.condition.wait()  # Producer added something to queue and notified the consumer
                num = self.queue.pop(0)
                milliseconds = int(round(time.time() * 1000))  # timestamp in ms reproduced
                self.packet_reproduced_time[num] = milliseconds
                # print("[-] Play packet %d" % num)
                self.condition.notify()
                self.condition.release()
                # time.sleep(random.random())

        except Exception as ex:
            print(ex)
            sys.exit()

    """
        show statistic at the end of the audio file transmission
    """

    def display_statistics(self):
        try:
            print(30 * "-" + "Statistics" + 30 * "-")
            print("Total of packet %d" % self.num_of_packet)
            # using enumerate() + list comprehension to return true indices.
            res = [i for i, val in enumerate(self.packet) if val]
            print("Num Packet received: %d" % len(res))
            lost = self.num_of_packet - len(res)
            print("Num Packet lost %d" % lost)
            print(70 * "-")

            # update array with lost packets
            for i in range(len(self.packet)):
                if not self.packet[i]:
                    self.packet_lost.append(i)


        except Exception as ex:
            print(ex)

    """
        plot graphic with time send, receive and play
    """

    def plot_grafic_times(self):
        try:

            x, y, z, w = np.loadtxt('time.log', comments='#', delimiter=':', unpack=True)

            plt.plot(x, y, label='transmitted', linewidth=1.0)
            # when the packet is lost it is marked as x in the graph
            plt.plot(x, z, '-rx', label='Received', linewidth=0.5, markevery=self.packet_lost)
            plt.plot(x, w, label='reproduced', linewidth=1.0)
            plt.xlabel('Time')
            plt.ylabel('Packet')
            plt.title('Tradeoff')
            plt.legend()
            plt.show()
        except Exception as ex:
            print(ex)

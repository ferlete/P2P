import socket
import sys
import threading
import os
import time
import io
import numpy as np


from pydub import AudioSegment
from pydub.playback import play

from .fileIO import FileIO
from .music import Music
from P2P.constants import *


class Client:


    def __init__(self, ip, port, filename):
        self.filename = filename
        self.server_address = (ip, port)
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
        current_packet = 0
        print("[+] Resquest filename %s" % self.filename)
        request = GET_FILE_STRING + self.filename
        self.socket.sendto(request.encode(), self.server_address)
        data, server = self.socket.recvfrom(BUFFER_SIZE)
        #print(data.decode())
        if data[:7].decode() == EXISTS_STRING:
            file_size = int(data[7:].decode())
            num_of_packet = int(self.calc_number_chunk(file_size))
            request = DOWNLOAD_STRING + self.filename
            self.socket.sendto(request.encode(), self.server_address)
            new_filename = "new_" + self.filename
            f = open(new_filename, 'wb')
            data, addr = self.socket.recvfrom(BUFFER_SIZE)
            #print("[+] Received packet %d from seeder %s" % (int(data[:5].decode()), addr))
            print("[+] Receiving filename %s from % s" % (self.filename, addr))
            self.buffer_data = data # buffer for play

            # create to work on a different thread for play audio on download
            t = threading.Timer(1.0, self.play_music_on_download, args=[new_filename])
            t.start()

            try:
                while(data):
                    if current_packet != int(data[:5].decode()):
                        print("[-] Packet %d out of order" % int(current_packet))
                        sys.exit()
                    f.write(data[5:])
                    self.socket.settimeout(2)
                    data, addr = self.socket.recvfrom(BUFFER_SIZE)
                    self.buffer_data += data[5:]
                    current_packet += 1
                    #print("[+] Received packet %d from seeder %s" % (int(data[:5].decode()), addr))

            except socket.timeout:
                f.close
                self.socket.close()
                print("[+] File Downloaded")
        else:
            print("[-] File does not Exists")
            self.socket.close()

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

    def _play(self, segment):
        play(segment)

    """
        calculate the number of chunks to be created
    """
    def calc_number_chunk(self, bytes):
        noOfChunks = int(bytes) / BLOCK_SIZE
        if (bytes % BLOCK_SIZE):
            noOfChunks += 1
        return noOfChunks
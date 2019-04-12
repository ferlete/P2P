import socket
import sys
import threading
import os
import time

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
            print('[+] connecting to %s:%s' % self.server_address)
            self.socket.connect(self.server_address)

            # create to work on a different thread
            i_thread = threading.Thread(target=self.retr_file)
            i_thread.daemon = False
            i_thread.start()

        except Exception as e:
            print(e)
        sys.exit()

    def retr_file(self):
        print("[+] resquest filename %s" % self.filename)
        request = GET_FILE_STRING + self.filename
        self.socket.sendto(request.encode(), self.server_address)
        data, server = self.socket.recvfrom(BUFFER_SIZE)
        #print(data.decode())
        if data[:7].decode() == EXISTS_STRING:
            file_size = int(data[7:].decode())
            num_of_packet = int(self.calc_number_chunk(file_size))
            request = DOWNLOAD_STRING + self.filename
            self.socket.sendto(request.encode(), self.server_address)
            f = open("new_" + self.filename, 'wb')
            data, addr = self.socket.recvfrom(BUFFER_SIZE)
            print("[+] received packet %d from %s" % (int(data[:5].decode()), addr))

            # create to work on a different thread to play music
            i_thread = threading.Thread(target=self.play_music_on_download, args=f)
            i_thread.daemon = False
            i_thread.start()


            try:
                while(data):
                    f.write(data[5:])
                    self.socket.settimeout(2)
                    data, addr = self.socket.recvfrom(BUFFER_SIZE)
                    #print("received message: %s" % data)
                    print("[+] received packet %d from %s" % (int(data[:5].decode()), addr))
            except socket.timeout:
                f.close
                self.socket.close()
                print("[+] File Downloaded")
        else:
            print("[-] File does not Exists")
            self.socket.close()

    def play_music_on_download(self, filename):
        print("sleep Play")
        time.sleep(1) # sleep 5 seconds
        print("Play................")
        music = Music()
        music.play_audio_segment(filename)

    """
        calculate the number of chunks to be created
    """
    def calc_number_chunk(self, bytes):
        noOfChunks = int(bytes) / BLOCK_SIZE
        if (bytes % BLOCK_SIZE):
            noOfChunks += 1
        return noOfChunks
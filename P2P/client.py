import socket
import sys
import threading
import os
import time

from .fileIO import FileIO
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
        try:
            print("[+] resquest filename %s" % self.filename)
            request = GET_FILE_STRING + self.filename
            self.socket.sendto(request.encode(), self.server_address)
            data, server = self.socket.recvfrom(BUFFER_SIZE)
            print(data.decode())
            if data[:7].decode() == EXISTS_STRING:
                file_size = int(data[7:].decode())
                num_of_packet = int(self.calc_number_chunk(file_size))

                request = DOWNLOAD_STRING + self.filename
                self.socket.sendto(request.encode(), self.server_address)

                while True:
                    data, addr = self.socket.recvfrom(BUFFER_SIZE)
                    print("received message: %s" % data)

                #cwd = os.getcwd()
                #path_to_newfile = cwd + "/music/slice_" + str(self.slice) + "_" + self.filename.strip()

                #socket.sendto(("SLICE"+str(self.slice)).encode())
                #data = socket.recv(self.BUFFER_SIZE)
                #print(data)

                #slicesize = int(data[3:])
                #print("slicesize: %d" % slicesize)
                # if slicesize == 0:
                #     print("[-] slice not found in server")
                #     data = socket.recv(self.BUFFER_SIZE)
                # else:
                #     f = open(path_to_newfile, 'wb')
                #     data = socket.recv(self.BUFFER_SIZE)
                #     totalRecv = len(data)
                #     f.write(data)
                #     while totalRecv < slicesize:
                #         data = socket.recv(self.BUFFER_SIZE)
                #         totalRecv += len(data)
                #         f.write(data)
                #         #print("{0:.2f}".format((totalRecv/float(slicesize))*100)+"% Done")
                #     print("[+] Download Complete!")
            else:
                print("[-] File does not Exists")
            self.socket.close()

        except KeyboardInterrupt as e:
            # If a user turns the server off due to KeyboardInterrupt
            socket.close()
            return

    """
        calculate the number of chunks to be created
    """
    def calc_number_chunk(self, bytes):
        noOfChunks = int(bytes) / BLOCK_SIZE
        if (bytes % BLOCK_SIZE):
            noOfChunks += 1
        return noOfChunks
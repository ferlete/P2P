import os, sys
from array import array
import binascii
import csv

from P2P.constants import *


class FileIO:

    def __init__(self):
        pass

    def slice_exists(self, filename, slice):
        if self.file_exists(filename):
            sizefile = self.get_file_size(filename)
            num_chunk = self.calc_number_chunk(sizefile)
            if slice > num_chunk:
                return False
            else:
                return True
        else:
            return False

    def get_file(self, filename):
        with open(self.get_path(filename), 'rb') as f:
            data = f.read()
        f.close()
        return data
    
    def get_file_array(self, filename):
        c = []
        with open(self.get_path(filename), 'rb') as f:            
            while True:
                # Read block size chunks of the music
                chunk = f.read(BLOCK_SIZE)
                c.append(chunk)
                if not chunk: break
        f.close()

        return c

    def get_num_packet(self, filename):
        sizefile = self.get_file_size(filename)
        return int(self.calc_number_chunk(sizefile))

    def file_exists_path(self, filename):
        if os.path.isfile(filename):
            return True
        else:
            return False

    def file_exists(self, filename):
        cwd = os.getcwd()
        path_to_file = cwd + MUSIC_FOLDER + filename

        if os.path.isfile(path_to_file):
            return True
        else:
            return False

    def get_path(self, filename):
        cwd = os.getcwd()
        return cwd + MUSIC_FOLDER + filename

    def get_file_size(self, filename):
        return os.path.getsize(self.get_path(filename))

    """
        calculate the number of chunks to be created
    """
    def calc_number_chunk(self, bytes):
        noOfChunks = int(bytes) / BLOCK_SIZE
        if (bytes % BLOCK_SIZE):
            noOfChunks += 1
        return noOfChunks

    """
         save log time send packets
     """
    def save_log_send(self, packet_send_time):
        try:
            f_send = open(FILENAME_LOG, 'w')
            for i in range(len(packet_send_time)):
                f_send.write(str(i) + ':' + str(packet_send_time[i]) + '\n')
            f_send.close()
        except Exception(ex):
            print(ex)
    """
         save log time received packets
     """
    def save_log_received(self, packet_received_time):

        if self.file_exists_path(FILENAME_LOG):
            f_received = open(FILENAME_LOG, 'r')
            data = [item for item in csv.reader(f_received, delimiter=':')]
            f_received.close()
            new_data = []
            for i, item in enumerate(data):
                if packet_received_time[int(i)] == None:
                    item.append(0)
                else:
                    item.append(packet_received_time[int(i)])
                new_data.append(item)
            f = open(FILENAME_LOG, 'w')
            csv.writer(f, delimiter=':').writerows(new_data)
            f.close()
        else:
            print("File %s not found!" % FILENAME_LOG)

    """
         save audio file
    """
    def save_audio_file(self, filename, buffer_data):
        try:
            new_filename = CURRENT_DIR + MUSIC_FOLDER + "new_" + filename
            f = open(new_filename, 'wb')
            for i in range(len(buffer_data)):
                if buffer_data[i] != None:
                    f.write(buffer_data[i])  # save in disk packet bytes
                #else:
                #    print("lost packet %d" %i)
            f.close()
        except Exception as ex:
            print(ex)


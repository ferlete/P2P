import os, sys
from array import array
import binascii
import csv

from P2P.constants import *


class FileIO:

    def __init__(self):
        pass

    def get_file(self, filename):
        """
             get file

            this function reads a file in binary mode and returns the contents

            Parameters
            ----------
                filename : str
                    filename

            Returns
            -------
            binary
                binary data

        """
        with open(self.get_path(filename), 'rb') as f:
            data = f.read()
        f.close()
        return data

    def get_file_array(self, filename):
        """
             reads file

            this function reads a file and returns an array with blocks of 320 bytes

            Parameters
            ----------
                filename : str
                    filename

            Returns
            -------
            bytearray
                an array with file content

        """

        c = []
        with open(self.get_path(filename), 'rb') as f:
            while True:
                # Read block size chunks of the music
                chunk = f.read(BLOCK_SIZE)
                c.append(chunk)
                if not chunk: break
        f.close()

        return c

    def file_exists_path(self, filename):
        """
             check if path exists

            this function check if path exists

            Parameters
            ----------
                filename : str
                    filename

            Returns
            -------
            bool
                true or false

        """

        if os.path.isfile(filename):
            return True
        else:
            return False

    def file_exists(self, filename):
        """
            check if file exists

            this function checks if file exists on disk

            Parameters
            ----------
                filename : str
                    filename

            Returns
            -------
                bool
                    true when file exists and false when file does not exist

        """
        cwd = os.getcwd()
        path_to_file = cwd + MUSIC_FOLDER + filename

        if os.path.isfile(path_to_file):
            return True
        else:
            return False

    def get_path(self, filename):
        """
            get path file.

            function that searches the number of bytes the file has.

            Parameters
            ----------
            filename : str
                file name

            Returns
            -------
            int
                Number of bytes of file

            """
        cwd = os.getcwd()
        return cwd + MUSIC_FOLDER + filename

    def get_file_size(self, filename):
        """
            get file size.

            function that searches the number of bytes the file has.

            Parameters
            ----------
            filename : str
                file name

            Returns
            -------
            int
                Number of bytes of file

        """
        return os.path.getsize(self.get_path(filename))

    def calc_number_chunk(self, bytes):
        """
            calculate the number of chunks to be created

            this function calculates the number of blocks that will be sent from the server to the client

            Parameters
            ----------
            bytes : int
                number of bytes

            Returns
            -------
            int
                Number of chuncks

        """
        noOfChunks = int(bytes) / BLOCK_SIZE
        if (bytes % BLOCK_SIZE):
            noOfChunks += 1
        return noOfChunks

    def get_real_lost(self):
        pass

    def save_log_time(self, packet_send_time, packet_received_time, packet_reproduced_time):
        """
            save log time send packets to disk

            this function saves in file the times of sending, receiving and reproduction of packages received by the client

            Parameters
            ----------
            packet_send_time : int
                package output timestamp
            packet_received_time : int
                package arrival timestamp
            packet_reproduced_time : int
                playback timestamp

            Returns
            -------
            int
                real lost UDP

        """
        try:
            real_lost = 0
            f = open(FILENAME_TIME, 'w')
            f2 = open(FILENAME_REAL_LOST, 'w')
            for i in range(len(packet_send_time)):
                if packet_send_time[i] != None:
                    #print(str(packet_reproduced_time[i]) + "\n")
                    if packet_reproduced_time[i] == None:
                        packet_reproduced_time[i] = packet_reproduced_time[i-1]
                    f.write(str(i) + ':' + str(packet_send_time[i]) + ':' + str(packet_received_time[i]) + ':' + str(
                        packet_reproduced_time[i]) + '\n')
                else:
                    f2.write(str(i))
                    real_lost += 1

            f.close()
            f2.close()

            return real_lost

        except Exception as ex:
            print(ex)

    def save_audio_file(self, filename, buffer_data):
        """
            save audio file to disk

            this function writes to disk the bits of the audio file

            Parameters
            ----------
                filename : str
                    file name
                buffer_data: array
                    buffer data audio

            Returns
            -------
                str
                    new file name saved

        """
        try:
            new_filename = CURRENT_DIR + MUSIC_FOLDER + "new_" + filename
            f = open(new_filename, 'wb')
            for i in range(len(buffer_data)):
                if buffer_data[i] != None:
                    f.write(buffer_data[i])  # save in disk packet bytes
            f.close()
        except Exception as ex:
            print(ex)

        return new_filename

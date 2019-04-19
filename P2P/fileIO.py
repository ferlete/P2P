import os, sys
from array import array

from P2P.constants import *

class FileIO:

    def __init__(self, music_folder, block_size):
        self.music_folder = music_folder
        self.block_size = block_size

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
        data = array('B')

        with open(self.get_path(filename), 'rb') as f:
            data.fromfile(f, self.get_file_size(filename))

        examples = [data[s:s + self.block_size] for s in range(0, self.get_file_size(filename), self.block_size)]

        return examples


    def get_num_packet(self, filename):
        sizefile = self.get_file_size(filename)
        return self.calc_number_chunk(sizefile)

    def get_slice_file(self, filename, slice):
        # TODO bug correction
        sizefile = self.get_file_size(filename)
        #num_chunk = self.calc_number_chunk(sizefile)
        pos = (slice * self.block_size)
        with open(self.get_path(filename), 'rb') as f:
            f.seek(pos, 0)
            data = f.read(self.block_size)
        f.close()
        return data

    def file_exists(self, filename):
        cwd = os.getcwd()
        path_to_file = cwd + self.music_folder + filename

        if os.path.isfile(path_to_file):
            return True
        else:
            return False

    def get_path(self, filename):
        cwd = os.getcwd()
        return cwd + self.music_folder + filename

    def get_file_size(self, filename):
        return os.path.getsize(self.get_path(filename))

    """
        calculate the number of chunks to be created
    """
    def calc_number_chunk(self, bytes):
        noOfChunks = int(bytes) / self.block_size
        if (bytes % self.block_size):
            noOfChunks += 1
        return noOfChunks

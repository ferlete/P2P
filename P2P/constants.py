"""
    This file is the constants of the peer to peer network
"""
import os

byte = 1
kilobyte = byte * 1024
megabyte = kilobyte * 1024
BLOCK_SIZE = int(320 * byte)  # file block size in bytes

CURRENT_DIR = os.getcwd()
MUSIC_FOLDER = "/music/"
GET_FILE_STRING = "GET FILE:"
DOWNLOAD_STRING = "DOWNLOAD FILE:"
EXISTS_STRING = 'EXISTS:'
NOT_FOUND_STRING = 'FILE NOT FOUND'
REQUEST_SLICE = "SLICE:"
BUFFER_SIZE = 1024
SEQUENCIAL_POLICY = 'sequential'
RANDON_POLICY = 'randon'
DELAY_FOR_SEND = 0.001
DELAY_FOR_TO_RECEIVE = 0.001

LEN_HEADER = 5 # Len header packet in bytes




"""
    This file is the constants of the peer to peer network
"""
import os

# len
byte = 1
kilobyte = byte * 1024
megabyte = kilobyte * 1024
BLOCK_SIZE = int(320 * byte)  # file block size in bytes
MAX_PACKET_BUFFER = 1000  # 320.000 bytes 320Kb
LEN_HEADER = 20  # 20 bytes to Len header
BUFFER_SIZE = BLOCK_SIZE + LEN_HEADER

# files
CURRENT_DIR = os.getcwd()
FILENAME_TIME = CURRENT_DIR + "/log/time.log"
FILENAME_REAL_LOST = CURRENT_DIR + "/log/real_lost.log"
FILENAME_SEEDER = CURRENT_DIR + "/list_seeder.txt"
MUSIC_FOLDER = "/music/"

# Responses
PONG_RESPONSE = "PONG"
EXISTS_RESPONSE = 'EXISTS:'
NOT_FOUND_RESPONSE = 'FILE NOT FOUND'

# Requests
GET_FILE_REQUEST = "GET FILE:"
SLICE_REQUEST = "SLICE:"
PING_REQUEST = "PING"
POLICY_REQUEST = "POLICY"
KILL_REQUEST = "KILL"

# Policy Support
SEQUENCIAL_POLICY = 'sequential'
RANDOM_POLICY = 'random'
SEMI_RANDOM_POLICY = 'semi-random'

# Delay Time
DELAY_FOR_SEND = 0.02  # 20 milliseconds
DELAY_FOR_TO_RECEIVE = 0.001
TIMEOUT_CONNECT = 0.1





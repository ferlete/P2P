import sys
import time
import os
import threading
import pyaudio
from pydub import AudioSegment
from pydub.utils import make_chunks

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

sound = AudioSegment.from_file(sys.argv[1])
player = pyaudio.PyAudio()


stream = player.open(format=player.get_format_from_width(sound.sample_width),
                     channels=sound.channels,
                     rate=sound.frame_rate,
                     output=True)

# PLAYBACK LOOP
loop = True
start = 0
length = sound.duration_seconds
volume = 100.0
playchunk = sound[start * 1000.0:(start + length) * 1000.0] - (60 - (60 * (volume / 100.0)))
millisecondchunk = 50 / 1000.0

while loop:
    timems = start
    for chunks in make_chunks(playchunk, millisecondchunk * 1000):
        print(playchunk)
        #time.sleep(0.5)
        timems += millisecondchunk
        stream.write(chunks._data)
        #print(len(chunks._data))
        if not loop:
            break
        if timems >= start + length:
            break

stream.close()
player.terminate()
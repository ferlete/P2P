"""
    This file deals with uploading music
    It also converts the mp3 file into bit stream
"""
from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import mediainfo
import os
import io


class Music:

    sound = None
    converted_sound = None

    cwd = os.getcwd()
    #song_path = cwd+"/music/song.mp3"
    song_path = cwd + "/new_song.mp3"

    def play_audio_segment(self):
        sound = AudioSegment.from_mp3(self.song_path)
        play(sound)

    def convert(self):
        sound = AudioSegment.from_mp3(self.song_path)

        # get the raw data
        raw_data = sound._data

        return raw_data

    def convert_to_music(self, bytes):
        song = AudioSegment.from_file(io.BytesIO(bytes), format="mp3")
        output = io.StringIO()
        song.export(output, format="mp3", bitrate="192k")
        converted_sound = AudioSegment.from_mp3(cwd + "/music/copy.mp3")
        play(converted_sound)
        print("Done")

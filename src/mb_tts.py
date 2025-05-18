from tiktok_voice import tts, Voice

class MB_TTS():
    def __init__(self, dest = "./tmp", voice = Voice.PIRATE, play_sound = True):
        self.dest = dest
        self.voice = voice
        self.play_sound = play_sound

    def speak(self, text):
    # arguments:
    #   - input text
    #   - voice which is used for the audio
    #   - output file name
    #   - play sound after generating the audio
        tts(text, self.voice, self.dest, play_sound=self.play_sound)
from mb_tts import MB_TTS

tts = MB_TTS("./mb_tts_test.mp3")

# text = """
# This is a test
# """
# tts.speak(text.replace("\n", " ").replace("\t", "").strip(), speaking_speed=1.5)

text = """
Did he just say the word?
Kai had enough of him.
He loves her so much.
Couldn't get better!
"""
tts.speak(text, speaking_speed=1, lang="en")
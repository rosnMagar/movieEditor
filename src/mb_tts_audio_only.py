from mb_tts import MB_TTS

tts = MB_TTS("./audio_only_tts.mp3")

script = input("Enter your script: ")
tts.speak(script, speaking_speed=1.5)
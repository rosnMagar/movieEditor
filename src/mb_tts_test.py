from mb_tts import MB_TTS

tts = MB_TTS("./mb_tts_test.mp3")

text = """
   In the ancient land of Eldoria, where the skies were painted with shades of mystic hues 
and the forests whispered secrets of old, there existed a dragon named Zephyros. Unlike the 
fearsome tales of dragons that plagued human hearts with terror, 
Zephyros was a creature of wonder and wisdom, revered by all who knew of his existence. 
"""
tts.speak(text.replace("\n", " ").replace("\t", "").strip(), speaking_speed=1.5)

# text = """
# おはようございます。今日はかっこいいですね。いい天気なので、遊びに行きたいです
# """
# tts.speak(text, speaking_speed=1.5)
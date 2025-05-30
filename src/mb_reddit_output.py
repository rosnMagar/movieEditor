from mb_stage_assets import MBStageAssets
import mb_subtitles
from moviepy import *
from moviepy.video.tools.subtitles import SubtitlesClip
from mb_minecraft_subclip import MBMineCraftSubClip
import os

clips = []
url = input("Enter Reddit URL: ")
sample_text = input("Enter your script: ")
if url == "":
    stager = MBStageAssets(['cats'], f"./tmp/clip_test", text=sample_text)
else:
    stager = MBStageAssets(['cats'], f"./tmp/clip_test", text=sample_text, reddit_url=url)

clips.append(VideoFileClip(stager.create_minecraft_clip()))

video = concatenate_videoclips(clips) 
video.resized((1080,1920))

video.write_videofile(f"./output/minecraft_reddit.mp4")
video.audio.write_audiofile(f"./output/minecraft_reddit.mp3")


subtitles = mb_subtitles.generate_word_level_subtitles_assemblyai(f"./output/minecraft_reddit.mp3")
with open("subtitles.srt", "w") as f:
    f.write(subtitles)

generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                                font_size=69,
                                color='white', stroke_width=2, 
                                text_align="center",
                                stroke_color="black", method="caption", size=(int(video.w * 0.8), 80))

subtitles = SubtitlesClip("subtitles.srt", make_textclip=generator, encoding='utf-8')

res = CompositeVideoClip([VideoFileClip(f"./output/minecraft_reddit.mp4"),
                          subtitles.with_position(("center", "center"))])

res.write_videofile(
    "./output/minecraft_reddit_final.mp4"
)

# Close clips
video.close()
res.close()


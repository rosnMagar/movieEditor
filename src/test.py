from mb_stage_assets import MBStageAssets
import mb_subtitles
from tiktok_voice import Voice
from moviepy import *
from moviepy.video.tools.subtitles import SubtitlesClip
import os

clips = []
stager = MBStageAssets(['dogs'], f"./tmp/clip_test", text="Dogs are human's best companions.")
clips.append(VideoFileClip(stager.create_clip()))

stager = MBStageAssets(['cats'], f"./tmp/clip_test", text="Cats are not!!!!!!!!!", voice=Voice.MALE_DEADPOOL)
clips.append(VideoFileClip(stager.create_clip()))

video = concatenate_videoclips(clips) 
video.write_videofile(f"./output/test.mp4")
video.audio.write_audiofile(f"./output/test.mp3")


subtitles = mb_subtitles.generate_subtitles_assemblyai(f"./output/test.mp3")
with open("subtitles.srt", "w") as f:
    f.write(subtitles)

# print(os.path.abspath())

generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                                font_size=24, color='white', stroke_width=3, 
                                stroke_color="black", method="caption", size=(int(video.w * 0.8), None))

subtitles = SubtitlesClip("subtitles.srt", make_textclip=generator, encoding='utf-8')

res = CompositeVideoClip([VideoFileClip(f"./output/test.mp4"),
                          subtitles.with_position(("center", "center"))])

res.write_videofile(
    "./output/video_with_subs.mp4"
)

# Close clips
video.close()
res.close()


import mb_subtitles
from moviepy import TextClip, CompositeVideoClip, VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
import uuid

OUT_FOLDER = "./output"
video_dir = input("Enter the video directory: ")

subtitles = mb_subtitles.generate_word_level_subtitles_assemblyai(video_dir)
generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                            font_size=80,
                            color='white', stroke_width=5, 
                            text_align="center",
                            stroke_color="black", method="caption", size=(int(1080 * 0.8), 100))
with open("subtitles.srt", "w") as f:
    f.write(subtitles)

subtitles = SubtitlesClip("subtitles.srt", make_textclip=generator, encoding='utf-8')

file_name = f"{uuid.uuid4()}_with_sub.mp4"
res = CompositeVideoClip([VideoFileClip(video_dir),
                            subtitles.with_position(("center", "center"))])
res.write_videofile(f"{OUT_FOLDER}/{uuid.uuid4()}_with_sub.mp4")

res.close()


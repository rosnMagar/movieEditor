import mb_subtitles
from moviepy import ColorClip, ImageClip, TextClip, CompositeVideoClip, VideoFileClip, concatenate_videoclips
from moviepy.video.tools.subtitles import SubtitlesClip
import uuid

OUT_FOLDER = "./output"
video_dir = input("Enter the video directory: ")
font_size = int(input("Enter Font size(80 default): "))
sub_height = float(input("Enter how hight the subtitles are needed to be(center Default): "))

subtitles = mb_subtitles.generate_word_level_subtitles_assemblyai(video_dir)
generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                            font_size=font_size,
                            color='white', stroke_width=10, 
                            text_align="center",
                            stroke_color="black", method="caption", 
                            size=((1080, 200)), 
                            )
with open("subtitles.srt", "w") as f:
    f.write(subtitles)

try:
    subtitles = SubtitlesClip("subtitles.srt", make_textclip=generator, encoding='utf-8')

    file_name = f"{uuid.uuid4()}_with_sub.mp4"
    image = ColorClip(color=(0,0,0), size=(1080,1920)).with_duration(1)
    video_file = VideoFileClip(video_dir)
    video_file = video_file.resized((1080, 1920))
    video_file = concatenate_videoclips([video_file, image])
    res = CompositeVideoClip([video_file,
                            subtitles.with_position(("center", "center" if int(sub_height * 1920) == 0 else int(sub_height * 1920)))])
    res.write_videofile(file_name, fps=60)

    res.close()
except Exception as e:
    print('No sub detected: ', e)



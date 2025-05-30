import google.generativeai as genai
from moviepy import *
import os
from dotenv import load_dotenv
import json
from regex import W
from termcolor import colored

from mb_stage_assets import MBStageAssets
import mb_util
import mb_subtitles 
import uuid

from moviepy.video.tools.subtitles import SubtitlesClip

load_dotenv()

OUT_FOLDER = "./output"
TMP_FOLDER = "./tmp"
FONT = "LilitaOne-Regular.ttf"

try:
    os.mkdir(OUT_FOLDER)
except:
    print("Output Folder Exists")

sub_mode = int(input("""
1. Press 1 for single word sub
2. Press 2 for general sub
"""))

print(colored(f"You selected: {sub_mode}", "green"))

input_mode = int(input("""
1. Press 1 for user defined script
2. Press 2 for AI Script(Gemini)
"""))

print(colored(f"You Selected: {input_mode}", "green"))

output = []

for i in range(0, 5):
    output[i] = input("Enter your {i} rank title: ")
bg_dir = input("Enter the folder directory for background videos: ")
print(colored("Should be numbered 1-5", "blue"))

output_video_name = uuid.uuid4() 

video.write_videofile(f"{OUT_FOLDER}/final_no_sub{output_video_name}_video.mp4")
video.audio.write_audiofile(f"{OUT_FOLDER}/final_no_sub_{output_video_name}_video.mp3")
# subtitles
if sub_mode == 1:
    subtitles = mb_subtitles.generate_word_level_subtitles_assemblyai(f"{OUT_FOLDER}/final_no_sub_{output_video_name}_video.mp3")
    generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                                font_size=69,
                                color='white', stroke_width=2, 
                                text_align="center",
                                stroke_color="black", method="caption", size=(int(video.w * 0.8), 80))
    with open("subtitles.srt", "w") as f:
        f.write(subtitles)
elif sub_mode==2:
    subtitles = mb_subtitles.generate_subtitles_assemblyai(f"{OUT_FOLDER}/final_no_sub_{output_video_name}_video.mp3")

    generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                                font_size=52,
                                color='white', stroke_width=2, 
                                text_align="center",
                                bg_color="#6496d9",
                                stroke_color="black", method="caption", size=(int(video.w * 0.8), None))
 
    with open("subtitles.srt", "w") as f:
        f.write(subtitles)

subtitles = SubtitlesClip("subtitles.srt", make_textclip=generator, encoding='utf-8')

if sub_mode == 1:
    res = CompositeVideoClip([VideoFileClip(f"{OUT_FOLDER}/final_no_sub{output_video_name}_video.mp4"),
                            subtitles.with_position(("center", "center"))])
if sub_mode == 2:
    res = CompositeVideoClip([VideoFileClip(f"{OUT_FOLDER}/final_no_sub{output_video_name}_video.mp4"),
                            subtitles.with_position(("center", video.h * (1 - 0.3)))])

res.write_videofile(f"{OUT_FOLDER}/final_{output_video_name}_video.mp4")

video.close()
res.close()

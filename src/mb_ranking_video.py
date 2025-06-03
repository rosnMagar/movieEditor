import traceback
from turtle import position
from Cython import nonecheck
from moviepy import *
from moviepy.video.tools.subtitles import SubtitlesClip
import uuid
import os
from dotenv import load_dotenv
from termcolor import colored

import mb_subtitles


load_dotenv()

OUT_FOLDER = "./output"
TMP_FOLDER = "./tmp"
FONT = "LilitaOne-Regular.ttf"

try:
    os.mkdir(OUT_FOLDER)
except:
    print("Output Folder Exists")

output = []

bg_dir = input("Enter the folder directory for background videos: ")
print(colored("Should be numbered 1-7", "blue"))


try:
    entries = os.listdir(bg_dir)
    clip_data = [] 
    clips_index = 0

    def get_rank_text(text, width, height, start, duration):
        return (TextClip(text = text, font="./LilitaOne-Regular.ttf",
                        font_size=64,
                        color="white",
                        stroke_width=2,
                        text_align="left",
                        stroke_color="black",
                        method="label",
                        size=(int(width), int(height * 0.7)))
                        .with_position((2, 2))
                        .with_start(start)
                        .with_duration(duration))

    with os.scandir(bg_dir) as entries:
        for entry in reversed(list(entries)):
            if entry.is_file():
                print(colored(f"File Found: {entry.path}", 'green'))
                try:

                    # Attempt to load as a video clip
                    print(colored("Filename should match title rank 1-5", "blue"))
                    title = input("Enter your title for this video: ")

                    out_filename = f"{TMP_FOLDER}/tmp_rank_{clips_index}.mp4"

                    clip_data.append({
                        "id": clips_index,
                        "src_file": entry.path,
                        "file_name": out_filename,
                        "text": title
                    })
                    clips_index += 1

                    # clip.close()

                except Exception as e:
                    # If it's not a valid video file, VideoFileClip will raise an error
                    print(colored(f"Could not load {entry.name} as a video clip: {e}. Skipping.", "yellow"))
                    print(traceback.format_exc())
    
    # exporting individual clips

    # adding space between all initial numbers
    clip_space_delta = 50
    burn_texts = []
   
    for j, clip in enumerate(clip_data):

        src_clip = VideoFileClip(clip['src_file'])
        src_clip = src_clip.resized((1080, 1920))
        number_texts = []

        for i in range(0, len(clip_data)):
            if i == 0:
                color="#f3b610"
            elif i == 1:
                color = "#9e9e9e"
            elif i == 2:
                color="#be6029"
            else:
                color="#ffffff"
            number_texts.append(TextClip(text = f"{i+1}.", font="./LilitaOne-Regular.ttf",
                                font_size=100,
                                color=color,
                                stroke_width=2,
                                text_align="left",
                                stroke_color="black",
                                method="label",
                                size=((None, None))
                                )
                                .with_position((50, (clip_space_delta * 3 * i) + 400))
                                .with_duration(src_clip.duration))

        for i, burn_text in enumerate(burn_texts):
            burn_texts[i] = burn_text.with_duration(src_clip.duration)
    
        burn_texts.append(TextClip(text = " " + clip['text'] + " ", font="./LilitaOne-Regular.ttf",
                            font_size=50,
                            color="white",
                            stroke_width=2,
                            text_align="left",
                            stroke_color="black",
                            method="label",
                            size=((None, 75))
                            )
                            .with_position((150, ((len(clip_data) - j - 1) * clip_space_delta * 3) + 410))
                            .with_duration(src_clip.duration))

        composite_input = [src_clip]
        composite_input.extend(number_texts)
        composite_input.extend(burn_texts)
        final_clip = CompositeVideoClip(composite_input)
        final_clip.write_videofile(
            clip['file_name'],
            threads=os.cpu_count(), # Use all available CPU cores
        )

    if not clip_data:
        print(colored(f"No valid video files found or loaded from directory: {bg_dir}", "red"))

    print(colored(f"Successfully loaded {len(clip_data)} video clip(s).", "blue"))

    # after videos are loaded:
    output_video_name = uuid.uuid4() 

    videos = []
    for clip in clip_data:
        videos.append(VideoFileClip(clip['file_name']))

    joined_clip = concatenate_videoclips(videos)
    final_clip = joined_clip.resized((1080, 1920))
    joined_clip.write_videofile(
        f"{OUT_FOLDER}/{output_video_name}_ranked_videos.mp4",
        threads=os.cpu_count(), # Use all available CPU cores
    )
    joined_clip.close()

    add_sub = input("Do you want to add subtitles too?[Y/N]: ")
    if add_sub.upper() == "N":
        exit()

    sub_height = float(input("Enter how high the subtitles are needed to be(center Default): (0-1)"))

    subtitles = mb_subtitles.generate_word_level_subtitles_assemblyai(f"{OUT_FOLDER}/{output_video_name}_ranked_videos.mp4")
    generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                                font_size=80,
                                color='white', stroke_width=5, 
                                text_align="center",
                                stroke_color="black", method="caption", 
                                size=((1080, 100)), 
                                )
    with open("subtitles.srt", "w") as f:
        f.write(subtitles)

    subtitles = SubtitlesClip("subtitles.srt", make_textclip=generator, encoding='utf-8')

    file_name = f"{OUT_FOLDER}/{output_video_name}_ranked_with_sub.mp4"
    res = CompositeVideoClip([VideoFileClip(f"{OUT_FOLDER}/{output_video_name}_ranked_videos.mp4"),
                                subtitles.with_position(("center", "center" if int(sub_height * 1920) == 0 else int(sub_height * 1920)))])

    res.write_videofile(file_name,
                        threads=os.cpu_count())
    res.close()

except Exception as e:
    print(colored(f"Exception: {e}", "red"))
    print(colored(traceback.format_exc(), "red"))

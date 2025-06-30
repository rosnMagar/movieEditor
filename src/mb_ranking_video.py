import json
import traceback
import re
from moviepy import *
from moviepy.video.tools.subtitles import SubtitlesClip
import uuid
import os
from dotenv import load_dotenv
from termcolor import colored
from skimage.filters import gaussian
from skimage.util import img_as_float, img_as_ubyte
from mb_tts import MB_TTS

import mb_subtitles
import numpy as np


load_dotenv()

OUT_FOLDER = "./output"
TMP_FOLDER = "./tmp"
FONT = "LilitaOne-Regular.ttf"

try:
    os.mkdir(OUT_FOLDER)
except:
    print("Output Folder Exists")

output = []

with open("ranking_input.json", "r") as file:
    data = json.load(file)
    bg_dir = data['bg_dir']
    require_sub = data['require_sub']
    video_order = data['video_order']
    video_meta = data['video_meta']

if require_sub:
    sub_height = data['sub_height'] 

try:
    entries = os.listdir(bg_dir)
    clip_data = [] 
    clips_index = 0

    def get_file_number(entry):
        """
        Helper function to extract the numerical part from a filename.
        Returns the integer if found, otherwise a very low number to place
        non-matching files at the end if they somehow get into the sorted list.
        """
        if entry.is_file() and entry.name.lower().endswith('.mp4'):
            match = re.match(r'(\d+)\.mp4$', entry.name.lower())
            if match:
                return int(match.group(1))
        return -1 # Return a value that ensures non-matching files are at the end when sorting numerically descending


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
        for video_index, entry in enumerate(sorted(list(entries), key=get_file_number)):
            if entry.is_file():
                print(colored(f"File Found: {entry.path}", 'green'))
                try:

                    # Attempt to load as a video clip
                    print(colored("Filename should match title rank 1-5", "blue"))

                    title = video_meta[video_index]['title']
                    sub = video_meta[video_index]['sub_required']
                    intro_required = video_meta[video_index]['intro_required']
                    intro_speech = video_meta[video_index]['intro_speech']
                    rank_index = video_meta[video_index]['rank_index']

                    out_filename = f"{TMP_FOLDER}/tmp_rank_{clips_index}"

                    clip_data.append({
                        "id": clips_index,
                        "src_file": entry.path,
                        "file_name": out_filename,
                        "text": title,
                        "sub": sub,
                        "intro_required": intro_required,
                        "intro_speech": intro_speech,
                        "rank": rank_index
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
   
    for j in video_order:

        clip = clip_data[j]

        src_clip = VideoFileClip(clip['src_file'])
        src_clip = src_clip.resized((1080, 1920))

        # done for every clip!
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
                            .with_position((150, ((len(clip_data) + (j - 5)) * clip_space_delta * 3) + 410))
                            .with_duration(src_clip.duration))

        composite_input = [src_clip]
        composite_input.extend(number_texts)
        composite_input.extend(burn_texts)
        composite_clip = CompositeVideoClip(composite_input)

        composite_clip_audio_file = f"{TMP_FOLDER}/audio_tmp_composite_clip.mp3"
        composite_clip.audio.write_audiofile(composite_clip_audio_file)

        if clip['sub']:
            subtitles = mb_subtitles.generate_word_level_subtitles_assemblyai(composite_clip_audio_file)
            generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                                        font_size=100,
                                        color='white', stroke_width=10, 
                                        text_align="center",
                                        stroke_color="black", method="caption", 
                                        size=((1080, 200)), 
                                        )
            with open("subtitles.srt", "w") as f:
                f.write(subtitles)
            # subtitles generated make some changes
            input(f"Edit Subtitles.srt for Clip: {clip['src_file']} Title: {clip['text']}  and press Enter to continue...")
            try:
                subtitles = SubtitlesClip("subtitles.srt", make_textclip=generator, encoding='utf-8')

                res = CompositeVideoClip([composite_clip,
                                        subtitles.with_position(("center", "center" if int(sub_height * 1920) == 0 else int(sub_height * 1920)))])
            except:
                res = CompositeVideoClip([composite_clip])
        else:
            res = CompositeVideoClip([composite_clip])

        # generate audio and subtitles for clip intro
        if j > 0 and clip['intro_required']:
            intro_audio_file_name = f"{clip['file_name']}_intro_clip.mp3"
            tts = MB_TTS(intro_audio_file_name)
            tts.speak(clip['intro_speech'], speaking_speed=1.3, lang='en')

            def apply_blur(image, sigma):
                img_float = img_as_float(image)
                blurred_image = gaussian(img_float, sigma=sigma, channel_axis=-1)
                blurred_img_uint8 = img_as_ubyte(blurred_image)
                return blurred_img_uint8 

            intro_audio = AudioFileClip(intro_audio_file_name)
            bg_img = ImageClip(apply_blur(res.get_frame(1), 4)).with_duration(intro_audio.duration - 0.1)

            bg = CompositeVideoClip([bg_img]).with_audio(intro_audio)

            subtitles = mb_subtitles.generate_word_level_subtitles_assemblyai(intro_audio_file_name)
            generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                                        font_size=100,
                                        color='white', stroke_width=10, 
                                        text_align="center",
                                        stroke_color="black", method="caption", 
                                        size=((1080, 200)), 
                                        )
            with open("subtitles.srt", "w") as f:
                f.write(subtitles)
            
            # subtitles generated make some changes
            input(f"Edit Subtitles.srt for intro: {j}  and press Enter to continue...")

            try:
                subtitles = SubtitlesClip("subtitles.srt", make_textclip=generator, encoding='utf-8')

                bg = CompositeVideoClip([bg,
                                        subtitles.with_position(("center", "center" if int(sub_height * 1920) == 0 else int(sub_height * 1920)))])
            except:
                bg = CompositeVideoClip([bg])

            res = concatenate_videoclips([bg, res])

        res.write_videofile(
            f"{clip['file_name']}.mp4",
            fps=30,
            threads=os.cpu_count(), # Use all available CPU cores
        )

    if not clip_data:
        print(colored(f"No valid video files found or loaded from directory: {bg_dir}", "red"))

    print(colored(f"Successfully loaded {len(clip_data)} video clip(s).", "blue"))

    # after videos are loaded:
    output_video_name = uuid.uuid4() 

    videos = []
    for video_index in video_order:
        videos.append(VideoFileClip(f"{clip_data[video_index]['file_name']}.mp4"))

    joined_clip = concatenate_videoclips(videos)
    final_clip = joined_clip.resized((1080, 1920))
    joined_clip.write_videofile(
        f"{OUT_FOLDER}/{output_video_name}_ranked_videos.mp4",
        threads=os.cpu_count(), # Use all available CPU cores
        fps=30
    )
    joined_clip.close()
    res.close()

except Exception as e:
    print(colored(f"Exception: {e}", "red"))
    print(colored(traceback.format_exc(), "red"))

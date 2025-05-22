from turtle import bgcolor
import google.generativeai as genai
from gtts import gTTS
from moviepy import *
import numpy as np
import os
from dotenv import load_dotenv
import json

from mb_pexels import MB_OnlineVideo
from mb_stage_assets import MB_OnlineVideo, MBStageAssets
import mb_util
import mb_subtitles 

from tiktok_voice import Voice
from moviepy.video.tools.subtitles import SubtitlesClip

load_dotenv()

# loading the api key from .env
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

OUT_FOLDER = "./output"
TMP_FOLDER = "./tmp"
FONT = "LilitaOne-Regular.ttf"

try:
    os.mkdir(OUT_FOLDER)
except:
    print("Output Folder Exists")

def generate_trivia(topic="random"):
    if topic == "random":
        sub_prompt = "Chose a random topic for telling facts to people about the topic."
    else:
        sub_prompt = f"Chose the topic as: {topic} for telling facts about that topic."
    prompt = f"""
        We are creating a short video like tiktok, or youtube short.
        {sub_prompt}
        Do not include any markdown, backticks, or code formatting — just output the content as plain text.
        Also do not include "..." because the tts reads it as dot dot dot. 

        Give me a response in json-like format: 

        chose very unique facts to present, not the usual facts most people know. 

        While generating content follow the HTC pattern. First Create a great hook, then create 
        tension and deliver the content. Use this pattern if you can.

        - for facts:
        topic:"",
        intro:{{
        "content": "actual content" 
        "assets":[""] // 3 keyword string keywords for related video clips
        }},
        cta:{{
        "content": "actual content" 
        "assets":[""] // 3 keyword string keywords for related video clips
        }},
        cta:{{
        "content": "actual content" 
        "assets":[""] // 3 keyword string keywords for related video clips
        }},
        // this is a list with objects
        facts:[{{fact: "", assets:[""...]}}...more facts],

        Remember this script is meant for reading by the tiktok text to speech api, so avoid any unnecessary text that confuses tts softwares. 
        
        Ask users to interact with the platform like comment, like and share.
        Also ask them to answer something in comment. Get creative with this.
        Do not CTA in the beginning do it in the middle of the video or at the end.

        Make sure you have at least 5 facts if it is short.
        For longer ones you can have at least 3. Make sure the video script will be around 40s-60s long.
    """
    model = genai.GenerativeModel("gemini-2.0-flash", generation_config=genai.GenerationConfig(temperature=1))

    response = model.generate_content(prompt)

    # cleanup for ```json
    output = response.text[len("```json"): len("```") * -1]
    output = json.loads(mb_util.remove_emoji(output))
    print(output)

    return output 

mode = int(input("""
Minecraft mode or general mode?: 
1. Press 1 for minecraft
2. Press 2 for general
"""))

if mode == 1:
    output = input("Enter your script: ")
elif mode == 2:
    prompt_topic = input("Please Enter a topic to make a fact video on: ")
    output = generate_trivia(prompt_topic)
else:
    print("Error: Exiting the program...")
    exit()

clips = []

if mode == 1:
    stager = MBStageAssets(['cats'], f"{TMP_FOLDER}/clip_1", text=output, voice=Voice.MALE_DEADPOOL)
    clips.append(VideoFileClip(stager.create_minecraft_clip()))
elif mode == 2:
    i = 0
    for key in output.keys():
        if key == "topic":
            continue
        if key == "facts":
            for fact in output[key]:
                stager = MBStageAssets(fact['assets'], f"{TMP_FOLDER}/clip_{i}", text=fact['fact'], voice = Voice.MALE_FUNNY)
                print("Fact:::", fact['assets'], f"{TMP_FOLDER}/clip_{i}", fact['fact'])
                clips.append(VideoFileClip(stager.create_clip()))
                i += 1
            continue
        stager = MBStageAssets(output[key]['assets'], f"{TMP_FOLDER}/clip_{i}", text=output[key]['content'], voice=Voice.MALE_FUNNY)
        print("OTHERS:::", output[key]['assets'], f"{TMP_FOLDER}/clip_{i}", output[key]['content'])
        clips.append(VideoFileClip(stager.create_clip()))
        i += 1

video = concatenate_videoclips(clips)
if mode == 1:
    video.write_videofile(f"{OUT_FOLDER}/final_no_sub_minecraft_video.mp4")
    video.audio.write_audiofile(f"{OUT_FOLDER}/final_no_sub_minecraft_video.mp3")
elif mode == 2:
    video.write_videofile(f"{OUT_FOLDER}/final_no_sub{mb_util.snake_case(output['topic'])}_video.mp4")
    video.audio.write_audiofile(f"{OUT_FOLDER}/final_no_sub_{mb_util.snake_case(output['topic'])}_video.mp3")


# subtitles
if mode == 1:
    subtitles = mb_subtitles.generate_word_level_subtitles_assemblyai(f"{OUT_FOLDER}/final_no_sub_minecraft_video.mp3")
    background_color = None
    with open("subtitles.srt", "w") as f:
        f.write(subtitles)
else:
    subtitles = mb_subtitles.generate_subtitles_assemblyai(f"{OUT_FOLDER}/final_no_sub_{mb_util.snake_case(output['topic'])}_video.mp3")
    background_color="#6496d9",
    with open("subtitles.srt", "w") as f:
        f.write(subtitles)

generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                                font_size=69,
                                color='white', stroke_width=2, 
                                text_align="center",
                                bg_color=background_color,
                                stroke_color="black", method="caption", size=(int(video.w * 0.8), 80))

subtitles = SubtitlesClip("subtitles.srt", make_textclip=generator, encoding='utf-8')

if mode == 1:
    res = CompositeVideoClip([VideoFileClip(f"{OUT_FOLDER}/final_no_sub_minecraft_video.mp4"),
                            subtitles.with_position(("center", "center"))])
    res.write_videofile(f"{OUT_FOLDER}/final_minecraft_video.mp4")
elif mode == 2:
    res = CompositeVideoClip([VideoFileClip(f"{OUT_FOLDER}/final_no_sub{mb_util.snake_case(output['topic'])}_video.mp4"),
                            subtitles.with_position(("center", video.h * (1 - 0.3)))])
    res.write_videofile(f"{OUT_FOLDER}/final_{mb_util.snake_case(output['topic'])}_video.mp4")


video.close()
res.close()

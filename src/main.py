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

load_dotenv()

# loading the api key from .env
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

OUT_FOLDER = "../output"
TMP_FOLDER = "../tmp"
FONT = "LilitaOne-Regular.ttf"

try:
    os.mkdir(OUT_FOLDER)
except:
    print("Output Folder Exists")

def linear_gradient(size, colors):
    # size = (width, height), colors = [(R,G,B), (R,G,B)]
    gradient = np.linspace(0, 1, size[0])
    gradient = np.vstack([gradient]*size[1])
    gradient = np.dstack([gradient]*3)
    
    # Apply colors
    color1, color2 = np.array(colors[0]), np.array(colors[1])
    colored_gradient = color1 + (color2 - color1) * gradient
    
    return colored_gradient.astype('uint8')

def generate_trivia(topic="random"):
    if topic == "random":
        sub_prompt = "Chose a random topic for telling facts to people about the topic."
    else:
        sub_prompt = f"Chose the topic as: {topic} for telling facts about that topic."
    prompt = f"""
        We are creating a short video like tiktok, or youtube short.
        {sub_prompt}
        Do not include any markdown, backticks, or code formatting — just output the content as plain text.

        Give me a response in json-like format: 

        chose facts to present 

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
        "outro": "actual content" 
        "assets":[""] // 3 keyword string keywords for related video clips
        }},
        // this is a list with objects
        facts:[{{fact: "", assets:[""...]}}...more facts],

        Make the script very engaging. For example ask users to interact with the platform like comment, like and share.
        Also ask them to answer something in comment. (example: Type something with eyes closed in the comments)
        Do not CTA in the beginning do it in the middle of the video or at the end.
        Make the script clean, no special characters, only very few emojis and text.

        Make sure you have at least 10 facts if it is short.
        For longer ones you can have 5. Make sure the video script will be around 1-1.5 minutes long.
    """
    model = genai.GenerativeModel("gemini-2.0-flash", generation_config=genai.GenerationConfig(temperature=0.5))

    response = model.generate_content(prompt)

    # cleanup for ```json
    output = response.text[len("```json"): len("```") * -1]
    output = json.loads(mb_util.remove_emoji(output))

    return output 

def generate_audio(text, filename="audio.mp3"):
    tts = gTTS(text)
    tts.save(filename)
    return filename

def create_video(theme, audio_path, out_path = "trivia_video.mp4"):

    pexels_video = MB_OnlineVideo(query=theme)
    url, photographer, src = pexels_video.download(OUT_FOLDER)
    print(url, photographer, src)

    audio = AudioFileClip(audio_path)
    bg = VideoFileClip(url)
    # bg = bg.resized((1080, 1920))
    bg = bg.resized((240, 352))
    # Composite the video
    video = CompositeVideoClip([bg]).with_audio(audio)
    video.write_videofile(f"{OUT_FOLDER}/{mb_util.snake_case(output['topic_keyword'])}.mp4", fps=24, threads=4)

output = generate_trivia()
print(output)

# generate_audio(output["intro"] + output["cta"] + output["outro"], filename=f"{OUT_FOLDER}/{snake_case(output['topic_keyword'])}.mp3")
# create_video(theme=output["topic_keyword"], audio_path=f"{OUT_FOLDER}/{snake_case(output['topic_keyword'])}.mp3")


for i, key in enumerate(output.keys()):
    if key == "topic":
        continue
    if key == "facts":
        for fact in output[key]:
            stager = MBStageAssets(fact['assets'], f"{TMP_FOLDER}/facts/clip_{i}")
            stager.create_clip()
        continue
    print(key)
    stager = MBStageAssets(output[key]['assets'], f"{TMP_FOLDER}/clip_{i}")
    stager.create_clip()
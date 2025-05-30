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

def generate_script(topic="random"):
    if topic == "random":
        sub_prompt = "Chose a random topic for telling facts to people about the topic."
    else:
        sub_prompt = f"Chose the topic as: {topic} for telling facts about that topic."
    prompt = f"""
        You are a content creator with millions of followers. 
        Your primary goal is to generate a script for a short video (e.g., TikTok, YouTube Short) based on the specific {sub_prompt} provided by the user.

        Overall Output Requirements:

        Format: Text With no Emojis, easily readable by TTS softwares(Coqui TTS).
        All string values within the output MUST be plain text. Do NOT use any Markdown, backticks, or other code formatting within these strings.
        TTS-Friendliness: Script content must be optimized for Text-to-Speech (TTS) narration.
        Avoid ellipses ("..."); write complete sentences instead.
        Avoid abbreviations or complex symbols that TTS might misinterpret.
        Use clear, concise language.

        Unique Facts: Prioritize surprising, lesser-known, and intriguing facts directly related to the {sub_prompt}. Avoid commonly known information.
        HTC Pattern (Hook, Tension, Content):
        Hook: Start with an engaging opening to immediately capture viewer attention.
        Tension: Build curiosity or anticipation before revealing the main facts.
        Content: Clearly present the unique facts.
        Video Length: The script should be designed to produce a video approximately 30 to 40 seconds long.
        Number of Facts:
        Include at least 5 facts if the facts are very short and concise.
        Include at least 3 facts if the facts are more detailed. Adjust as needed to meet the target video length.
        Calls to Action (CTAs) & Engagement:
        Do NOT include major CTAs at the very beginning of the script.
        Incorporate opportunities for user interaction (e.g., likes, shares, comments).
        Include a specific, creative question for viewers to answer in the comments section, related to the video's topic. This should ideally be towards the end.
        Please include commas(,) and full stops(.) This helps the TTS learn where to pause and stop.

        Make the script unique and creative. 

    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17", generation_config=genai.GenerationConfig(temperature=1))

        response = model.generate_content(prompt)

        # cleanup for ```json
        # output = response.text[len("```json"): len("```") * -1]
        # output = json.loads(mb_util.remove_emoji(output))
        print(response.text)

        return response.text 
    except:
        print("Error while generating the results, do you want to write the script yourself following the json guidelines?")
        output = input("Json Input: ")
        return json.loads(mb_util.remove_emoji(output))

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

if input_mode == 1:
    output = input("Enter your script: ")
elif input_mode == 2:
    prompt_topic = input("Please Enter a topic to make a fact video on: ")
    output = generate_script(prompt_topic)
else:
    print("Error: Exiting the program...")
    exit()

bg_dir = input("Enter the folder directory for background videos: ")

stager = MBStageAssets(['cats'], f"{TMP_FOLDER}/clip_1", text=output)
video = VideoFileClip(stager.create_user_selected_video(bg_dir))

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

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
        Your primary goal is to generate a script for a short video (e.g., TikTok, YouTube Short) based on the specific {sub_prompt} provided by the user.

        Overall Output Requirements:

        Format: The entire response MUST be a single, valid JSON object.
        Content within JSON: All string values within the JSON (e.g., script lines, topic names) MUST be plain text. Do NOT use any Markdown, backticks, or other code formatting within these strings.
        TTS-Friendliness: Script content must be optimized for Text-to-Speech (TTS) narration.
        Avoid ellipses ("..."); write complete sentences instead.
        Avoid abbreviations or complex symbols that TTS might misinterpret.
        Use clear, concise language.
        Video Script Requirements (to be reflected in the JSON structure):

        Unique Facts: Prioritize surprising, lesser-known, and intriguing facts directly related to the {sub_prompt}. Avoid commonly known information.
        HTC Pattern (Hook, Tension, Content):
        Hook: Start with an engaging opening to immediately capture viewer attention.
        Tension: Build curiosity or anticipation before revealing the main facts.
        Content: Clearly present the unique facts.
        Video Length: The script should be designed to produce a video approximately 40-60 seconds long.
        Number of Facts:
        Include at least 5 facts if the facts are very short and concise.
        Include at least 3 facts if the facts are more detailed. Adjust as needed to meet the target video length.
        Calls to Action (CTAs) & Engagement:
        Do NOT include major CTAs at the very beginning of the script.
        Incorporate opportunities for user interaction (e.g., likes, shares, comments).
        Include a specific, creative question for viewers to answer in the comments section, related to the video's topic. This should ideally be towards the end.

        JSON Structure Definition:

        Please generate the JSON object with the following keys and structure:

        {{
            "topic": "The core subject of the video, derived from {sub_prompt}",
            "intro": {{
                "content": "Engaging opening (1-2 sentences) that acts as a hook and builds tension/curiosity for the facts to come.",
                "assets_keywords": ["keyword1", "keyword2", "keyword3"] // 3 concise keywords for related visuals
            }},
            "facts": [
            {{
                "fact": "Unique fact #1, presented clearly and engagingly.",
                "assets_keywords": ["keyword1", "keyword2", "keyword3"]
            }},
            {{
                "fact": "Unique fact #2, presented clearly and engagingly.",
                "assets_keywords": ["keyword1", "keyword2", "keyword3"]
            }}
            // Add more fact objects here as needed, following the quantity guidelines
            ],
            "cta": {{ // Optional, can be brief. Place after a few facts.
            "content": "A short prompt to encourage likes, shares, or a quick thought. Example: 'Pretty wild, right? If you agree, hit that like!'",
            "assets_keywords": ["keyword1", "keyword2", "keyword3"]
            }},
            "outro": {{
            "content": "Encourage follows, shares, and pose a creative, topic-related question for comments. Example: 'Want more mind-blowing facts? Follow us! And tell me in the comments: what's the most surprising thing you've learned about [Topic]?'",
            "assets_keywords": ["keyword1", "keyword2", "keyword3"]
            }}
        }}
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17", generation_config=genai.GenerationConfig(temperature=1))

        response = model.generate_content(prompt)

        # cleanup for ```json
        output = response.text[len("```json"): len("```") * -1]
        output = json.loads(mb_util.remove_emoji(output))
        print(output)

        return output 
    except:
        print("Error while generating the results, do you want to write the script yourself following the json guidelines?")
        output = input("Json Input: ")
        return json.loads(mb_util.remove_emoji(output))

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
                stager = MBStageAssets(fact['assets_keywords'], f"{TMP_FOLDER}/clip_{i}", text=fact['fact'])
                print("Fact:::", fact['assets_keywords'], f"{TMP_FOLDER}/clip_{i}", fact['fact'])
                clips.append(VideoFileClip(stager.create_clip()))
                i += 1
            continue
        stager = MBStageAssets(output[key]['assets_keywords'], f"{TMP_FOLDER}/clip_{i}", text=output[key]['content'])
        print("OTHERS:::", output[key]['assets_keywords'], f"{TMP_FOLDER}/clip_{i}", output[key]['content'])
        clips.append(VideoFileClip(stager.create_clip()))
        i += 1
elif mode == 3:
    stager = MBStageAssets(['cats'], f"{TMP_FOLDER}/clip_1", text=output, reddit_url="https://www.reddit.com/r/Millennials/comments/1kryeks/did_we_get_ripped_off_with_homework/")
    clips.append(VideoFileClip(stager.create_minecraft_clip()))

video = concatenate_videoclips(clips)
if mode == 1 or mode == 3:
    video.write_videofile(f"{OUT_FOLDER}/final_no_sub_minecraft_video.mp4")
    video.audio.write_audiofile(f"{OUT_FOLDER}/final_no_sub_minecraft_video.mp3")
elif mode == 2:
    video.write_videofile(f"{OUT_FOLDER}/final_no_sub{mb_util.snake_case(output['topic'])}_video.mp4")
    video.audio.write_audiofile(f"{OUT_FOLDER}/final_no_sub_{mb_util.snake_case(output['topic'])}_video.mp3")
# subtitles
if mode == 1:
    subtitles = mb_subtitles.generate_word_level_subtitles_assemblyai(f"{OUT_FOLDER}/final_no_sub_minecraft_video.mp3")
    generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                                font_size=69,
                                color='white', stroke_width=2, 
                                text_align="center",
                                stroke_color="black", method="caption", size=(int(video.w * 0.8), 80))
    with open("subtitles.srt", "w") as f:
        f.write(subtitles)
elif mode==2:
    subtitles = mb_subtitles.generate_subtitles_assemblyai(f"{OUT_FOLDER}/final_no_sub_{mb_util.snake_case(output['topic'])}_video.mp3")

    generator = lambda text: TextClip(text=text, font='./LilitaOne-Regular.ttf',
                                font_size=52,
                                color='white', stroke_width=2, 
                                text_align="center",
                                bg_color="#6496d9",
                                stroke_color="black", method="caption", size=(int(video.w * 0.8), None))
 
    with open("subtitles.srt", "w") as f:
        f.write(subtitles)

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

import google.generativeai as genai
from gtts import gTTS
from moviepy import *
import os
from dotenv import load_dotenv
import json
import emoji
from mb_pexels import MB_OnlineImage

load_dotenv()

# loading the api key from .env
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

OUT_FOLDER = "output"

try:
    os.mkdir(OUT_FOLDER)
except:
    print("Output Folder Exists")

def remove_emoji(text):
    return emoji.replace_emoji(text, replace="")

def generate_trivia(topic="random"):
    prompt = f"""
        We are creating a short video like tiktok, or youtube short about {topic}
        Do not include any markdown, backticks, or code formatting — just output the content as plain text.
        Give me a response in json-like format: 

        randomly chose one topic, trivia or facts

        for trivia videos:
        intro:"",
        cta: "",
        outro: "", 
        {{
        [Question: "...",
        Options: [],
        answer: "...",
        img_keywords: ["..",".."],
        wait_time: // time in seconds
        ], ... more}},
        topic_keyword="keywords related to the content" // one or two words
        for facts:

        intro:"",
        cta:"",
        outro:"",
        facts:[{{fact: "", img_keywords:[""...]}}...more facts],
        topic_keyword="keywords related to the content" // one or two words

        for trivia questions, you need to add a 10s or 5s timer after each question depending on the difficulty.

        Make the script very engaging. For example ask users to interact with the platform like comment, like and share.
        Also ask them to answer something in comment. (example: Type something with eyes closed in the comments)
        Do not CTA in the beginning do it in the middle of the video or at the end.
        Make the script clean, no special characters, only very few emojis and text.

        Make sure you have at least 10 questions or facts if it is short.
        For longer ones you can have 5. Make sure the video script will be around 1-1.5 minutes long.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    # cleanup for ```json
    output = response.text[len("```json"): len("```") * -1]
    output = json.loads(remove_emoji(output))

    return output 

def generate_audio(text, filename="audio.mp3"):
    tts = gTTS(text)
    tts.save(filename)
    return filename

def snake_case(text):
    return str(text).replace(" ", "_")

def create_video(theme, audio_path, out_path = "trivia_video.mp4"):

    pexels_image = MB_OnlineImage(query=theme)
    url, photographer, src = pexels_image.download(OUT_FOLDER)
    print(url, photographer, src)

    # txt_q = TextClip(text=f"Q: {question}", font="./Barlow-Regular.ttf", font_size=60, color="white", size=(1000, None)).with_position("center").with_duration(5)
    # txt_a = TextClip(text=f"A: {answer}", font="./Barlow-Regular.ttf", font_size=60, color="white", size=(1000, None)).with_position("center").with_start(5).with_duration(5)
    audio = AudioFileClip(audio_path)
    bg = ImageClip(url).with_duration(audio.duration)
    # bg = bg.resized((1080, 1920))
    bg = bg.resized((360, 680))
    text = TextClip(font="Barlow-Regular.ttf", text="Hello MoviePy!", font_size=70, color='white')
    text = text.with_position('center').with_duration(10)

    # Composite the video
    video = CompositeVideoClip([bg, text]).with_audio(audio)
    video.write_videofile(f"{OUT_FOLDER}/{snake_case(output['topic_keyword'])}.mp4", fps=24, threads=4)

output = generate_trivia()
print(output)

generate_audio(output["intro"] + output["cta"] + output["outro"], filename=f"{OUT_FOLDER}/{snake_case(output['topic_keyword'])}.mp3")
create_video(theme=output["topic_keyword"], audio_path=f"{OUT_FOLDER}/{snake_case(output['topic_keyword'])}.mp3")

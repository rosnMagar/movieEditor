from mb_pexels import MB_OnlineVideo
from mb_tts import MB_TTS
from tiktok_voice import Voice
from moviepy import *
import mb_util

import os
import uuid

STAGED_FOLDER = "../tmp/staged_audio"

class MBStageAssets():
    """
    A class to download video assets from Pexels based on search keywords.
    
    Attributes:
        keywords (list): List of search terms for finding videos
        dest (str): Destination folder for downloaded videos
    """
    def __init__(self, keywords, dest = 'folder1', text = "This is a test"):
        """
        Initializes the MBStageAssets downloader.
        
        Args:
            keywords (list): List of search terms to find videos
            dest (str, optional): Destination folder for downloads. Defaults to 'folder1'.
        """
        self.keywords = keywords
        self.text = text
        self.dest = dest

    def create_clip(self):
        """
        Downloads videos for all keywords in the instance's keyword list.
        
        For each keyword:
        1. Creates an MB_OnlineVideo instance with the keyword and duration of 5 seconds
        2. Downloads the video to the specified destination folder
        3. Prints download information including source path, artist credit, and original URL
        
        Outputs:
            Prints download confirmation and attribution information for each video
        """

        try:
            os.makedirs(self.dest)
        except:
            print("Output Folder Exists")

        videos = []

        for keyword in self.keywords:
            # video section
            video_url = self.create_video(keyword)
            videos.append(video_url)

            # audio section
            audio_url = self.create_audio(text=self.text, voice=Voice.MALE_GRINCH, file_name=self.dest)

        audio = AudioFileClip(audio_url)
        clip_duration = audio.duration

        bg = VideoFileClip(videos[0])
        
        video_index = 1
        while bg.duration < clip_duration:
            try:
                bg2 = VideoFileClip(videos[video_index])
                bg = CompositeVideoClip([bg, bg2])
                video_index += 1
            except:
                # mu is the slow down factor to match the duration of the audio clip 
                mu = bg.duration / clip_duration
                bg = bg.without_audio().speedx(mu)

        # bg = bg.resized((1080, 1920))
        bg = bg.subclipped(0, clip_duration)
        bg = bg.resized((240, 352))
        # Composite the video
        video = CompositeVideoClip([bg]).with_audio(audio)
        video.write_videofile(f"{self.dest}.mp4", fps=24, threads=4)
   
    def create_video(self, keyword):
        video = MB_OnlineVideo(keyword, 5)
        video_url, artist, source_url = video.download(destination=self.dest) 

        print(f"Video Clip Downloaded: {video_url}")
        print(f"Video Credit: {artist}")
        print(f"URL: {source_url} \n")
        print("--------------------------------------------")
        print()

        return video_url, artist, source_url
    
    
    def create_audio(self, text = "This is a test", voice=Voice.PIRATE, file_name = ""):
        if name == "":
            name = "audio" + "_" + uuid.uuid4()
        tts = MB_TTS(str=f"{STAGED_FOLDER}/{name}.mp3", voice=voice)
        tts.speak(text)
        return f"{STAGED_FOLDER}/{name}.mp3"

    



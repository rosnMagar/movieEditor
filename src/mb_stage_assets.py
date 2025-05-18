from mb_pexels import MB_OnlineVideo
from mb_tts import MB_TTS
from tiktok_voice import Voice
from moviepy import *
import mb_util

import os
import uuid

class MBStageAssets():
    """
    A class to download video assets from Pexels based on search keywords.
    
    Attributes:
        keywords (list): List of search terms for finding videos
        dest (str): Destination folder for downloaded videos
    """
    def __init__(self, keywords, dest = 'folder1', text = "This is a test", voice=Voice.US_FEMALE_1):
        """
        Initializes the MBStageAssets downloader.
        
        Args:
            keywords (list): List of search terms to find videos
            dest (str, optional): Destination folder for downloads. Defaults to 'folder1'.
        """
        self.keywords = keywords
        self.text = text
        self.dest = dest
        self.voice = voice 

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
            video_url, artist, source_url = self.create_video(keyword)
            videos.append(video_url)

            # audio section
            audio_url = self.create_audio(text=self.text, voice=self.voice, file_name=self.dest)

        audio = AudioFileClip(audio_url)
        clip_duration = audio.duration

        bg = VideoFileClip(videos[0])
        
        video_index = 1
        for video_path in videos[1:]:
            if bg.duration > clip_duration:
                break

            try:
                bg2 = VideoFileClip(videos[video_index])
                bg = concatenate_videoclips([bg, bg2])
            except Exception as e:
                print(f"error loading video {video_path}: {str(e)}")
                
        if bg.duration < clip_duration:
            bg = bg.with_effects([vfx.MultiplySpeed(clip_duration)])

        # bg = bg.resized((1080, 1920))
        bg = bg.subclipped(0, clip_duration)
        bg = bg.resized((240, 352))
        # Composite the video
        video = CompositeVideoClip([bg]).with_audio(audio)

        video.write_videofile(f"{self.dest}.mp4", fps=24, threads=4)
        return f"{self.dest}.mp4"
   
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
        if file_name == "":
            file_name = "audio" + "_" + uuid.uuid4()
        tts = MB_TTS(dest=f"{file_name}.mp3", voice=voice)
        tts.speak(text)
        return f"{file_name}.mp3"

    



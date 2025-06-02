from fileinput import filename
from genericpath import isfile
from mb_minecraft_subclip import MBMineCraftSubClip
from mb_pexels import MB_OnlineVideo
from mb_tts import MB_TTS
from moviepy import *
from mb_reddit import TMP_DIR, MBReddit
from termcolor import colored

import random
import os
import uuid

class MBStageAssets():
    """
    A class to download video assets from Pexels based on search keywords.
    
    Attributes:
        keywords (list): List of search terms for finding videos
        dest (str): Destination folder for downloaded videos
    """
    def __init__(self, keywords, dest = 'folder1', text = "This is a test", reddit_url=None):
        """
        Initializes the MBStageAssets downloader.
        
        Args:
            keywords (list): List of search terms to find videos
            dest (str, optional): Destination folder for downloads. Defaults to 'folder1'.
        """
        self.keywords = keywords
        self.text = text
        self.dest = dest
        self.reddit_url = reddit_url

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

        if len(videos) == 0:
            video_url, artist, source_url = self.create_video("random")

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

        bg = bg.resized((1080, 1920))
        bg = bg.subclipped(0, clip_duration)
        # bg = bg.resized((240, 352))
        # bg = bg.resized((360, 640))
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

    def create_user_selected_video(self, dir, audio_required = True):
        try:
            entries = os.listdir(dir)
            videos = []
            with os.scandir(dir) as entries:
                for entry in entries:
                    if entry.is_file():
                        print(colored(f"File Found: {entry.path}", 'green'))
                        try:
                            # Attempt to load as a video clip
                            clip = VideoFileClip(entry.path)
                            videos.append(clip)
                            print(colored(f"Successfully loaded {entry.name} as a video clip.", "green"))
                        except Exception as e_clip:
                            # If it's not a valid video file, VideoFileClip will raise an error
                            print(colored(f"Could not load {entry.name} as a video clip: {e_clip}. Skipping.", "yellow"))

            if not videos:
                print(colored(f"No valid video files found or loaded from directory: {dir}", "red"))
                return None # Explicitly return None if no videos

            print(colored(f"Successfully loaded {len(videos)} video clip(s).", "blue"))

            audio_url = self.create_audio(self.text, file_name=self.dest)
            audio = AudioFileClip(audio_url)
            clip_duration = audio.duration

            preserve_order = input("Do you want videos in order? (Y/N): ")

            if preserve_order.upper() == "N":
                random.shuffle(videos)

            bg = concatenate_videoclips(videos).without_audio()
            bg = bg.with_effects([vfx.MultiplySpeed(factor=1.5)])

            if bg.duration < clip_duration:
                bg = bg.with_effects([vfx.MultiplySpeed(final_duration=clip_duration)])

            bg = bg.resized((1080, 1920))
            bg = bg.subclipped(0, clip_duration)

            final_video = CompositeVideoClip([bg]).with_audio(audio)
            final_video.write_videofile(f"{self.dest}.mp4", fps=24, threads=4)
            return f"{self.dest}.mp4"

        except FileNotFoundError:
            print(f"Error: Directory not found at {dir}")
        except Exception as e:
            print(f"An error occurred: {e}")

    
    def create_minecraft_clip(self):
        if self.reddit_url != None:
            mb_reddit_image = MBReddit(self.reddit_url)
            mb_reddit_image.get_post_screenshot()
            title = mb_reddit_image.get_post_title()
            mb_reddit_image.close_driver()

            title_audio_url = self.create_audio(text=title, file_name=f"{self.dest}_title")
            title_audio = AudioFileClip(title_audio_url)
            reddit_image = ImageClip(f"{TMP_DIR}/reddit_topic.png")
            reddit_image = reddit_image.with_duration(title_audio.duration)

            audio_url = self.create_audio(text=self.text, file_name=self.dest)
            audio = AudioFileClip(audio_url)

            final_audio = concatenate_audioclips([title_audio, audio])
            clip_duration = audio.duration + title_audio.duration

            minecraft_clip = MBMineCraftSubClip(clip_duration)
            bg = minecraft_clip.get_sub_clip() 
            minecraft_clip.close_video()

            reddit_image = reddit_image.with_position(("center", bg.h * 0.2))

            video = CompositeVideoClip([bg, reddit_image]).with_audio(final_audio)
            video.write_videofile(f"{self.dest}.mp4", fps=60, threads=4)
            return f"{self.dest}.mp4"
    

        else:
            audio_url = self.create_audio(text=self.text, voice=self.voice, file_name=self.dest)
            audio = AudioFileClip(audio_url)
            clip_duration = audio.duration 
            minecraft_clip = MBMineCraftSubClip(clip_duration)
            bg = minecraft_clip.get_sub_clip() 
            minecraft_clip.close_video()

        video = CompositeVideoClip([bg]).with_audio(audio)
        video.write_videofile(f"{self.dest}.mp4", fps=60, threads=4)
        return f"{self.dest}.mp4"
    
    def create_audio(self, text = "This is a test", file_name = ""):
        if file_name == "":
            file_name = "audio" + "_" + uuid.uuid4()
        tts = MB_TTS(dest=f"{file_name}.mp3")
        tts.speak(text, speaking_speed=1.5)
        return f"{file_name}.mp3"

    



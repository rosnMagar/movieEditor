from turtle import end_poly
from moviepy import *
from moviepy.video.fx.Crop import Crop
import random 

MINECRAFT_FOLDER = "./backgrounds/minecraft"

class MBMineCraftSubClip():

    def __init__(self, duration = 30):
        self.duration = duration

    def get_sub_clip(self):
        self.video_clip = VideoFileClip(f"{MINECRAFT_FOLDER}/minecraft{random.randrange(1,3)}.mp4")

        start_point = random.randint(0, int(self.video_clip.duration - self.duration))
        self.video_clip = self.video_clip.subclipped(start_point, start_point + self.duration)

        height = self.video_clip.h
        width = int(height * 9 / 16)

        x1 = int(self.video_clip.w / 2) - int(width / 2)
        x2 = x1 + width

        return self.video_clip.with_effects([Crop(x1=x1, y1=0, x2=x2, y2=height)])
    
    def close_video(self):
        self.video_clip.close()
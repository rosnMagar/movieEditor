import traceback
import mb_subtitles
from moviepy import ColorClip, ImageClip, TextClip, CompositeVideoClip, VideoFileClip, concatenate_videoclips
from moviepy.video.tools.subtitles import SubtitlesClip
import uuid
import numpy as np
from PIL import Image

OUT_FOLDER = "./output"
video_dir = input("Enter the video directory: ")
font_size = int(input("Enter Font size(80 default): "))
sub_height = float(input("Enter how hight the subtitles are needed to be(center Default): "))

subtitles = mb_subtitles.generate_word_level_subtitles_assemblyai(video_dir)

def bouncing_scale(t):
    return 1 + 0.5 * np.exp(-5 * t) * np.cos(15 * t)

# Frame filter function for a TextClip
def apply_bounce_effect_to_frame(get_frame, t):
    frame = get_frame(t)
    return frame.resize(bouncing_scale(t))

def process_bouncing_frame(get_initial_frame_func, t, initial_w, initial_h):
    frame_array = get_initial_frame_func(t)
    scale_factor = bouncing_scale(t)
    new_w = int(initial_w * scale_factor)
    new_h = int(initial_h * scale_factor)
    new_w = max(1, new_w)
    new_h = max(1, new_h)
    
    pil_image = Image.fromarray(frame_array)
    resized_pil_image = pil_image.resize((new_w, new_h), Image.LANCZOS)
    resized_frame_array = np.array(resized_pil_image)
    
    output_frame = np.zeros_like(frame_array) 
    
    paste_x = (initial_w - new_w) // 2
    paste_y = (initial_h - new_h) // 2
    
    target_y_start = max(0, paste_y)
    target_y_end = min(initial_h, paste_y + new_h)
    target_x_start = max(0, paste_x)
    target_x_end = min(initial_w, paste_x + new_w)

    source_y_start = max(0, -paste_y)
    source_y_end = min(new_h, initial_h - paste_y)
    source_x_start = max(0, -paste_x)
    source_x_end = min(new_w, initial_h - paste_x)
    
    output_frame[target_y_start:target_y_end, target_x_start:target_x_end] = \
        resized_frame_array[source_y_start:source_y_end, source_x_start:source_x_end]
    
    return output_frame

def generator(txt):
    text_clip = TextClip(text=txt, font='./LilitaOne-Regular.ttf',
                            font_size=font_size,
                            color='white', stroke_width=10, 
                            text_align="center",
                            stroke_color="black", method="caption", 
                            size=((1080, 200)), 
                            )
    # Get initial dimensions ONCE for *this* specific TextClip
    initial_w, initial_h = text_clip.size

    # Pass the clean, named function to transform, currying initial_w and initial_h
    animated_text_clip = text_clip.transform(
        lambda get_frame, t: process_bouncing_frame(get_frame, t, initial_w, initial_h)
    )
    return animated_text_clip.with_position("center")


with open("subtitles.srt", "w") as f:
    f.write(subtitles)

try:
    subtitles = SubtitlesClip("subtitles.srt", make_textclip=generator, encoding='utf-8')

    file_name = f"{uuid.uuid4()}_with_sub.mp4"
    image = ColorClip(color=(0,0,0), size=(1080,1920)).with_duration(1)
    video_file = VideoFileClip(video_dir)
    video_file = video_file.resized((1080, 1920))
    video_file = concatenate_videoclips([video_file, image])
    res = CompositeVideoClip([video_file,
                            subtitles.with_position(("center", "center" if int(sub_height * 1920) == 0 else int(sub_height * 1920)))])
    res.write_videofile(file_name, fps=60)

    res.close()
except Exception as e:
    traceback.print_exc()
    print('No sub detected: ', e)



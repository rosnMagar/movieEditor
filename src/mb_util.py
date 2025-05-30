from tkinter import W
import emoji
import re

def snake_case(text):
    return str(text).replace(" ", "_")

def remove_emoji(text):
    return emoji.replace_emoji(text, replace="")

def clean_text_for_tts(text):
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s.,!?;:\'-]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text





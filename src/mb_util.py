from tkinter import W
import emoji

def snake_case(text):
    return str(text).replace(" ", "_")

def remove_emoji(text):
    return emoji.replace_emoji(text, replace="")




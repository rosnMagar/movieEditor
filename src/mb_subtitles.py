import enum
import assemblyai as aai
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')

def generate_subtitles_assemblyai(audio_file):

    # audio_file = "./local_file.mp3"

    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, 
                                     punctuate=True, 
                                     format_text=True)

    transcript = aai.Transcriber(config=config).transcribe(audio_file)
    return transcript.export_subtitles_srt()

def generate_word_level_subtitles_assemblyai(audio_file):

    # audio_file = "./local_file.mp3"

    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, 
                                     punctuate=True, 
                                     format_text=True,
                                     )

    # Transcribe the audio file
    transcript = aai.Transcriber(config=config).transcribe(audio_file)

    srt_lines = []
    words = transcript.words

    for i, word in enumerate(words, start=1):
        start_time = format_timedelta(word.start / 1000)
        end_time = format_timedelta(word.end / 1000)
        text = word.text

        srt_lines.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")

    # to remove the last missing subtitle error
    srt_lines.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")
    return "\n".join(srt_lines)

def format_timedelta(seconds: float) -> str:
    """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
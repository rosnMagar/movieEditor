import assemblyai as aai
import os
from dotenv import load_dotenv

load_dotenv()

aai.settings.api_key = os.getenv('ASSEMBLY_API_KEY')

def generate_subtitles_assemblyai(audio_file):

    # audio_file = "./local_file.mp3"

    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, punctuate=True, format_text=True)

    transcript = aai.Transcriber(config=config).transcribe(audio_file)
    return transcript.export_subtitles_srt()

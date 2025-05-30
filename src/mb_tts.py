# from tiktok_voice import tts, Voice
import os

# from elevenlabs.client import ElevenLabs
# from elevenlabs import VoiceSettings

from TTS.api import TTS
import torch
import traceback
import subprocess
import shlex
import time

from termcolor import colored

# load_dotenv()

# elevenlabs = ElevenLabs(
#   api_key=os.getenv("ELEVENLABS_API_KEY"),
# )


class MB_TTS():
    def __init__(self, dest = "./tmp"):
        self.dest = dest

    def speak(self, text, speaking_speed=1.0):
    # arguments:
    #   - input text
    #   - voice which is used for the audio
    #   - output file name
    #   - play sound after generating the audio


    # Old code using External APIs

        # tts(text, self.voice, self.dest, play_sound=self.play_sound)

        # Define your desired voice settings
        # Increase the speed (e.g., 1.1 for 10% faster, 1.2 for 20% faster)
        # You might need to experiment to find the best value.
        # custom_voice_settings = VoiceSettings(
        #     stability=0.71, # Example value, adjust as needed
        #     similarity_boost=0.5, # Example value, adjust as needed
        #     style=0.0, # Example value, adjust as needed
        #     use_speaker_boost=True, # Example value, adjust as needed
        #     speed=1.2 # Adjust this value to change the speed
        # )

        # audio_stream = elevenlabs.text_to_speech.convert(
        #     text=text,
        #     voice_id="JBFqnCBsd6RMkjVDRZzb",
        #     model_id="eleven_turbo_v2",
        #     output_format="mp3_44100_128",
        #     voice_settings=custom_voice_settings # Pass the custom voice settings here
        # )

        # with open(self.dest, "wb") as f:
        #     for chunk in audio_stream:
        #         if chunk:
        #             f.write(chunk)

        # print(f"Audio saved to {self.dest}")


        # new version using Coqui TTS Self hosted AI Model

        try:
            print("Initializing TTS with model: tts_models/multilingual/multi-dataset/xtts_v2")
            tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True, gpu=False)
            print("TTS model initialized.")

            # output_directory = "tmp"
            # os.makedirs(output_directory, exist_ok=True)
            # output_file_name = f"{self.dest}"
            # output_file_path = os.path.join(output_directory, output_file_name)

            # --- IMPORTANT: Provide a reference audio for the desired male enthusiastic voice ---
            speaker_reference_wav = "./backgrounds/sounds/brian_sample_fast.wav" # <--- CHANGE THIS
            # This file should be a clear recording of a male voice speaking with enthusiasm.

            if not os.path.exists(speaker_reference_wav):
                print(f"ERROR: Speaker reference WAV file not found at '{speaker_reference_wav}'.")
                print("Please provide a valid .wav file for the speaker_wav argument.")
                exit()

            print(f"Using speaker reference: {speaker_reference_wav}")
            print(f"Setting speaking speed to: {speaking_speed}")

            tts.tts_to_file(
                text=text,
                speaker_wav=speaker_reference_wav,
                # language="ja",
                language="en",
                speed=speaking_speed, # Coqui TTS speed parameter
                file_path="./tmp_tts_slow.wav"
            )

            print(colored(f"Coqui TTS audio successfully saved as ./tmp_tts_slow.mp3", "green"))

            # --- CRUCIAL: Give time for file system to release the file ---
            print(colored("DEBUG: Waiting for 2 seconds to ensure file release before FFmpeg...", "yellow"))
            time.sleep(2)
            # -----------------------------------------------------------

            # These are the values that will be used for FFmpeg
            # Ensure 'speaking_speed' here is the one intended for atempo, not necessarily the Coqui one.
            # Based on your previous log, 'speaking_speed' was 1.0 for FFmpeg.
            print(colored(f"DEBUG: 'speaking_speed' for FFmpeg atempo: {speaking_speed}", "cyan"))
            print(colored(f"DEBUG: Output file 'self.dest' for FFmpeg: {self.dest}", "cyan"))
            print(colored("DEBUG: About to prepare FFmpeg command (for Popen)...", "cyan"))

            try:
                command = [
                    'ffmpeg',
                    '-y', # Automatically overwrite output if it exists
                    '-i', "./tmp_tts_slow.wav",
                    '-filter:a', f'atempo={speaking_speed}', # FFmpeg's atempo speed
                    '-vn',
                    self.dest
                ]

                print(colored(f"Executing FFmpeg command (with Popen): {' '.join(shlex.quote(arg) for arg in command)}", "blue"))
                print(colored("DEBUG: Python is NOW about to call subprocess.Popen...", "cyan"))

                # Use Popen
                process = subprocess.Popen(command,
                                           stdout=subprocess.PIPE, # Capture stdout
                                           stderr=subprocess.PIPE, # Capture stderr
                                           text=True) # Decode stdout/stderr as text

                print(colored("DEBUG: Popen has been called. Now calling communicate() with timeout...", "cyan"))

                # process.communicate() waits for the process to complete and gets all output.
                # It's important to use a timeout here as well.
                try:
                    stdout_data, stderr_data = process.communicate(timeout=60) # Timeout in seconds
                    return_code = process.returncode # Get the return code after communicate()

                    print(colored(f"DEBUG: communicate() has returned. FFmpeg Return Code: {return_code}", "cyan"))

                    if return_code == 0:
                        print(colored("FFmpeg process completed successfully (via Popen).", "green"))
                        if stdout_data: # FFmpeg often doesn't use stdout for main info
                            print("STDOUT:", stdout_data)
                        if stderr_data: # FFmpeg logs/info usually go to stderr
                            print(colored("STDERR:", "yellow"), colored(stderr_data, "yellow"))
                        return self.dest
                    else:
                        # FFmpeg returned an error code
                        print(colored(f"Error during FFmpeg processing (Popen). Return code: {return_code}", "red"))
                        if stdout_data:
                            print(colored("FFmpeg STDOUT (on error):", "red"), stdout_data)
                        if stderr_data:
                            print(colored("FFmpeg STDERR (on error):", "red"), stderr_data)
                        return None # Or raise an exception or return a specific error indicator

                except subprocess.TimeoutExpired:
                    print(colored(f"FFmpeg command (Popen) timed out after 60 seconds.", "red"))
                    process.kill()  # Important: kill the lingering process
                    # Try to get any output that was captured before the kill
                    try:
                        # After kill, communicate again (quickly) to gather any final output
                        stdout_data, stderr_data = process.communicate(timeout=5)
                    except Exception as e_comm: # Catch errors during this secondary communicate
                        print(colored(f"Error getting output after Popen timeout/kill: {e_comm}", "red"))
                        stdout_data, stderr_data = "", "" # Default to empty if further errors

                    if stdout_data:
                        print(colored("FFmpeg STDOUT (on timeout):", "red"), stdout_data)
                    if stderr_data:
                        print(colored("FFmpeg STDERR (on timeout):", "red"), stderr_data)
                    return None # Or raise an exception

            except FileNotFoundError:
                print(colored("Error: FFmpeg not found. Please ensure it is installed and in your system's PATH.", "red"))
                return None
            except Exception as e:
                print(colored(f"An unexpected error occurred with Popen/FFmpeg: {e}", "red"))
                # You might want to print the full traceback here for unexpected errors
                import traceback
                traceback.print_exc()
                return None
        except Exception as e:
            print(colored(f"\nAn error occurred with Coqui TTS: {e}", "red"))
            print(colored("This might be due to model download issues, missing dependencies, or configuration.", "red"))
            print(colored("Please check the Coqui TTS documentation for troubleshooting.", "red"))
            print(colored("\nFull traceback:", "red"))
            traceback.print_exc()
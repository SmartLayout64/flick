import edge_tts
from pydub import AudioSegment
from pydub.playback import play
import os
import openai
from pathlib import Path
import flickTools # Assuming this module contains loadSettings()

# Load settings from flickTools. This likely includes preferences for speech speed and volume.
settings = flickTools.loadSettings()

# Initialize the OpenAI client with your API key.
client = openai.OpenAI(api_key="")

def generateFile(speech):
    """
    Generates an MP3 audio file from the given text using OpenAI's Text-to-Speech (TTS) model.
    The generated audio is saved to 'temp/speech.mp3'.

    Args:
        speech (str): The text content to be converted into speech.
    """
    # Call OpenAI's audio speech creation API.
    # 'model="tts-1"' specifies the TTS model to use.
    # 'voice="fable"' selects a specific voice for the speech.
    # 'input=speech' provides the text that will be spoken.
    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=speech
    )

    # Define the output path for the MP3 file.
    output_path = Path("temp/speech.mp3")
    
    # Ensure the 'temp' directory exists.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the audio content received from the API to the MP3 file.
    output_path.write_bytes(response.content)

def playSpeech():
    """
    Plays the 'temp/speech.mp3' audio file.
    Adjusts the playback speed and volume based on settings loaded from flickTools.
    """
    # Load the MP3 audio file into an AudioSegment object.
    sound = AudioSegment.from_mp3("temp/speech.mp3")

    # Calculate the new frame rate based on the 'speed' setting.
    # This effectively changes the playback speed without altering pitch.
    newFrameRate = int(sound.frame_rate * settings["speed"])
    
    # Apply the new frame rate to the audio segment.
    # ._spawn creates a new AudioSegment with the modified raw data and overrides.
    # .set_frame_rate then sets the displayed frame rate to the original for proper playback interpretation
    # by pydub's play function, while the speed change is handled by _spawn's raw data manipulation.
    sound = sound._spawn(sound.raw_data, overrides={"frame_rate": newFrameRate}).set_frame_rate(sound.frame_rate)
    
    # Play the adjusted sound. The 'volumeIncr' setting is added to the sound
    # which adjusts its decibels (volume).
    play(sound + settings["volumeIncr"])
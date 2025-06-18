import sounddevice as sd
import soundfile as sf
import numpy as np
from openai import OpenAI

# Initialize the OpenAI client with your API key.
client = OpenAI(api_key="")

# Define audio recording parameters.
samplerate = 44100  # Samples per second (standard for audio CDs)
channels = 1        # Number of audio channels (1 for mono, 2 for stereo)
defaultFilename = "temp/recording.wav" # Default file path to save recordings

# Global variables to manage the audio stream and recorded frames.
_stream = None      # Will hold the SoundDevice InputStream object
_audioFrames = []   # List to store audio data chunks

def startRecording():
    """
    Starts an audio recording session.
    It initializes an input stream and continuously appends audio data to _audioFrames.
    """
    global _stream, _audioFrames
    _audioFrames = []  # Clear any previous audio frames

    def callback(indata, frames, time, status):
        """
        Callback function for the audio stream.
        This function is called automatically by sounddevice whenever new audio data is available.
        """
        _audioFrames.append(indata.copy()) # Append a copy of the incoming audio data

    # Create an InputStream object with the defined parameters and the callback function.
    _stream = sd.InputStream(callback=callback, channels=channels, samplerate=samplerate)
    _stream.start() # Start the audio stream
    print("STT   | Recording started")

def endRecording(filename=defaultFilename):
    """
    Stops the current recording, saves the recorded audio to a WAV file, and cleans up the stream.

    Args:
        filename (str): The path and name of the file to save the recording.
                        Defaults to "temp/recording.wav".

    Returns:
        str or None: The filename of the saved recording if successful, None otherwise.
    """
    global _stream, _audioFrames
    if _stream: # Check if a recording stream is active
        _stream.stop()  # Stop the audio stream
        _stream.close() # Close the audio stream
        _stream = None  # Reset the stream variable

        # Concatenate all recorded audio frames into a single NumPy array.
        audio = np.concatenate(_audioFrames, axis=0)
        
        # Save the concatenated audio data to a WAV file.
        sf.write(filename, audio, samplerate)
        print(f"STT   | Recording saved to {filename}")
        return filename
    else:
        print("STT   | No active recording to stop")
        return None

def transcribe(filename=defaultFilename):
    """
    Transcribes the audio from a specified WAV file into text using OpenAI's Whisper model.

    Args:
        filename (str): The path and name of the audio file to transcribe.
                        Defaults to "temp/recording.wav".

    Returns:
        str: The transcribed text.
    """
    print("STT   | Transcribing...")
    with open(filename, "rb") as f:
        # Send the audio file to OpenAI's audio transcription API.
        transcript = client.audio.transcriptions.create(
            model="whisper-1", # Specify the Whisper model for transcription
            file=f             # Provide the audio file
        )
    print(f"STT   | You said: {transcript.text}")
    return transcript.text
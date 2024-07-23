import os
import requests
import soundfile as sf
import TTS

from TTS.config import load_config
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer

def download_file(url, filename):
    """
    Download a file from a URL and save it locally
    Args:
        url: str - the url from which you want to download the file
        filename: str - name under which you want to store the file
    Return:
        None
    """
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {filename}")
    else:
        print("Failed to download the file.")


def setupTTS():
    """
    This function initializes the TTS module with the necessary configuration
    Args:
        None
    Return:
        synthesizer: TTS.utils.synthesizer.Synthesizer - this is the synthesizer to be used in the speak function later to convert Text into Audio
    """
    model_path = "tts/best_model.pth"
    config_path = "tts/config.json"
    speakers_file_path = "tts/speakers.pth"

    # first check if best_model.pth exists otherwise download it from hf
    filename = model_path
    file_url = "https://huggingface.co/mbarnig/lb-de-fr-en-pt-coqui-vits-tts/resolve/main/best_model.pth?download=true"

    # check if the file already exists
    if not os.path.exists(filename):
        print(f"{filename} does not exist. Downloading...")
        download_file(file_url, filename)
    else:
        print(f"{filename} already exists.")

    synthesizer = Synthesizer(
        model_path, 
        config_path, 
        speakers_file_path, 
        None, None, None,
    )
    return synthesizer


def speak(synthesizer: TTS.utils.synthesizer.Synthesizer,
          text: str,
          speaker_name: str = "Judith",
          language_name: str ='x-lb'):
    """
    This function uses the synthesizer to generate speech from text
    Args:
        synthesizer: the TTS synthesizer defined by the setupTTS function
        text: the text you want to convert into speech
        speaker_name: the voice you want for your speech, choose a speaker between Judith, Luc, Sara or Charel, Judith is selected by default
        language_name: the language you want to use. It is set to luxembourgish by default

    Returns:
        Nothing is returned and the speech is saved as output.wav
    """
    wavs = synthesizer.tts(
        text, 
        speaker_name,
        language_name
    )
    sf.write('output.wav', wavs, 16000)
    print("Speech generated in speech/output.wav file")
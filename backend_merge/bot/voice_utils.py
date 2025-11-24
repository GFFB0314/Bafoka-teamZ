import os
import logging
import uuid
import whisper
from gtts import gTTS
import requests

LOG = logging.getLogger("voice_utils")
LOG.setLevel(logging.INFO)

# Global model variable to load it once (lazy loading recommended if startup time is critical)
# Available models: tiny, base, small, medium, large
WHISPER_MODEL = None

def get_model():
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        LOG.info("Loading Whisper model 'base'...")
        WHISPER_MODEL = whisper.load_model("base")
        LOG.info("Whisper model loaded.")
    return WHISPER_MODEL

def download_audio(url: str, save_dir: str = "temp_audio") -> str:
    """
    Downloads audio from a URL and saves it locally.
    Returns the path to the saved file.
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Guess extension or default to .ogg (common for WhatsApp)
        ext = ".ogg"
        content_type = response.headers.get("Content-Type", "")
        if "audio/mp4" in content_type:
            ext = ".m4a"
        elif "audio/mpeg" in content_type:
            ext = ".mp3"
        elif "audio/ogg" in content_type:
            ext = ".ogg"
            
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        LOG.info(f"Downloaded audio to {filepath}")
        return filepath
    except Exception as e:
        LOG.error(f"Failed to download audio: {e}")
        raise

def transcribe_audio(filepath: str) -> str:
    """
    Uses local OpenAI Whisper to transcribe audio file to text.
    """
    try:
        model = get_model()
        result = model.transcribe(filepath)
        text = result["text"]
        LOG.info(f"Transcribed text: {text}")
        return text
    except Exception as e:
        LOG.error(f"Transcription failed: {e}")
        raise

def generate_speech(text: str, save_dir: str = "static/audio") -> str:
    """
    Uses gTTS (Google TTS) to generate speech from text.
    Returns the relative path to the audio file (for serving via Flask).
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    try:
        filename = f"response_{uuid.uuid4()}.mp3"
        filepath = os.path.join(save_dir, filename)
        
        # lang='en' by default, can be parameterized if needed
        tts = gTTS(text=text, lang='en')
        tts.save(filepath)
        
        LOG.info(f"Generated speech at {filepath}")
        
        # Return path relative to app root for URL generation
        return f"audio/{filename}" 
    except Exception as e:
        LOG.error(f"TTS generation failed: {e}")
        raise

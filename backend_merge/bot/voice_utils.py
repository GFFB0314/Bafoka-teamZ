# bot/voice_utils.py
import os
import shutil
import subprocess
import uuid
import logging
import whisper
from gtts import gTTS
import requests
import tempfile

LOG = logging.getLogger(__name__)

# Try to find ffmpeg in local dev folder or system PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_LOCAL_BIN = os.path.join(BASE_DIR, "ffmpeg-2025-11-24-git-c732564d2e-essentials_build", "bin")

if os.path.exists(FFMPEG_LOCAL_BIN) and FFMPEG_LOCAL_BIN not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + FFMPEG_LOCAL_BIN

def ensure_ffmpeg_available():
    """Checked if ffmpeg is available."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found in PATH. Please install ffmpeg.")

WHISPER_MODEL = None

def get_model():
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        LOG.info("Loading Whisper model 'base'...")
        WHISPER_MODEL = whisper.load_model("base")
        LOG.info("Whisper model loaded.")
    return WHISPER_MODEL

def download_audio(url: str, save_dir: str) -> str:
    """Download audio from URL to save_dir."""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Determine extension from header or default to .ogg
        ct = response.headers.get("Content-Type", "")
        ext = ".ogg"
        if "audio/mp4" in ct: ext = ".m4a"
        elif "audio/mpeg" in ct: ext = ".mp3"
        elif "audio/wav" in ct: ext = ".wav"
        
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        LOG.info(f"Downloaded audio to {filepath}")
        return filepath
    except Exception as e:
        LOG.error(f"Download failed: {e}")
        raise

def convert_to_wav(input_path: str) -> str:
    """Convert input audio to WAV 16kHz mono (optimal for Whisper)."""
    ensure_ffmpeg_available()
    
    # Create temp wav file
    fd, tmp_wav = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        "-sample_fmt", "s16",
        tmp_wav
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return tmp_wav
    except subprocess.CalledProcessError as e:
        LOG.error(f"FFmpeg conversion failed: {e.stderr.decode()}")
        if os.path.exists(tmp_wav): os.remove(tmp_wav)
        raise

def transcribe_audio(filepath: str) -> str:
    """Transcribe audio file using Whisper."""
    wav_path = None
    try:
        # Optimization: Whisper handles many formats, but explicit conversion ensures consistency
        wav_path = convert_to_wav(filepath)
        model = get_model()
        result = model.transcribe(wav_path)
        return result["text"].strip()
    except Exception as e:
        LOG.error(f"Transcription failed: {e}")
        raise
    finally:
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except: pass

def generate_speech(text: str, save_dir: str) -> str:
    """Generate TTS MP3."""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    try:
        filename = f"response_{uuid.uuid4()}.mp3"
        filepath = os.path.join(save_dir, filename)
        
        # Determine language? Defaulting to English but project implies French/Pidgin context (Cameroon localities)
        # Using 'en' for safety, but 'fr' might be better for names like "Bafoka". 
        # sticking to 'en' as per previous code unless specified.
        tts = gTTS(text=text, lang='en')
        tts.save(filepath)
        
        return filename # caller constructs full URL
    except Exception as e:
        LOG.error(f"TTS failed: {e}")
        raise

import os
import logging
import uuid
import shutil
import subprocess
import tempfile
import whisper
from gtts import gTTS
import requests

LOG = logging.getLogger("voice_utils")
LOG.setLevel(logging.INFO)

# Global model variable to load it once (lazy loading recommended if startup time is critical)
# Available models: tiny, base, small, medium, large
WHISPER_MODEL = None

def ensure_ffmpeg_available():
    """Raise a helpful error if ffmpeg isn't found by Python."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg not found in PATH available to Python. "
            "Make sure ffmpeg is installed and visible to Python. "
            "To test inside Python try:\n"
            ">>> import os; os.system('ffmpeg -version')\n\n"
            "On Windows, add the folder containing ffmpeg.exe (e.g. C:\\ffmpeg\\bin) to your PATH "
            "or set os.environ['PATH'] before calling this script."
        )

def get_model():
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        LOG.info("Loading Whisper model 'base'...")
        WHISPER_MODEL = whisper.load_model("base")
        LOG.info("Whisper model loaded.")
    return WHISPER_MODEL

def convert_to_wav(input_path: str, output_path: str):
    """
    Convert any audio file to WAV (mono, 16kHz, 16-bit PCM) using ffmpeg.
    This format is optimal for speech recognition models like Whisper.
    """
    ensure_ffmpeg_available()
    
    cmd = [
        "ffmpeg",
        "-y",                    # overwrite output if exists
        "-i", input_path,        # input file
        "-ac", "1",              # mono (1 audio channel)
        "-ar", "16000",          # 16 kHz sample rate
        "-sample_fmt", "s16",    # 16-bit PCM
        output_path
    ]
    
    try:
        LOG.info(f"Converting {input_path} to WAV format...")
        result = subprocess.run(
            cmd, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=60  # 60 second timeout for conversion
        )
        LOG.info(f"Successfully converted to {output_path}")
    except subprocess.CalledProcessError as e:
        LOG.error(f"ffmpeg conversion failed. stderr: {e.stderr.decode(errors='ignore')}")
        raise RuntimeError(f"Audio conversion failed: {e.stderr.decode(errors='ignore')}")
    except subprocess.TimeoutExpired:
        LOG.error("ffmpeg conversion timed out")
        raise RuntimeError("Audio conversion timed out after 60 seconds")

def download_audio(url: str, save_dir: str = "temp_audio") -> str:
    """
    Downloads audio from a URL and saves it locally.
    Returns the path to the saved file.
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Guess extension or default to .ogg (common for WhatsApp)
        ext = ".ogg"
        content_type = response.headers.get("Content-Type", "")
        if "audio/mp4" in content_type:
            ext = ".m4a"
        elif "audio/mpeg" in content_type:
            ext = ".mp3"
        elif "audio/ogg" in content_type or "audio/opus" in content_type:
            ext = ".ogg"
        elif "audio/wav" in content_type:
            ext = ".wav"
            
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
    Automatically converts any audio format to WAV using ffmpeg before transcription.
    """
    wav_path = None
    try:
        # Check if input is already WAV, if not convert it
        if not filepath.lower().endswith('.wav'):
            # Create temporary WAV file
            fd, wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)  # close file descriptor, ffmpeg will write the file
            
            # Convert to WAV format
            convert_to_wav(filepath, wav_path)
            transcribe_path = wav_path
        else:
            transcribe_path = filepath
        
        # Load Whisper model and transcribe
        model = get_model()
        LOG.info(f"Transcribing audio from {transcribe_path}...")
        result = model.transcribe(transcribe_path)
        text = result["text"].strip()
        LOG.info(f"Transcribed text: {text}")
        return text
        
    except Exception as e:
        LOG.error(f"Transcription failed: {e}")
        raise
    finally:
        # Cleanup temporary WAV file if it was created
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
                LOG.info(f"Cleaned up temporary WAV file: {wav_path}")
            except Exception as cleanup_error:
                LOG.warning(f"Failed to cleanup temp file {wav_path}: {cleanup_error}")

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

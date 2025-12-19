# bot/services/transcription_service.py
import os
import logging
from bot import voice_utils

LOG = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir

    def process_incoming_audio_url(self, audio_url: str) -> str:
        """
        Download and transcribe audio from a URL.
        """
        try:
            local_path = voice_utils.download_audio(audio_url, self.upload_dir)
            text = voice_utils.transcribe_audio(local_path)
            # Cleanup source file? Maybe keep for debugging.
            return text
        except Exception as e:
            LOG.error(f"Process incoming audio failed: {e}")
            raise

    def generate_response_audio(self, text: str) -> str:
        """
        Generate audio from text and return the relative filename.
        """
        return voice_utils.generate_speech(text, self.upload_dir)

# bot/config.py
import os
from dotenv import load_dotenv

# Load env vars from .env file in the parent directory
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///whatsapp_app.db")
    
    # Bafoka API (Defaults to local fake API)
    BAFOKA_API_URL = os.getenv("BAFOKA_API_URL", "http://localhost:9000")
    BAFOKA_API_KEY = os.getenv("BAFOKA_API_KEY", "")

    # Uploads/Static
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
    AUDIO_UPLOAD_DIR = os.path.join(STATIC_FOLDER, "audio")

    # Twilio (Optional/Legacy)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Dictionary to map environment names to config classes
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
}

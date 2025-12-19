# bot/__init__.py
from flask import Flask
from .db import db
from .config import config_by_name
import os

def create_app(config_name='dev'):
    app = Flask(__name__)
    
    # Load config
    config_cls = config_by_name.get(config_name, config_by_name['dev'])
    app.config.from_object(config_cls)

    # Initialize extensions
    db.init_app(app)
    
    # Ensure static/audio directories exist
    os.makedirs(app.config['AUDIO_UPLOAD_DIR'], exist_ok=True)

    # Register Blueprints
    from .routes.botpress_routes import botpress_bp
    app.register_blueprint(botpress_bp)

    with app.app_context():
        # Create tables for dev (In prod, use Alembic)
        db.create_all()

    return app

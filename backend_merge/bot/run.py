# bot/run.py
import os
import sys

# Add parent directory to path to allow running as script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot import create_app

# Default to dev environment
env_name = os.getenv('FLASK_ENV', 'dev')
app = create_app(env_name)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting Bafoka Bot on port {port} ({env_name} mode)...")
    app.run(host="0.0.0.0", port=port)

import os
from bot.fake_bafoka import app as bafoka_app

if __name__ == "__main__":
    bafoka_app.run(host="0.0.0.0", port=int(os.getenv("BAFOKA_PORT", 9000)), debug=True)


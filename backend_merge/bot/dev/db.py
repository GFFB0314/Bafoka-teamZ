# dev/db.py
# Separate SQLAlchemy instance for the dev backend. Does not share with bot/db.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

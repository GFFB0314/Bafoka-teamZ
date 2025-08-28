# Ensures project root is on sys.path so that `import app` etc. work
import os
import sys

# Add parent directory of this tests/ folder to sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


"""Make the tests runnable from the project folder (python -m pytest modular/tests) or from modular/."""
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

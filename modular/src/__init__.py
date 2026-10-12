import sys
from pathlib import Path

# The saved model was built with the `training` package, which lives next to this app's folder in the project root.
# Put the project root on the import path so the model can be loaded, whichever folder the app is started from.
import os

APP_DIR = Path(__file__).resolve().parent.parent
ROOT = Path(os.getenv("TELECOM_PROJECT_ROOT", APP_DIR.parent)).resolve()
for p in (str(ROOT), str(APP_DIR)):      # app folder first, so `src` and `views` always resolve to this app
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

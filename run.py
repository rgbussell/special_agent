import chainlit as cl

# This makes Python treat the current folder as a package
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Now run the real app
from ui.app import *  # noqa

# set up the data directories
os.makedirs("data/inbox", exist_ok=True)
os.makedirs("data/vector_db", exist_ok=True)

# This is the magic line that actually starts Chainlit
cl.run_app("ui/app.py")
from dotenv import load_dotenv

from pathlib import Path

import os

BASE_DIR = Path(__file__).parent.parent.parent

# reading ./deployment/example.env file
load_dotenv(os.path.join(BASE_DIR, 'deployment', 'example.env'))

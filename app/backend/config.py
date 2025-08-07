import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# HMM model directory and file
HMM_MODEL_DIR = os.getenv("HMM_MODEL_DIR", os.path.join(os.path.dirname(__file__), "..", "data", "concatenated"))
HMM_MODEL_FILE = os.getenv("HMM_MODEL_FILE", "all_germlines.hmm")

# Add other config constants as needed


import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# HMM model directory and file
# Path relative to project root - try different levels for different environments
# Local: backend is at app/backend/, need to go up two levels to project root
# Docker: backend is at /app/backend/, need to go up one level to /app/
def find_project_root():
    current_dir = os.path.dirname(__file__)
    # Try one level up first (Docker)
    one_level_up = os.path.join(current_dir, "..")
    if os.path.exists(os.path.join(one_level_up, "data")):
        return one_level_up
    # Try two levels up (local)
    two_levels_up = os.path.join(current_dir, "..", "..")
    if os.path.exists(os.path.join(two_levels_up, "data")):
        return two_levels_up
    # Fallback to one level up
    return one_level_up

PROJECT_ROOT = find_project_root()
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# Concatenated HMM for all germlines
HMM_MODEL_DIR = os.getenv("HMM_MODEL_DIR", os.path.join(DATA_DIR, "concatenated"))
HMM_MODEL_FILE = os.getenv("HMM_MODEL_FILE", "all_germlines.hmm")
HMM_MODEL_PATH = os.path.join(HMM_MODEL_DIR, HMM_MODEL_FILE)

# Individual isotype HMMs
ISOTYPE_HMM_DIR = os.getenv("ISOTYPE_HMM_DIR", os.path.join(DATA_DIR, "isotype_hmms"))

# Add other config constants as needed

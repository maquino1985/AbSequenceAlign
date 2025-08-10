import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Data directory - use environment variable with fallback
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "data"))

# Concatenated HMM for all germlines
HMM_MODEL_DIR = os.getenv("HMM_MODEL_DIR", os.path.join(DATA_DIR, "concatenated"))
HMM_MODEL_FILE = os.getenv("HMM_MODEL_FILE", "all_germlines.hmm")
HMM_MODEL_PATH = os.path.join(HMM_MODEL_DIR, HMM_MODEL_FILE)

# Individual isotype HMMs
ISOTYPE_HMM_DIR = os.getenv("ISOTYPE_HMM_DIR", os.path.join(DATA_DIR, "isotype_hmms"))

# Add other config constants as needed

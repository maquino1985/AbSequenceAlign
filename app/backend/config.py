import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Data directory - use environment variable with fallback
DATA_DIR = os.getenv(
    "DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "data")
)

# Concatenated HMM for all germlines
HMM_MODEL_DIR = os.getenv(
    "HMM_MODEL_DIR", os.path.join(DATA_DIR, "concatenated")
)
HMM_MODEL_FILE = os.getenv("HMM_MODEL_FILE", "all_germlines.hmm")
HMM_MODEL_PATH = os.path.join(HMM_MODEL_DIR, HMM_MODEL_FILE)

# Individual isotype HMMs
ISOTYPE_HMM_DIR = os.getenv(
    "ISOTYPE_HMM_DIR", os.path.join(DATA_DIR, "isotype_hmms")
)

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5433"))
DB_NAME = os.getenv("DB_NAME", "absequencealign_dev")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Database Pool Configuration
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "30"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Database Logging
DB_ECHO = os.getenv("DB_ECHO", "true").lower() == "true"
DB_ECHO_POOL = os.getenv("DB_ECHO_POOL", "false").lower() == "true"

# Add other config constants as needed

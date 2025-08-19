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

from pathlib import Path

# BLAST and IgBLAST Configuration
BLAST_DB_DIR = Path(os.getenv("BLAST_DB_DIR", os.path.join(DATA_DIR, "blast")))
IGBLAST_DB_DIR = Path(
    os.getenv("IGBLAST_DB_DIR", os.path.join(DATA_DIR, "igblast"))
)
IGBLAST_INTERNAL_DATA_DIR = Path(
    os.getenv(
        "IGBLAST_INTERNAL_DATA_DIR",
        os.path.join(IGBLAST_DB_DIR, "internal_data"),
    )
)
IGBLAST_OPTIONAL_FILE_DIR = Path(
    os.getenv(
        "IGBLAST_OPTIONAL_FILE_DIR",
        os.path.join(IGBLAST_DB_DIR, "optional_file"),
    )
)

# IgBLAST Database Paths
IGBLAST_HUMAN_V_DB = Path(
    os.getenv(
        "IGBLAST_HUMAN_V_DB",
        os.path.join(IGBLAST_INTERNAL_DATA_DIR, "human", "airr_c_human_ig.V"),
    )
)
IGBLAST_HUMAN_D_DB = Path(
    os.getenv(
        "IGBLAST_HUMAN_D_DB",
        os.path.join(IGBLAST_INTERNAL_DATA_DIR, "human", "airr_c_human_igh.D"),
    )
)
IGBLAST_HUMAN_J_DB = Path(
    os.getenv(
        "IGBLAST_HUMAN_J_DB",
        os.path.join(IGBLAST_INTERNAL_DATA_DIR, "human", "airr_c_human_ig.J"),
    )
)
IGBLAST_HUMAN_C_DB = Path(
    os.getenv(
        "IGBLAST_HUMAN_C_DB",
        os.path.join(IGBLAST_INTERNAL_DATA_DIR, "ncbi_human_c_genes"),
    )
)


# Generic IgBLAST database path patterns
def get_igblast_v_db_path(organism: str) -> Path:
    """Get V gene database path for organism"""
    if organism == "human":
        return IGBLAST_HUMAN_V_DB
    # For mouse and other organisms, use the gl_ prefix pattern
    return IGBLAST_INTERNAL_DATA_DIR / organism / f"{organism}_gl_V"


def get_igblast_d_db_path(organism: str) -> Path:
    """Get D gene database path for organism"""
    if organism == "human":
        return IGBLAST_HUMAN_D_DB
    # For mouse and other organisms, use the gl_ prefix pattern
    return IGBLAST_INTERNAL_DATA_DIR / organism / f"{organism}_gl_D"


def get_igblast_j_db_path(organism: str) -> Path:
    """Get J gene database path for organism"""
    if organism == "human":
        return IGBLAST_HUMAN_J_DB
    # For mouse and other organisms, use the gl_ prefix pattern
    return IGBLAST_INTERNAL_DATA_DIR / organism / f"{organism}_gl_J"


def get_igblast_c_db_path(organism: str) -> Path:
    """Get C gene database path for organism"""
    if organism == "human":
        return IGBLAST_HUMAN_C_DB
    elif organism == "mouse":
        # Use the newly created mouse C gene database
        return IGBLAST_INTERNAL_DATA_DIR / "mouse_c_genes"
    # For other organisms, use the gl_ prefix pattern
    return IGBLAST_INTERNAL_DATA_DIR / f"ncbi_{organism}_c_genes"


# BLAST Database Name Mappings
# Maps logical database names to actual BLAST database names
BLAST_DB_NAME_MAPPINGS = {
    "human_genome": "GCF_000001405.39_top_level",
    "mouse_genome": "GCF_000001635.27_top_level",
    "refseq_select_rna": "refseq_select_rna",
    "16S_ribosomal_RNA": "16S_ribosomal_RNA",
    "swissprot": "swissprot",
    "pdb": "pdb",
}


def get_blast_db_name(logical_name: str) -> str:
    """Get the actual BLAST database name from logical name"""
    return BLAST_DB_NAME_MAPPINGS.get(logical_name, logical_name)

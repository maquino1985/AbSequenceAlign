import os
import subprocess
from typing import Optional

def detect_isotype_with_hmmer(sequence: str, hmm_dir: str = "data/isotype_hmms") -> Optional[str]:
    """
    Detect antibody isotype using HMMER against isotype HMMs.
    Args:
        sequence: Amino acid sequence (FASTA format or raw string)
        hmm_dir: Directory containing isotype HMMs
    Returns:
        Best-matching isotype (e.g., 'IGHG1', 'IGHA1', etc.) or None if no confident match
    """
    import tempfile
    import shutil

    # Write sequence to temp FASTA
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".fasta") as fasta:
        fasta.write(">query\n" + sequence + "\n")
        fasta_path = fasta.name

    best_isotype = None
    best_score = float("-inf")
    best_evalue = float("inf")

    try:
        for hmmfile in os.listdir(hmm_dir):
            if hmmfile.endswith(".hmm"):
                hmm_path = os.path.join(hmm_dir, hmmfile)
                with tempfile.NamedTemporaryFile("r", delete=False, suffix=".tblout") as tblout_file:
                    tblout_path = tblout_file.name
                cmd = [
                    "hmmsearch",
                    "--noali",
                    "--tblout", tblout_path,
                    hmm_path,
                    fasta_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                # Read tblout file
                with open(tblout_path, "r") as tbl:
                    for line in tbl:
                        if line.startswith("#") or not line.strip():
                            continue
                        fields = line.split()
                        if len(fields) < 6:
                            continue
                        target = hmmfile.replace(".hmm", "")
                        try:
                            evalue = float(fields[4])
                            score = float(fields[5])
                        except ValueError:
                            continue
                        if score > best_score or (score == best_score and evalue < best_evalue):
                            best_score = score
                            best_evalue = evalue
                            best_isotype = target
                        break  # Only consider the top hit per HMM
                os.unlink(tblout_path)
    finally:
        os.unlink(fasta_path)
    return best_isotype

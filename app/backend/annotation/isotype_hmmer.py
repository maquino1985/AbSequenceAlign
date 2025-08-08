import os
import subprocess
from typing import Optional
from backend.config import ISOTYPE_HMM_DIR


def detect_isotype_with_hmmer(sequence: str, hmm_dir: str = None) -> Optional[str]:
    """
    Detect antibody isotype using HMMER against isotype HMMs.
    Args:
        sequence: Amino acid sequence (FASTA format or raw string)
        hmm_dir: Directory containing isotype HMMs (defaults to config ISOTYPE_HMM_DIR)
    Returns:
        Best-matching isotype (e.g., 'IGHG1', 'IGHA1', etc.) or None if no confident match
    """
    import tempfile
    
    # Use default HMM directory from config if not specified
    if hmm_dir is None:
        hmm_dir = ISOTYPE_HMM_DIR

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
                cmd = [
                    "hmmsearch",
                    "--noali",
                    # "--tblout=-",
                    hmm_path,
                    fasta_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                target = ""
                tblout = result.stdout
                for tbloutline in tblout.splitlines():
                    if tbloutline.startswith("#") or not tbloutline.strip():
                        continue
                    fields = tbloutline.split()

                    if fields[0] == "Query:":
                        # Extract the target name from fields[1] (should end with .aln or .ALN)
                        target = fields[1]
                        if target.lower().endswith('.aln'):
                            target = target[:-4]
                        continue
                    elif len(fields) < 6:
                        continue
                    # Use full sequence score/E-value (fields[0]=E-value, fields[1]=score)
                    try:
                        # full sequence
                        evalue = float(fields[0])
                        score = float(fields[1])
                        # best 1 domain
                        # evalue = float(fields[3])
                        # score = float(fields[4])
                    except ValueError:
                        continue
                    if score > best_score or (score == best_score and evalue < best_evalue):
                        best_score = score
                        best_evalue = evalue
                        best_isotype = target
    finally:
        os.unlink(fasta_path)
    return best_isotype

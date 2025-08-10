import os
import subprocess

import pytest
from backend.annotation.isotype_hmmer import detect_isotype_with_hmmer
from backend.config import ISOTYPE_HMM_DIR
from backend.logger import logger

hmm_dir = ISOTYPE_HMM_DIR
# Canonical constant region sequences for each isotype (truncated for test)
ISOTYPE_SEQS = {
    "IGHG1": "GQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK",
    "IGHG2": "APPVAGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVQFNWYVDGVEVHNAKTKPREEQFNSTFRVVSVLTVVHQDWLNGKEYKCKVSNKGLPAPIEKTISKTK",
    "IGHG3": "ASTKGPSVFPLAPCSRSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYTCNVNHKPSNTKVDKRV",
    "IGHG4": "APEFLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSQEDPEVQFNWYVDGVEVHNAKTKPREEQFNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKGLPSSIEKTISKAK",
    "IGHA1": "GNTFRPEVHLLPPPSEELALNELVTLTCLARGFSPKDVLVRWLQGSQELPREKYLTWASRQEPSQGTTTFAVTSILRVAAEDWKKGDTFSCMVGHEALPLAFTQKTIDRLAGKPTHVNVSVVMAEVDGTCY",
    "IGHA2": "VPPPPPCCHPRLSLHRPALEDLLLGSEANLTCTLTGLRDASGATFTWTPSSGKSAVQGPPERDLCGCYSVSSVLPGCAQPWNHGETFTCTAAHPELKTPLTANITKS",
    "IGHM": "GSASAPTLFPLVSCENSPSDTSSVAVGCLAQDFLPDSITLSWKYKNNSDISSTRGFPSVLRGGKYAATSQVLLPSKDVMQGTDEHVVCKVQHPNGNKEKNVPLP",
    "IGHD": "AAQAPVKLSLNLLASSDPPEAASWLLCEVSGFSPPNILLMWLEDQREVNTSGFAPARPPPQPGSTTFWAWSVLRVPAPPSPQPATYTCVVSHEDSRTLLNASRSLEVS",
    "IGHE": "GPRAAPEVYAFATPEGPGSRDKRTLACLIQNFMPEDISVQWLHNEVQLPDARHSTTQPRKTKGSGFFVFSRLEVTRAEWEQKDEFICRAVHEAASPSQTVQRAVSVNPGK",
}


@pytest.mark.parametrize("isotype,seq", ISOTYPE_SEQS.items())
def test_hmmer_isotype_detection(isotype, seq):
    # hmm_dir = os.path.join(os.path.dirname(__file__), "..", "data", "isotype_hmms")
    detected = detect_isotype_with_hmmer(seq, hmm_dir=hmm_dir)
    assert detected is not None, f"No isotype detected for {isotype}"
    assert detected.upper() == isotype.upper(), f"Expected {isotype}, got {detected}"


def test_hmmer_isotype_detection_debug():
    # Use a canonical IgG1 constant region sequence
    # >S71043|IGHA2*03|Homo sapiens|F|CH3-CHS|g,1170..1561|393 nt|1|+1| | |131 AA|131+0=131| | |
    KIH_SEQ = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCARDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK"

    # hmm_dir = os.path.join(os.path.dirname(__file__), "..", "data", "concatenated")
    # Run HMMER manually and log output
    import tempfile

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".fasta") as fasta:
        fasta.write(">query\n" + KIH_SEQ + "\n")
        fasta_path = fasta.name
    try:
        for hmmfile in os.listdir(hmm_dir):
            if hmmfile.endswith(".hmm"):
                hmm_path = os.path.join(hmm_dir, hmmfile)
                cmd = [
                    "hmmsearch",
                    "--noali",
                    # "--tblout=-",
                    hmm_path,
                    fasta_path,
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                logger.debug(f"\nHMM: {hmmfile}")
                logger.debug("--- HMMER tblout ---")
                logger.debug(result.stdout)
                logger.debug("--- stderr ---")
                logger.debug(result.stderr)
    finally:
        os.unlink(fasta_path)
    # Also run the detection function and print the result
    detected = detect_isotype_with_hmmer(KIH_SEQ, hmm_dir=hmm_dir)
    logger.debug(f"\nBest detected isotype: {detected}")
    assert detected == "IGHG1", f"got {detected}"

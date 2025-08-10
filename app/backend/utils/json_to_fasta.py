"""
Utility functions for converting JSON sequence formats to FASTA
"""

from typing import Dict, List, Any


def json_seqs_to_fasta(
    json_sequences: List[Dict[str, Any]], sequence_name: str = None
) -> str:
    """
    Convert JSON sequences to FASTA format.

    Args:
        json_sequences: List of dictionaries containing sequence data
                       Each dict should have a 'name' field and chain labels as keys
        sequence_name: Optional name prefix for the FASTA headers
                      If None, uses the sequence name from the JSON

    Returns:
        FASTA format string with chain labels as headers and sequences as content

    Example:
        Input:
        [
            {
                "name": "igg_test",
                "heavy_chain": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                "light_chain": "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK"
            }
        ]

        Output:
        >igg_test_heavy_chain
        EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS
        >igg_test_light_chain
        DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK
    """
    fasta_lines = []

    for seq_data in json_sequences:
        # Get the sequence name
        seq_name = seq_data.get("name", "unknown")

        # Get all fields except 'name' as chain data
        chain_data = {k: v for k, v in seq_data.items() if k != "name"}

        for chain_label, sequence in chain_data.items():
            # Create FASTA header: sequence_name_chain_label
            header = f"{seq_name}_{chain_label}"

            # Add header
            fasta_lines.append(f">{header}")

            # Add sequence as single line
            fasta_lines.append(sequence)

    return "\n".join(fasta_lines)


def json_seqs_to_fasta_simple(json_sequences: List[Dict[str, Any]]) -> str:
    """
    Convert JSON sequences to FASTA format with simple chain labels as headers.

    Args:
        json_sequences: List of dictionaries containing sequence data
                       Each dict should have chain labels as keys and sequences as values

    Returns:
        FASTA format string with chain labels as headers and sequences as content

    Example:
        Input:
        {
            "heavy_chain_1": "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS",
            "light_chain_1": "DIQLTQSPGTLSLSPGERATLSCRASQSVSTYLAWYQKKPGQAPRLLIYGASKRATGIPDRFSGSGSGTDFTLTISRLEPEDFAVYYCQQYGDSPLTFGQGTKVEIK"
        }

        Output:
        >heavy_chain_1
        ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS
        >light_chain_1
        DIQLTQSPGTLSLSPGERATLSCRASQSVSTYLAWYQKKPGQAPRLLIYGASKRATGIPDRFSGSGSGTDFTLTISRLEPEDFAVYYCQQYGDSPLTFGQGTKVEIK
    """
    fasta_lines = []

    for chain_label, sequence in json_sequences.items():
        # Add header
        fasta_lines.append(f">{chain_label}")

        # Add sequence as single line
        fasta_lines.append(sequence)

    return "\n".join(fasta_lines)

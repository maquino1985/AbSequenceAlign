"""
AIRR Format Parser for IgBLAST Output

This module provides comprehensive parsing of IgBLAST AIRR format output (outfmt 19),
extracting all rearrangement data including gene assignments, CDR regions, alignments,
and quality metrics.
"""

import logging
from typing import Dict, Any

from backend.infrastructure.adapters.base_parser import BaseIgBlastParser


class AIRRParser(BaseIgBlastParser):
    """Parser for IgBLAST AIRR format output (outfmt 19)."""

    def __init__(self):
        """Initialize the AIRR parser."""
        super().__init__()
        self._logger = logging.getLogger(__name__)

    def parse(self, output: str, blast_type: str) -> Dict[str, Any]:
        """Parse IgBLAST AIRR format output (outfmt 19)."""
        result = {
            "blast_type": blast_type,
            "query_info": {},
            "hits": [],
            "analysis_summary": {},
            "total_hits": 0,
            "airr_data": {},
        }

        if not output.strip():
            return result

        lines = output.strip().split("\n")

        # Find the header line to get column names
        header_line = None
        data_lines = []

        for line in lines:
            if line.startswith("sequence_id\t"):
                header_line = line
            elif (
                line
                and not line.startswith("#")
                and not line.startswith("Warning:")
            ):
                data_lines.append(line)

        if not header_line or not data_lines:
            return result

        # Parse header to get column indices
        headers = header_line.strip().split("\t")

        # Parse data lines
        for line in data_lines:
            if not line.strip():
                continue

            parts = line.strip().split("\t")
            if len(parts) < len(headers):
                continue

            # Create a dictionary from headers and values
            airr_record = dict(zip(headers, parts))

            # Extract comprehensive information from AIRR record
            hit = self._extract_hit_data(airr_record)
            # Add missing fields that are expected by the frontend
            if airr_record.get("v_identity"):
                hit["percent_identity"] = float(
                    airr_record.get("v_identity", 0)
                )
            if airr_record.get("v_score"):
                hit["bit_score"] = float(airr_record.get("v_score", 0))
            # Calculate alignment length from V gene positions
            if airr_record.get("v_sequence_start") and airr_record.get(
                "v_sequence_end"
            ):
                v_start = int(airr_record.get("v_sequence_start", 0))
                v_end = int(airr_record.get("v_sequence_end", 0))
                hit["alignment_length"] = v_end - v_start + 1
            # Set a default evalue (AIRR format doesn't provide this)
            hit["evalue"] = 0.0

            result["hits"].append(hit)
            result["airr_data"] = airr_record

        result["total_hits"] = len(result["hits"])

        # Extract comprehensive summary information from first hit
        if result["hits"]:
            first_hit = result["hits"][0]
            result["analysis_summary"] = self._extract_summary_data(first_hit)

        return result

    def _extract_hit_data(self, airr_record: Dict[str, str]) -> Dict[str, Any]:
        """Extract hit data from AIRR record."""
        return {
            "v_call": airr_record.get("v_call"),
            "d_call": airr_record.get("d_call"),
            "j_call": airr_record.get("j_call"),
            "locus": airr_record.get("locus"),
            "productive": airr_record.get("productive"),
            "stop_codon": airr_record.get("stop_codon"),
            "vj_in_frame": airr_record.get("vj_in_frame"),
            "complete_vdj": airr_record.get("complete_vdj"),
            "rev_comp": airr_record.get("rev_comp"),
            # CDR3 and junction information
            "cdr3": airr_record.get("cdr3"),
            "cdr3_start": airr_record.get("cdr3_start"),
            "cdr3_end": airr_record.get("cdr3_end"),
            "junction": airr_record.get("junction"),
            "junction_length": airr_record.get("junction_length"),
            "junction_aa": airr_record.get("junction_aa"),
            "junction_aa_length": airr_record.get("junction_aa_length"),
            # Framework and CDR regions
            "fwr1": airr_record.get("fwr1"),
            "fwr1_aa": airr_record.get("fwr1_aa"),
            "cdr1": airr_record.get("cdr1"),
            "cdr1_aa": airr_record.get("cdr1_aa"),
            "fwr2": airr_record.get("fwr2"),
            "fwr2_aa": airr_record.get("fwr2_aa"),
            "cdr2": airr_record.get("cdr2"),
            "cdr2_aa": airr_record.get("cdr2_aa"),
            "fwr3": airr_record.get("fwr3"),
            "fwr3_aa": airr_record.get("fwr3_aa"),
            "fwr4": airr_record.get("fwr4"),
            "fwr4_aa": airr_record.get("fwr4_aa"),
            # Alignment information
            "v_identity": float(airr_record.get("v_identity", 0.0)),
            "j_identity": float(airr_record.get("j_identity", 0.0)),
            "d_identity": float(airr_record.get("d_identity", 0.0)),
            "v_score": float(airr_record.get("v_score", 0.0)),
            "j_score": float(airr_record.get("j_score", 0.0)),
            # Sequence alignments
            "sequence_alignment": airr_record.get("sequence_alignment"),
            "germline_alignment": airr_record.get("germline_alignment"),
            "sequence_alignment_aa": airr_record.get("sequence_alignment_aa"),
            "germline_alignment_aa": airr_record.get("germline_alignment_aa"),
            # V/D/J specific alignments
            "v_sequence_alignment": airr_record.get("v_sequence_alignment"),
            "v_sequence_alignment_aa": airr_record.get(
                "v_sequence_alignment_aa"
            ),
            "v_germline_alignment": airr_record.get("v_germline_alignment"),
            "v_germline_alignment_aa": airr_record.get(
                "v_germline_alignment_aa"
            ),
            "d_sequence_alignment": airr_record.get("d_sequence_alignment"),
            "d_sequence_alignment_aa": airr_record.get(
                "d_sequence_alignment_aa"
            ),
            "d_germline_alignment": airr_record.get("d_germline_alignment"),
            "d_germline_alignment_aa": airr_record.get(
                "d_germline_alignment_aa"
            ),
            "j_sequence_alignment": airr_record.get("j_sequence_alignment"),
            "j_sequence_alignment_aa": airr_record.get(
                "j_sequence_alignment_aa"
            ),
            "j_germline_alignment": airr_record.get("j_germline_alignment"),
            "j_germline_alignment_aa": airr_record.get(
                "j_germline_alignment_aa"
            ),
            # Position information
            "v_sequence_start": airr_record.get("v_sequence_start"),
            "v_sequence_end": airr_record.get("v_sequence_end"),
            "v_germline_start": airr_record.get("v_germline_start"),
            "v_germline_end": airr_record.get("v_germline_end"),
            "d_sequence_start": airr_record.get("d_sequence_start"),
            "d_sequence_end": airr_record.get("d_sequence_end"),
            "d_germline_start": airr_record.get("d_germline_start"),
            "d_germline_end": airr_record.get("d_germline_end"),
            "j_sequence_start": airr_record.get("j_sequence_start"),
            "j_sequence_end": airr_record.get("j_sequence_end"),
            "j_germline_start": airr_record.get("j_germline_start"),
            "j_germline_end": airr_record.get("j_germline_end"),
            # Framework and CDR positions
            "fwr1_start": airr_record.get("fwr1_start"),
            "fwr1_end": airr_record.get("fwr1_end"),
            "cdr1_start": airr_record.get("cdr1_start"),
            "cdr1_end": airr_record.get("cdr1_end"),
            "fwr2_start": airr_record.get("fwr2_start"),
            "fwr2_end": airr_record.get("fwr2_end"),
            "cdr2_start": airr_record.get("cdr2_start"),
            "cdr2_end": airr_record.get("cdr2_end"),
            "fwr3_start": airr_record.get("fwr3_start"),
            "fwr3_end": airr_record.get("fwr3_end"),
            "fwr4_start": airr_record.get("fwr4_start"),
            "fwr4_end": airr_record.get("fwr4_end"),
            # CIGAR strings
            "v_cigar": airr_record.get("v_cigar"),
            "d_cigar": airr_record.get("d_cigar"),
            "j_cigar": airr_record.get("j_cigar"),
        }

    def _extract_summary_data(self, hit: Dict[str, Any]) -> Dict[str, Any]:
        """Extract summary data from hit."""
        return {
            "v_gene": hit["v_call"],
            "d_gene": hit["d_call"],
            "j_gene": hit["j_call"],
            "chain_type": hit["locus"],
            "productive": hit["productive"],
            "cdr3_sequence": hit["cdr3"],
            "cdr3_start": hit["cdr3_start"],
            "cdr3_end": hit["cdr3_end"],
            "junction": hit["junction"],
            "junction_length": hit["junction_length"],
            "v_identity": hit["v_identity"],
            "j_identity": hit["j_identity"],
            "d_identity": hit["d_identity"],
            "stop_codon": hit["stop_codon"],
            "vj_in_frame": hit["vj_in_frame"],
            "complete_vdj": hit["complete_vdj"],
        }

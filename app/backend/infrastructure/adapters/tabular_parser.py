"""
Tabular Format Parser for IgBLAST Output

This module provides parsing of IgBLAST tabular output (outfmt 7),
extracting hit information, gene assignments, and CDR3 data.
"""

import logging
import re
from typing import Dict, Any, List

from backend.infrastructure.adapters.base_parser import BaseIgBlastParser


class TabularParser(BaseIgBlastParser):
    """Parser for IgBLAST tabular output (outfmt 7)."""

    def __init__(self):
        """Initialize the tabular parser."""
        super().__init__()
        self._logger = logging.getLogger(__name__)

    def parse(self, output: str, blast_type: str) -> Dict[str, Any]:
        """Parse IgBLAST tabular output (outfmt 7)."""
        result = {
            "blast_type": blast_type,
            "query_info": {},
            "hits": [],
            "analysis_summary": {},
            "total_hits": 0,
        }

        if not output.strip():
            return result

        lines = output.strip().split("\n")

        for idx, line in enumerate(lines):
            if line.startswith("#"):
                # Parse header information
                if "Query:" in line:
                    result["query_info"]["query_id"] = line.split("Query:")[
                        1
                    ].strip()
                elif "Database:" in line:
                    result["query_info"]["database"] = line.split("Database:")[
                        1
                    ].strip()
                elif "Sub-region sequence details" in line:
                    # Look for CDR3 line in the next few lines
                    for i in range(idx + 1, min(idx + 5, len(lines))):
                        if lines[i].startswith("CDR3") and not lines[
                            i
                        ].startswith("#"):
                            cdr3_data = self._extract_cdr3_data_from_subregion(
                                lines[i]
                            )
                            if cdr3_data:
                                result["analysis_summary"].update(cdr3_data)
                            break
                continue

            if (
                line.strip().startswith("V")
                or line.strip().startswith("D")
                or line.strip().startswith("J")
            ) and "query" in line:
                # Parse hit information
                parts = line.split()
                if len(parts) >= 14:
                    hit = self._extract_hit_data(parts)
                    hit["subject_url"] = self._get_subject_url(
                        hit["subject_id"]
                    )
                    result["hits"].append(hit)

            elif "V-(D)-J rearrangement summary" in line:
                # Parse rearrangement summary
                next_line = lines[idx + 1] if (idx + 1) < len(lines) else ""
                if next_line and not next_line.startswith("#"):
                    parts = next_line.split("\t")
                    if len(parts) >= 8:
                        result["analysis_summary"] = (
                            self._extract_summary_data(parts)
                        )

            elif "CDR3" in line and "junction details" in line:
                # Parse CDR3 information
                next_line = lines[idx + 1] if (idx + 1) < len(lines) else ""
                if next_line and not next_line.startswith("#"):
                    cdr3_data = self._extract_cdr3_data(next_line)
                    if cdr3_data:
                        result["analysis_summary"].update(cdr3_data)
                        # Also add CDR3 info to all hits
                        for hit in result["hits"]:
                            hit.update(cdr3_data)

        result["total_hits"] = len(result["hits"])

        # If no analysis summary was found, try to extract from hits
        if not result["analysis_summary"] and result["hits"]:
            result["analysis_summary"] = self._extract_summary_from_hits(
                result["hits"]
            )

        # Add CDR3 data to all hits if available
        if result["analysis_summary"].get("cdr3_sequence") and result["hits"]:
            cdr3_data = {
                "cdr3_sequence": result["analysis_summary"].get(
                    "cdr3_sequence"
                ),
                "cdr3_aa": result["analysis_summary"].get("cdr3_aa"),
                "cdr3_start": result["analysis_summary"].get("cdr3_start"),
                "cdr3_end": result["analysis_summary"].get("cdr3_end"),
            }
            for hit in result["hits"]:
                hit.update(cdr3_data)

        return result

    def _extract_hit_data(self, parts: List[str]) -> Dict[str, Any]:
        """Extract hit data from tabular line parts."""
        hit_type = parts[0]
        query_id = parts[1]
        subject_id = parts[2]
        percent_identity = float(parts[3]) if parts[3] != "N/A" else None
        alignment_length = int(parts[4]) if parts[4] != "N/A" else None
        mismatches = int(parts[5]) if parts[5] != "N/A" else None
        gap_opens = int(parts[6]) if parts[6] != "N/A" else None
        gaps = int(parts[7]) if parts[7] != "N/A" else None
        q_start = int(parts[8]) if parts[8] != "N/A" else None
        q_end = int(parts[9]) if parts[9] != "N/A" else None
        s_start = int(parts[10]) if parts[10] != "N/A" else None
        s_end = int(parts[11]) if parts[11] != "N/A" else None
        evalue = float(parts[12]) if parts[12] != "N/A" else None
        bit_score = float(parts[13]) if parts[13] != "N/A" else None

        hit = {
            "hit_type": hit_type,
            "query_id": query_id,
            "subject_id": subject_id,
            "percent_identity": percent_identity,
            "alignment_length": alignment_length,
            "mismatches": mismatches,
            "gap_opens": gap_opens,
            "gaps": gaps,
            "q_start": q_start,
            "q_end": q_end,
            "s_start": s_start,
            "s_end": s_end,
            "evalue": evalue,
            "bit_score": bit_score,
        }

        # Add gene information based on hit type
        if hit_type == "V":
            hit["v_gene"] = subject_id
            hit["chain_type"] = self._extract_chain_type(subject_id)
        elif hit_type == "D":
            hit["d_gene"] = subject_id
        elif hit_type == "J":
            hit["j_gene"] = subject_id

        return hit

    def _extract_summary_data(self, parts: List[str]) -> Dict[str, Any]:
        """Extract summary data from rearrangement summary line."""
        return {
            "v_gene": parts[0] if parts[0] != "N/A" else None,
            "d_gene": parts[1] if parts[1] != "N/A" else None,
            "j_gene": parts[2] if parts[2] != "N/A" else None,
            "chain_type": parts[3] if parts[3] != "N/A" else None,
            "stop_codon": parts[4] if parts[4] != "N/A" else None,
            "v_j_frame": parts[5] if parts[5] != "N/A" else None,
            "productive": parts[6] if parts[6] != "N/A" else None,
            "strand": parts[7] if parts[7] != "N/A" else None,
        }

    def _extract_cdr3_data(self, line: str) -> Dict[str, Any]:
        """Extract CDR3 data from junction details line."""
        # Look for CDR3 sequence in the line
        cdr3_match = re.search(r"([ACGTN]+)", line)
        if cdr3_match:
            cdr3_sequence = cdr3_match.group(1)

            # Try to extract position information if available
            # Look for patterns like "position 289-330" or similar
            position_match = re.search(
                r"position\s+(\d+)-(\d+)", line, re.IGNORECASE
            )
            cdr3_start = None
            cdr3_end = None

            if position_match:
                cdr3_start = int(position_match.group(1))
                cdr3_end = int(position_match.group(2))

            return {
                "cdr3_sequence": cdr3_sequence,
                "cdr3_start": cdr3_start,
                "cdr3_end": cdr3_end,
            }
        return {}

    def _extract_cdr3_data_from_subregion(self, line: str) -> Dict[str, Any]:
        """Extract CDR3 data from sub-region sequence details line."""
        # Format: CDR3    GCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTAT      AKVSYLSTASSLDY  289     330
        parts = line.split()
        if len(parts) >= 5 and parts[0] == "CDR3":
            cdr3_sequence = parts[1]
            cdr3_aa = parts[2] if len(parts) > 2 else None
            cdr3_start = int(parts[3]) if len(parts) > 3 else None
            cdr3_end = int(parts[4]) if len(parts) > 4 else None

            return {
                "cdr3_sequence": cdr3_sequence,
                "cdr3_aa": cdr3_aa,
                "cdr3_start": cdr3_start,
                "cdr3_end": cdr3_end,
            }
        return {}

    def _extract_summary_from_hits(
        self, hits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract summary information from hits."""
        v_hits = [h for h in hits if h["hit_type"] == "V"]
        d_hits = [h for h in hits if h["hit_type"] == "D"]
        j_hits = [h for h in hits if h["hit_type"] == "J"]

        return {
            "v_gene": v_hits[0]["v_gene"] if v_hits else None,
            "d_gene": d_hits[0]["d_gene"] if d_hits else None,
            "j_gene": j_hits[0]["j_gene"] if j_hits else None,
            "chain_type": v_hits[0]["chain_type"] if v_hits else None,
            "stop_codon": None,
            "v_j_frame": None,
            "productive": None,
            "strand": None,
        }

    # Chain type extraction and subject URL utilities are in BaseIgBlastParser

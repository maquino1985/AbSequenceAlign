"""
Advanced AIRR format parser for IgBLAST output.
Parses comprehensive AIRR format data into structured Pydantic models
with advanced immunological annotations.
"""

import logging
from typing import Dict, List, Optional

from backend.models.airr_models import (
    AIRRRearrangement,
    AIRRAnalysisResult,
    AIRRAlignment,
    CDRRegion,
    FrameworkRegion,
    JunctionRegion,
    SomaticMutationAnalysis,
    Locus,
    ProductivityStatus,
    FrameShiftStatus,
)


class AIRRParser:
    """Advanced parser for AIRR format IgBLAST output"""

    def __init__(self):
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    def parse_airr_output(self, airr_output: str) -> AIRRAnalysisResult:
        """
        Parse AIRR format output into structured analysis result.

        Args:
            airr_output: Raw AIRR format output from IgBLAST

        Returns:
            AIRRAnalysisResult with comprehensive annotations
        """
        self._logger.info("Parsing AIRR format output")

        lines = airr_output.strip().split("\n")
        if len(lines) < 2:
            self._logger.warning("AIRR output has insufficient data")
            return AIRRAnalysisResult(
                rearrangements=[],
                total_sequences=0,
                analysis_metadata={"error": "Insufficient AIRR data"},
            )

        # Parse header
        header = lines[0].split("\t")
        self._logger.debug(f"AIRR header contains {len(header)} fields")

        rearrangements = []
        for line_idx, line in enumerate(lines[1:], 1):
            if not line.strip():
                continue

            try:
                rearrangement = self._parse_rearrangement_line(header, line)
                if rearrangement:
                    rearrangements.append(rearrangement)
            except Exception as e:
                self._logger.error(f"Error parsing AIRR line {line_idx}: {e}")
                continue

        self._logger.info(
            f"Successfully parsed {len(rearrangements)} rearrangements"
        )

        # Calculate productive sequences count
        productive_count = sum(
            1
            for r in rearrangements
            if r.productive == ProductivityStatus.PRODUCTIVE
        )

        # Extract unique genes
        unique_v_genes = list(
            set(r.v_call for r in rearrangements if r.v_call)
        )
        unique_j_genes = list(
            set(r.j_call for r in rearrangements if r.j_call)
        )
        unique_d_genes = list(
            set(r.d_call for r in rearrangements if r.d_call)
        )

        return AIRRAnalysisResult(
            rearrangements=rearrangements,
            total_sequences=len(rearrangements),
            productive_sequences=productive_count,
            unique_v_genes=unique_v_genes,
            unique_j_genes=unique_j_genes,
            unique_d_genes=unique_d_genes,
            analysis_metadata={
                "parser_version": "1.0",
                "total_lines_processed": len(lines) - 1,
                "successful_parses": len(rearrangements),
            },
        )

    def _parse_rearrangement_line(
        self, header: List[str], line: str
    ) -> Optional[AIRRRearrangement]:
        """Parse a single AIRR data line into a rearrangement record"""

        data = line.split("\t")

        # Pad data with empty strings if shorter than header
        if len(data) < len(header):
            data.extend([""] * (len(header) - len(data)))

        # Create field mapping
        airr_data = dict(zip(header, data))

        # Extract basic sequence information
        sequence_id = airr_data.get("sequence_id", "")
        if not sequence_id:
            self._logger.warning("Skipping rearrangement without sequence_id")
            return None

        # Parse all the AIRR fields into our comprehensive model
        rearrangement_data = {
            # Basic information
            "sequence_id": sequence_id,
            "sequence": airr_data.get("sequence", ""),
            "sequence_aa": airr_data.get("sequence_aa", ""),
            "locus": self._parse_locus(airr_data.get("locus")),
            # Productivity and quality
            "productive": self._parse_productivity(
                airr_data.get("productive")
            ),
            "stop_codon": self._parse_boolean(airr_data.get("stop_codon")),
            "vj_in_frame": self._parse_boolean(airr_data.get("vj_in_frame")),
            "v_frameshift": self._parse_frameshift(
                airr_data.get("v_frameshift")
            ),
            "rev_comp": self._parse_boolean(airr_data.get("rev_comp")),
            "complete_vdj": self._parse_boolean(airr_data.get("complete_vdj")),
            "d_frame": self._parse_int(airr_data.get("d_frame")),
            # Gene assignments
            "v_call": airr_data.get("v_call") or None,
            "d_call": airr_data.get("d_call") or None,
            "j_call": airr_data.get("j_call") or None,
            "c_call": airr_data.get("c_call") or None,
            # Sequence coordinates
            "v_sequence_start": self._parse_int(
                airr_data.get("v_sequence_start")
            ),
            "v_sequence_end": self._parse_int(airr_data.get("v_sequence_end")),
            "v_germline_start": self._parse_int(
                airr_data.get("v_germline_start")
            ),
            "v_germline_end": self._parse_int(airr_data.get("v_germline_end")),
            "d_sequence_start": self._parse_int(
                airr_data.get("d_sequence_start")
            ),
            "d_sequence_end": self._parse_int(airr_data.get("d_sequence_end")),
            "d_germline_start": self._parse_int(
                airr_data.get("d_germline_start")
            ),
            "d_germline_end": self._parse_int(airr_data.get("d_germline_end")),
            "j_sequence_start": self._parse_int(
                airr_data.get("j_sequence_start")
            ),
            "j_sequence_end": self._parse_int(airr_data.get("j_sequence_end")),
            "j_germline_start": self._parse_int(
                airr_data.get("j_germline_start")
            ),
            "j_germline_end": self._parse_int(airr_data.get("j_germline_end")),
            # Full alignments
            "sequence_alignment": airr_data.get("sequence_alignment") or None,
            "germline_alignment": airr_data.get("germline_alignment") or None,
            "sequence_alignment_aa": airr_data.get("sequence_alignment_aa")
            or None,
            "germline_alignment_aa": airr_data.get("germline_alignment_aa")
            or None,
        }

        # Parse alignment details
        rearrangement_data["v_alignment"] = self._parse_alignment(
            airr_data, "v"
        )
        rearrangement_data["d_alignment"] = self._parse_alignment(
            airr_data, "d"
        )
        rearrangement_data["j_alignment"] = self._parse_alignment(
            airr_data, "j"
        )

        # Parse framework and CDR regions
        rearrangement_data["fwr1"] = self._parse_framework_region(
            airr_data, "fwr1"
        )
        rearrangement_data["cdr1"] = self._parse_cdr_region(airr_data, "cdr1")
        rearrangement_data["fwr2"] = self._parse_framework_region(
            airr_data, "fwr2"
        )
        rearrangement_data["cdr2"] = self._parse_cdr_region(airr_data, "cdr2")
        rearrangement_data["fwr3"] = self._parse_framework_region(
            airr_data, "fwr3"
        )
        rearrangement_data["fwr4"] = self._parse_framework_region(
            airr_data, "fwr4"
        )

        # Parse junction/CDR3 region
        rearrangement_data["junction_region"] = self._parse_junction_region(
            airr_data
        )

        # Parse somatic mutations (if available)
        rearrangement_data["somatic_mutations"] = (
            self._parse_somatic_mutations(airr_data)
        )

        try:
            return AIRRRearrangement(**rearrangement_data)
        except Exception as e:
            self._logger.error(f"Error creating AIRRRearrangement: {e}")
            self._logger.debug(f"Data that failed: {rearrangement_data}")
            return None

    def _parse_alignment(
        self, airr_data: Dict[str, str], gene_type: str
    ) -> Optional[AIRRAlignment]:
        """Parse alignment information for V, D, or J genes"""

        alignment_data = {
            "start": self._parse_int(
                airr_data.get(f"{gene_type}_alignment_start")
            ),
            "end": self._parse_int(
                airr_data.get(f"{gene_type}_alignment_end")
            ),
            "sequence_alignment": airr_data.get(
                f"{gene_type}_sequence_alignment"
            )
            or None,
            "sequence_alignment_aa": airr_data.get(
                f"{gene_type}_sequence_alignment_aa"
            )
            or None,
            "germline_alignment": airr_data.get(
                f"{gene_type}_germline_alignment"
            )
            or None,
            "germline_alignment_aa": airr_data.get(
                f"{gene_type}_germline_alignment_aa"
            )
            or None,
            "score": self._parse_float(airr_data.get(f"{gene_type}_score")),
            "identity": self._parse_float(
                airr_data.get(f"{gene_type}_identity")
            ),
            "cigar": airr_data.get(f"{gene_type}_cigar") or None,
            "support": self._parse_float(
                airr_data.get(f"{gene_type}_support")
            ),
        }

        # Only create alignment if we have some data
        if any(v is not None for v in alignment_data.values()):
            return AIRRAlignment(**alignment_data)
        return None

    def _parse_framework_region(
        self, airr_data: Dict[str, str], region: str
    ) -> Optional[FrameworkRegion]:
        """Parse framework region information"""

        fwr_data = {
            "sequence": airr_data.get(region) or None,
            "sequence_aa": airr_data.get(f"{region}_aa") or None,
            "start": self._parse_int(airr_data.get(f"{region}_start")),
            "end": self._parse_int(airr_data.get(f"{region}_end")),
        }

        if any(v is not None for v in fwr_data.values()):
            return FrameworkRegion(**fwr_data)
        return None

    def _parse_cdr_region(
        self, airr_data: Dict[str, str], region: str
    ) -> Optional[CDRRegion]:
        """Parse CDR region information"""

        cdr_data = {
            "sequence": airr_data.get(region) or None,
            "sequence_aa": airr_data.get(f"{region}_aa") or None,
            "start": self._parse_int(airr_data.get(f"{region}_start")),
            "end": self._parse_int(airr_data.get(f"{region}_end")),
        }

        if any(v is not None for v in cdr_data.values()):
            return CDRRegion(**cdr_data)
        return None

    def _parse_junction_region(
        self, airr_data: Dict[str, str]
    ) -> Optional[JunctionRegion]:
        """Parse junction/CDR3 region with detailed annotations"""

        junction_data = {
            "junction": airr_data.get("junction") or None,
            "junction_aa": airr_data.get("junction_aa") or None,
            "junction_length": self._parse_int(
                airr_data.get("junction_length")
            ),
            "junction_aa_length": self._parse_int(
                airr_data.get("junction_aa_length")
            ),
            "cdr3": airr_data.get("cdr3") or None,
            "cdr3_aa": airr_data.get("cdr3_aa") or None,
            "cdr3_start": self._parse_int(airr_data.get("cdr3_start")),
            "cdr3_end": self._parse_int(airr_data.get("cdr3_end")),
            "np1": airr_data.get("np1") or None,
            "np1_length": self._parse_int(airr_data.get("np1_length")),
            "np2": airr_data.get("np2") or None,
            "np2_length": self._parse_int(airr_data.get("np2_length")),
        }

        if any(v is not None for v in junction_data.values()):
            return JunctionRegion(**junction_data)
        return None

    def _parse_somatic_mutations(
        self, airr_data: Dict[str, str]
    ) -> Optional[SomaticMutationAnalysis]:
        """Parse somatic mutation information if available"""

        # These fields are not standard in IgBLAST AIRR output but could be added
        # by downstream analysis tools
        mutation_data = {
            "v_mutations": self._parse_int(airr_data.get("v_mutations")),
            "v_mutation_frequency": self._parse_float(
                airr_data.get("v_mutation_frequency")
            ),
            "silent_mutations": self._parse_int(
                airr_data.get("silent_mutations")
            ),
            "replacement_mutations": self._parse_int(
                airr_data.get("replacement_mutations")
            ),
            "replacement_to_silent_ratio": self._parse_float(
                airr_data.get("replacement_to_silent_ratio")
            ),
        }

        if any(v is not None for v in mutation_data.values()):
            return SomaticMutationAnalysis(**mutation_data)
        return None

    def _parse_locus(self, value: Optional[str]) -> Optional[Locus]:
        """Parse locus field"""
        if not value:
            return None
        try:
            return Locus(value.upper())
        except ValueError:
            self._logger.warning(f"Unknown locus value: {value}")
            return None

    def _parse_productivity(
        self, value: Optional[str]
    ) -> Optional[ProductivityStatus]:
        """Parse productivity field"""
        if not value:
            return ProductivityStatus.UNKNOWN

        value = value.upper().strip()
        if value in ["T", "TRUE", "PRODUCTIVE"]:
            return ProductivityStatus.PRODUCTIVE
        elif value in ["F", "FALSE", "UNPRODUCTIVE"]:
            return ProductivityStatus.UNPRODUCTIVE
        else:
            return ProductivityStatus.UNKNOWN

    def _parse_frameshift(
        self, value: Optional[str]
    ) -> Optional[FrameShiftStatus]:
        """Parse frameshift field"""
        if not value:
            return FrameShiftStatus.UNKNOWN

        value = value.upper().strip()
        if value in ["T", "TRUE"]:
            return FrameShiftStatus.FRAMESHIFT
        elif value in ["F", "FALSE"]:
            return FrameShiftStatus.NO_FRAMESHIFT
        else:
            return FrameShiftStatus.UNKNOWN

    def _parse_boolean(self, value: Optional[str]) -> Optional[bool]:
        """Parse boolean field"""
        if not value:
            return None

        value = value.upper().strip()
        if value in ["T", "TRUE", "1", "YES"]:
            return True
        elif value in ["F", "FALSE", "0", "NO"]:
            return False
        return None

    def _parse_int(self, value: Optional[str]) -> Optional[int]:
        """Parse integer field"""
        if not value or value.strip() == "":
            return None
        try:
            return int(float(value))  # Handle cases like "123.0"
        except (ValueError, TypeError):
            return None

    def _parse_float(self, value: Optional[str]) -> Optional[float]:
        """Parse float field"""
        if not value or value.strip() == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

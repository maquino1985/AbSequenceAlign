"""
IgBLAST adapter for immunoglobulin and T-cell receptor sequence analysis.
Implements the ExternalToolAdapter interface to provide a clean abstraction.
IgBLAST is specifically designed for antibody and TCR sequence analysis.
"""

import subprocess
import tempfile
import os
from typing import Dict, Any, List
import logging

from .base_adapter import BaseExternalToolAdapter
from ...core.exceptions import ExternalToolError


class IgBlastAdapter(BaseExternalToolAdapter):
    """Adapter for the IgBLAST tool for immunoglobulin and TCR sequence analysis"""

    def __init__(self, docker_client=None):
        self.docker_client = docker_client
        self._supported_blast_types = ["igblastn", "igblastp"]
        self._supported_organisms = [
            "human",
            "mouse",
            "rat",
            "rabbit",
            "rhesus_monkey",
        ]
        super().__init__("igblast")
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    def _find_executable(self) -> str:
        """Find the IgBLAST executable path"""
        # First try to find igblastn in PATH
        igblastn_path = self._find_executable_in_path("igblastn")
        if igblastn_path:
            return igblastn_path

        # If not found, try using Docker
        if self.docker_client:
            return "docker"

        raise FileNotFoundError(
            "IgBLAST executable not found in PATH and Docker not available"
        )

    def _validate_tool_installation(self) -> None:
        """Validate that IgBLAST is properly installed"""
        try:
            if self.executable_path == "docker":
                # Check if Docker is available and IgBLAST image exists
                if not self.docker_client:
                    raise ExternalToolError(
                        "Docker client not available", tool_name=self.tool_name
                    )

                # Check if IgBLAST image is available
                try:
                    self.docker_client.images.get("ncbi/igblast:latest")
                except Exception:
                    raise ExternalToolError(
                        "NCBI IgBLAST Docker image not found",
                        tool_name=self.tool_name,
                    )
            else:
                # Check if IgBLAST executable works
                result = subprocess.run(
                    [self.executable_path, "-help"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    raise ExternalToolError(
                        f"IgBLAST executable test failed: {result.stderr}",
                        tool_name=self.tool_name,
                    )

        except Exception as e:
            raise ExternalToolError(
                f"IgBLAST validation failed: {str(e)}",
                tool_name=self.tool_name,
            )

    def _build_command(self, **kwargs) -> List[str]:
        """Build the IgBLAST command"""
        blast_type = kwargs.get("blast_type", "igblastn")
        query_sequence = kwargs.get("query_sequence")
        organism = kwargs.get("organism", "human")

        if not query_sequence:
            raise ValueError("query_sequence is required")
        if blast_type not in self._supported_blast_types:
            raise ValueError(f"Unsupported IgBLAST type: {blast_type}")
        if organism not in self._supported_organisms:
            raise ValueError(f"Unsupported organism: {organism}")

        # Validate sequence
        self._validate_sequence(query_sequence, blast_type)

        # Create temporary query file
        query_file = self._create_query_file(query_sequence)

        # Build base command
        if self.executable_path == "docker":
            # Use absolute paths for Docker volume mounting
            abs_query_file = os.path.abspath(query_file)
            work_dir = os.path.dirname(abs_query_file)

            command = [
                "docker",
                "run",
                "--rm",
                "--platform",
                "linux/amd64",
                "-v",
                f"{work_dir}:/work",
                "-w",
                "/work",
                "ncbi/igblast:latest",
                blast_type,
            ]
        else:
            command = [blast_type]

        # Add required parameters
        if self.executable_path == "docker":
            command.extend(["-query", os.path.basename(abs_query_file)])
        else:
            command.extend(["-query", query_file])

        command.extend(["-organism", organism])

        # Add optional parameters
        if "evalue" in kwargs:
            command.extend(["-evalue", str(kwargs["evalue"])])
        if "num_alignments_V" in kwargs:
            command.extend(
                ["-num_alignments_V", str(kwargs["num_alignments_V"])]
            )
        if "num_alignments_D" in kwargs:
            command.extend(
                ["-num_alignments_D", str(kwargs["num_alignments_D"])]
            )
        if "num_alignments_J" in kwargs:
            command.extend(
                ["-num_alignments_J", str(kwargs["num_alignments_J"])]
            )
        if "num_alignments_C" in kwargs:
            command.extend(
                ["-num_alignments_C", str(kwargs["num_alignments_C"])]
            )
        if "outfmt" in kwargs:
            command.extend(["-outfmt", str(kwargs["outfmt"])])
        else:
            # Default to tabular format with antibody-specific fields
            command.extend(
                [
                    "-outfmt",
                    "7 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore v_gene d_gene j_gene c_gene cdr3_start cdr3_end cdr3_seq",
                ]
            )

        # Add additional parameters
        for key, value in kwargs.items():
            if key not in [
                "blast_type",
                "query_sequence",
                "organism",
                "evalue",
                "num_alignments_V",
                "num_alignments_D",
                "num_alignments_J",
                "num_alignments_C",
                "outfmt",
            ]:
                if isinstance(value, bool):
                    if value:
                        command.append(f"-{key}")
                else:
                    command.extend([f"-{key}", str(value)])

        return command

    def _parse_output(self, output: str, **kwargs) -> Dict[str, Any]:
        """Parse IgBLAST output"""
        blast_type = kwargs.get("blast_type", "igblastn")
        outfmt = kwargs.get("outfmt", "7")

        if outfmt == "7":
            return self._parse_tabular_output(output, blast_type)
        else:
            return self._parse_standard_output(output, blast_type)

    def _parse_tabular_output(
        self, output: str, blast_type: str
    ) -> Dict[str, Any]:
        """Parse tabular IgBLAST output (outfmt 7)"""
        lines = output.strip().split("\n")
        hits = []
        query_info = {}
        analysis_summary = {}

        # Parse headers if present
        header_lines = []
        data_lines = []

        for line in lines:
            if line.startswith("#"):
                header_lines.append(line)
                # Extract query info from headers
                if "Query:" in line:
                    query_info["query_id"] = line.split("Query:")[1].strip()
                elif "Database:" in line:
                    query_info["database"] = line.split("Database:")[1].strip()
            else:
                data_lines.append(line)

        # Parse data lines
        for line in data_lines:
            if not line.strip():
                continue

            fields = line.split("\t")
            if len(fields) >= 17:  # IgBLAST tabular format has 17+ fields
                hit = {
                    "query_id": fields[0],
                    "subject_id": fields[1],
                    "identity": float(fields[2]),
                    "alignment_length": int(fields[3]),
                    "mismatches": int(fields[4]),
                    "gap_opens": int(fields[5]),
                    "query_start": int(fields[6]),
                    "query_end": int(fields[7]),
                    "subject_start": int(fields[8]),
                    "subject_end": int(fields[9]),
                    "evalue": float(fields[10]),
                    "bit_score": float(fields[11]),
                    "v_gene": fields[12] if fields[12] != "N/A" else None,
                    "d_gene": fields[13] if fields[13] != "N/A" else None,
                    "j_gene": fields[14] if fields[14] != "N/A" else None,
                    "c_gene": fields[15] if fields[15] != "N/A" else None,
                }

                # Add CDR3 information if present
                if len(fields) > 16:
                    try:
                        hit["cdr3_start"] = (
                            int(fields[16]) if fields[16] != "N/A" else None
                        )
                    except ValueError:
                        hit["cdr3_start"] = None

                if len(fields) > 17:
                    try:
                        hit["cdr3_end"] = (
                            int(fields[17]) if fields[17] != "N/A" else None
                        )
                    except ValueError:
                        hit["cdr3_end"] = None

                if len(fields) > 18:
                    hit["cdr3_sequence"] = (
                        fields[18] if fields[18] != "N/A" else None
                    )

                hits.append(hit)

        # Create analysis summary
        if hits:
            best_hit = hits[0]
            analysis_summary = {
                "best_v_gene": best_hit.get("v_gene"),
                "best_d_gene": best_hit.get("d_gene"),
                "best_j_gene": best_hit.get("j_gene"),
                "best_c_gene": best_hit.get("c_gene"),
                "cdr3_sequence": best_hit.get("cdr3_sequence"),
                "cdr3_start": best_hit.get("cdr3_start"),
                "cdr3_end": best_hit.get("cdr3_end"),
                "total_hits": len(hits),
            }

        return {
            "blast_type": blast_type,
            "query_info": query_info,
            "hits": hits,
            "analysis_summary": analysis_summary,
            "total_hits": len(hits),
        }

    def _parse_standard_output(
        self, output: str, blast_type: str
    ) -> Dict[str, Any]:
        """Parse standard IgBLAST output"""
        # This is a simplified parser for standard output
        # In a real implementation, you'd want a more robust parser
        return {
            "blast_type": blast_type,
            "raw_output": output,
            "hits": [],
            "analysis_summary": {},
            "total_hits": 0,
        }

    def _validate_sequence(self, sequence: str, blast_type: str) -> None:
        """Validate input sequence"""
        if not sequence or not isinstance(sequence, str):
            raise ValueError("Sequence must be a non-empty string")

        sequence = sequence.upper().strip()

        if blast_type == "igblastn":
            # DNA sequence validation
            valid_nt = set("ATGCU")
            invalid_chars = set(sequence) - valid_nt
            if invalid_chars:
                raise ValueError(
                    f"Invalid nucleotide characters: {invalid_chars}"
                )
        elif blast_type == "igblastp":
            # Protein sequence validation
            valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
            invalid_chars = set(sequence) - valid_aa
            if invalid_chars:
                raise ValueError(
                    f"Invalid amino acid characters: {invalid_chars}"
                )

    def _create_query_file(self, sequence: str) -> str:
        """Create a temporary FASTA file for the query sequence"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as f:
            f.write(f">query\n{sequence}\n")
            return f.name

    def get_supported_organisms(self) -> List[str]:
        """Get list of supported organisms"""
        return self._supported_organisms.copy()

    def get_supported_blast_types(self) -> List[str]:
        """Get list of supported IgBLAST types"""
        return self._supported_blast_types.copy()

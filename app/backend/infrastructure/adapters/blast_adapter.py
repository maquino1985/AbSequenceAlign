"""
BLAST adapter for sequence similarity searches.
Implements the ExternalToolAdapter interface to provide a clean abstraction.
"""

import subprocess
import tempfile
import os
from typing import Dict, Any, List
import logging

from .base_adapter import BaseExternalToolAdapter
from ...core.exceptions import ExternalToolError


class BlastAdapter(BaseExternalToolAdapter):
    """Adapter for the BLAST tool for sequence similarity searches"""

    def __init__(self, docker_client=None):
        self.docker_client = docker_client
        self._supported_blast_types = [
            "blastp",
            "blastn",
            "blastx",
            "tblastn",
            "tblastx",
        ]
        super().__init__("blast")
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    def _find_executable(self) -> str:
        """Find the BLAST executable path"""
        # First try to find blastp in PATH
        blastp_path = self._find_executable_in_path("blastp")
        if blastp_path:
            return blastp_path

        # If not found, try using Docker
        if self.docker_client:
            return "docker"

        raise FileNotFoundError(
            "BLAST executable not found in PATH and Docker not available"
        )

    def _validate_tool_installation(self) -> None:
        """Validate that BLAST is properly installed"""
        try:
            if self.executable_path == "docker":
                # Check if Docker is available and BLAST image exists
                if not self.docker_client:
                    raise ExternalToolError(
                        "Docker client not available", tool_name=self.tool_name
                    )

                # Check if BLAST image is available
                try:
                    self.docker_client.images.get("ncbi/blast:latest")
                except Exception:
                    raise ExternalToolError(
                        "NCBI BLAST Docker image not found",
                        tool_name=self.tool_name,
                    )
            else:
                # Check if BLAST executable works
                result = subprocess.run(
                    [self.executable_path, "-help"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    raise ExternalToolError(
                        f"BLAST executable test failed: {result.stderr}",
                        tool_name=self.tool_name,
                    )

        except Exception as e:
            raise ExternalToolError(
                f"BLAST validation failed: {str(e)}", tool_name=self.tool_name
            )

    def _build_command(self, **kwargs) -> List[str]:
        """Build the BLAST command"""
        blast_type = kwargs.get("blast_type", "blastp")
        query_sequence = kwargs.get("query_sequence")
        database = kwargs.get("database")

        if not query_sequence:
            raise ValueError("query_sequence is required")
        if not database:
            raise ValueError("database is required")
        if blast_type not in self._supported_blast_types:
            raise ValueError(f"Unsupported BLAST type: {blast_type}")

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
                "ncbi/blast:latest",
                blast_type,
            ]
        else:
            command = [blast_type]

        # Add required parameters
        if self.executable_path == "docker":
            command.extend(["-query", os.path.basename(abs_query_file)])
            command.extend(["-db", database])
        else:
            command.extend(["-query", query_file])
            command.extend(["-db", database])

        # Add optional parameters
        if "evalue" in kwargs:
            command.extend(["-evalue", str(kwargs["evalue"])])
        if "max_target_seqs" in kwargs:
            command.extend(
                ["-max_target_seqs", str(kwargs["max_target_seqs"])]
            )
        if "outfmt" in kwargs:
            command.extend(["-outfmt", str(kwargs["outfmt"])])
        else:
            # Default to tabular format
            command.extend(["-outfmt", "6"])

        # Add additional parameters
        for key, value in kwargs.items():
            if key not in [
                "blast_type",
                "query_sequence",
                "database",
                "evalue",
                "max_target_seqs",
                "outfmt",
            ]:
                if isinstance(value, bool):
                    if value:
                        command.append(f"-{key}")
                else:
                    command.extend([f"-{key}", str(value)])

        return command

    def _parse_output(self, output: str, **kwargs) -> Dict[str, Any]:
        """Parse BLAST output"""
        blast_type = kwargs.get("blast_type", "blastp")
        outfmt = kwargs.get("outfmt", "6")

        if outfmt == "6":
            return self._parse_tabular_output(output, blast_type)
        else:
            return self._parse_standard_output(output, blast_type)

    def _parse_tabular_output(
        self, output: str, blast_type: str
    ) -> Dict[str, Any]:
        """Parse tabular BLAST output (outfmt 6)"""
        lines = output.strip().split("\n")
        hits = []
        query_info = {}

        # Parse headers if present
        header_lines = []
        data_lines = []

        for line in lines:
            if line.startswith("#"):
                header_lines.append(line)
                # Extract query info from headers
                if "Query:" in line:
                    query_info["query_id"] = line.split("Query:")[1].strip()
            else:
                data_lines.append(line)

        # Parse data lines
        for line in data_lines:
            if not line.strip():
                continue

            fields = line.split("\t")
            if len(fields) >= 12:  # Standard tabular format has 12+ fields
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
                }

                # Add additional fields if present
                if len(fields) > 12:
                    hit["subject_def"] = fields[12]

                hits.append(hit)

        return {
            "blast_type": blast_type,
            "query_info": query_info,
            "hits": hits,
            "total_hits": len(hits),
        }

    def _parse_standard_output(
        self, output: str, blast_type: str
    ) -> Dict[str, Any]:
        """Parse standard BLAST output"""
        # This is a simplified parser for standard output
        # In a real implementation, you'd want a more robust parser
        return {
            "blast_type": blast_type,
            "raw_output": output,
            "hits": [],
            "total_hits": 0,
        }

    def _validate_sequence(self, sequence: str, blast_type: str) -> None:
        """Validate input sequence"""
        if not sequence or not isinstance(sequence, str):
            raise ValueError("Sequence must be a non-empty string")

        sequence = sequence.upper().strip()

        if blast_type in ["blastp", "blastx", "tblastn"]:
            # Protein sequence validation
            valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
            invalid_chars = set(sequence) - valid_aa
            if invalid_chars:
                raise ValueError(
                    f"Invalid amino acid characters: {invalid_chars}"
                )
        elif blast_type in ["blastn", "tblastx"]:
            # DNA/RNA sequence validation
            valid_nt = set("ATGCU")
            invalid_chars = set(sequence) - valid_nt
            if invalid_chars:
                raise ValueError(
                    f"Invalid nucleotide characters: {invalid_chars}"
                )

    def _create_query_file(self, sequence: str) -> str:
        """Create a temporary FASTA file for the query sequence"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as f:
            f.write(f">query\n{sequence}\n")
            return f.name

    def _create_blast_database(
        self, fasta_file: str, database_name: str
    ) -> None:
        """Create a BLAST database from a FASTA file"""
        if self.executable_path == "docker":
            # Use absolute paths for Docker volume mounting
            abs_fasta_file = os.path.abspath(fasta_file)
            abs_database_name = os.path.abspath(database_name)
            work_dir = os.path.dirname(abs_fasta_file)

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
                "ncbi/blast:latest",
                "makeblastdb",
                "-in",
                os.path.basename(abs_fasta_file),
                "-dbtype",
                "prot" if self._is_protein_fasta(fasta_file) else "nucl",
                "-out",
                os.path.basename(abs_database_name),
            ]
        else:
            command = [
                "makeblastdb",
                "-in",
                fasta_file,
                "-dbtype",
                "prot" if self._is_protein_fasta(fasta_file) else "nucl",
                "-out",
                database_name,
            ]

        result = subprocess.run(
            command, capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            raise ExternalToolError(
                f"Failed to create BLAST database: {result.stderr}",
                tool_name=self.tool_name,
            )

    def _cleanup_blast_database(self, database_name: str) -> None:
        """Clean up BLAST database files"""
        extensions = [".phr", ".pin", ".psq", ".nhr", ".nin", ".nsq"]
        for ext in extensions:
            db_file = f"{database_name}{ext}"
            if os.path.exists(db_file):
                os.unlink(db_file)

    def _is_protein_fasta(self, fasta_file: str) -> bool:
        """Determine if a FASTA file contains protein sequences"""
        with open(fasta_file, "r") as f:
            for line in f:
                if line.startswith(">"):
                    continue
                sequence = line.strip().upper()
                if sequence:
                    # Check if sequence contains mostly amino acids
                    aa_chars = sum(
                        1 for c in sequence if c in "ACDEFGHIKLMNPQRSTVWY"
                    )
                    nt_chars = sum(1 for c in sequence if c in "ATGCU")
                    return aa_chars > nt_chars
        return True  # Default to protein if we can't determine

    def get_supported_blast_types(self) -> List[str]:
        """Get list of supported BLAST types"""
        return self._supported_blast_types.copy()

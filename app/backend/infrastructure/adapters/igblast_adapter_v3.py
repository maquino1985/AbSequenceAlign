"""
IgBLAST Adapter V3 - Simplified User-Selectable Database Approach

This adapter implements a clean, simple approach where users explicitly select
which databases to use for V, D, J, and C genes, eliminating the complexity
of organism detection and database guessing.
"""

import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.exceptions import ExternalToolError
from backend.infrastructure.adapters.base_adapter import (
    BaseExternalToolAdapter,
)
from backend.infrastructure.adapters.airr_parser import AIRRParser
from backend.infrastructure.adapters.tabular_parser import TabularParser


class IgBlastAdapterV3(BaseExternalToolAdapter):
    """Simplified IgBLAST adapter with user-selectable databases."""

    def __init__(self):
        """Initialize the IgBLAST adapter."""
        super().__init__("igblast", "docker")
        self._logger = logging.getLogger(__name__)
        self.database_metadata = self._load_database_metadata()
        self.airr_parser = AIRRParser()
        self.tabular_parser = TabularParser()

    def _load_database_metadata(self) -> Dict[str, Any]:
        """Load database metadata from JSON file."""
        # Try multiple possible paths for the metadata file
        possible_paths = [
            Path(
                "data/igblast/database_metadata.json"
            ),  # Relative to current directory
            Path(__file__).parent.parent.parent.parent.parent
            / "data/igblast/database_metadata.json",  # Relative to this file
            Path(
                "/Users/aquinmx3/repos/AbSequenceAlign/data/igblast/database_metadata.json"
            ),  # Absolute path
        ]

        for metadata_path in possible_paths:
            if metadata_path.exists():
                try:
                    with open(metadata_path, "r") as f:
                        self._logger.info(
                            f"Loaded database metadata from: {metadata_path}"
                        )
                        return json.load(f)
                except Exception as e:
                    self._logger.error(
                        f"Error loading database metadata from {metadata_path}: {e}"
                    )
                    continue

        self._logger.warning(
            f"Database metadata not found in any of the expected locations: {[str(p) for p in possible_paths]}"
        )
        return {"igblast_databases": {}, "blast_databases": {}}

    def get_available_databases(self) -> Dict[str, Any]:
        """Return available databases organized by organism and gene type."""
        return self.database_metadata.get("igblast_databases", {})

    def get_blast_databases(self) -> Dict[str, Any]:
        """Return available BLAST databases."""
        return self.database_metadata.get("blast_databases", {})

    def _validate_tool_installation(self) -> None:
        """Validate that IgBLAST Docker container is running."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=absequencealign-igblast",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if "absequencealign-igblast" not in result.stdout:
                raise ExternalToolError(
                    "IgBLAST Docker container is not running",
                    tool_name=self.tool_name,
                )
        except Exception as e:
            raise ExternalToolError(
                f"Failed to validate IgBLAST installation: {e}",
                tool_name=self.tool_name,
            )

    def _find_executable(self) -> str:
        """Find IgBLAST executable (Docker container)."""
        return "docker"

    def _validate_sequence(self, sequence: str, blast_type: str) -> None:
        """Validate sequence format."""
        if not sequence:
            raise ValueError("Sequence cannot be empty")

        # Clean sequence by removing spaces, newlines, and converting to uppercase
        clean_sequence = re.sub(r"[\s\n\r]", "", sequence).upper()

        if blast_type == "igblastn":
            # Validate nucleotide sequence (A, C, G, T, N)
            if not re.match(r"^[ACGTN]+$", clean_sequence):
                raise ValueError("Invalid nucleotide sequence")
        elif blast_type == "igblastp":
            # Validate protein sequence (standard amino acids)
            if not re.match(r"^[ACDEFGHIKLMNPQRSTVWY]+$", clean_sequence):
                raise ValueError("Invalid protein sequence")

    def _validate_database_path(self, db_path: str) -> bool:
        """Validate that a database path exists and is accessible."""
        if not db_path:
            return False

        # Check if database files exist in the container
        try:
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "absequencealign-igblast",
                    "test",
                    "-f",
                    f"{db_path}.nhr",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _extract_organism_from_db_path(self, db_path: str) -> Optional[str]:
        """Extract organism from database path."""
        if not db_path:
            return None

        # Look for organism in the path
        path_parts = db_path.split("/")
        for part in path_parts:
            if part in ["human", "mouse", "rhesus", "rabbit", "rat"]:
                return part

        return None

    def _get_auxiliary_data_path(self, organism: str) -> Optional[str]:
        """Get auxiliary data path for the organism."""
        if not organism:
            return None

        # Map organism names to auxiliary file names
        organism_map = {
            "human": "human_gl.aux",
            "mouse": "mouse_gl.aux",
            "rhesus": "rhesus_monkey_gl.aux",
            "rabbit": "rabbit_gl.aux",
            "rat": "rat_gl.aux",
        }

        aux_file = organism_map.get(organism)
        if aux_file:
            return f"/ncbi-igblast-1.22.0/optional_file/{aux_file}"

        return None

    def _build_command(
        self,
        query_sequence: str,
        v_db: str,
        d_db: Optional[str] = None,
        j_db: Optional[str] = None,
        c_db: Optional[str] = None,
        blast_type: str = "igblastn",
        use_airr_format: bool = False,
        **kwargs,
    ) -> List[str]:
        """Build IgBLAST command with user-selected databases."""
        # Validate sequence
        self._validate_sequence(query_sequence, blast_type)

        # AIRR format is only available for nucleotide IgBLAST
        if blast_type == "igblastp" and use_airr_format:
            raise ValueError(
                "AIRR format is only available for nucleotide IgBLAST (igblastn), not protein IgBLAST (igblastp)"
            )

        # Validate required V database
        if not self._validate_database_path(v_db):
            raise ValueError(f"Invalid V database path: {v_db}")

        # Extract organism from V database path
        organism = self._extract_organism_from_db_path(v_db)
        # Propagate organism hint to parsers for proper IMGT URL species mapping
        self.airr_parser.organism = organism
        self.tabular_parser.organism = organism
        auxiliary_data_path = self._get_auxiliary_data_path(organism)

        # Build base command
        command = [
            "docker",
            "exec",
            "-i",
            "absequencealign-igblast",
            blast_type,
            "-query",
            "/dev/stdin",
            "-germline_db_V",
            v_db,
        ]

        # Add auxiliary data only for nucleotide IgBLAST
        if blast_type == "igblastn" and auxiliary_data_path:
            command.extend(["-auxiliary_data", auxiliary_data_path])

        # For protein IgBLAST, only use V database (ignore D, J, C)
        if blast_type == "igblastp":
            self._logger.info(
                "Protein IgBLAST: Using only V database, ignoring D, J, C databases"
            )
        else:
            # Add optional databases for nucleotide IgBLAST
            if d_db and self._validate_database_path(d_db):
                command.extend(["-germline_db_D", d_db])

            if j_db and self._validate_database_path(j_db):
                command.extend(["-germline_db_J", j_db])

            if c_db and self._validate_database_path(c_db):
                # Check if C gene database files exist and are valid
                c_db_path = Path(c_db)
                if (
                    c_db_path.exists() and c_db_path.stat().st_size > 1000
                ):  # Basic size check
                    command.extend(["-c_region_db", c_db])
                else:
                    self._logger.warning(
                        f"C gene database {c_db} is invalid or too small, skipping"
                    )

        # Add domain system for protein IgBLAST
        if blast_type == "igblastp" and kwargs.get("domain_system"):
            domain_system = kwargs["domain_system"]
            if domain_system not in ["imgt", "kabat"]:
                raise ValueError(
                    f"Unsupported domain system: {domain_system}. Supported: imgt, kabat"
                )
            command.extend(["-domain_system", domain_system])

        # Add output format (at the end)
        if use_airr_format:
            command.extend(["-outfmt", "19"])  # AIRR format
        else:
            command.extend(["-outfmt", "7"])  # Tabular format

        return command

    def execute(
        self,
        query_sequence: str,
        v_db: str,
        d_db: Optional[str] = None,
        j_db: Optional[str] = None,
        c_db: Optional[str] = None,
        blast_type: str = "igblastn",
        use_airr_format: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute IgBLAST with user-selected databases."""
        try:
            # Clean sequence by removing spaces, newlines, and converting to uppercase
            clean_sequence = re.sub(r"[\s\n\r]", "", query_sequence).upper()

            command = self._build_command(
                query_sequence=clean_sequence,
                v_db=v_db,
                d_db=d_db,
                j_db=j_db,
                c_db=c_db,
                blast_type=blast_type,
                use_airr_format=use_airr_format,
                **kwargs,
            )

            self._logger.debug(f"Executing: {' '.join(command)}")

            # Execute with stdin piping
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            input_data = f">query\n{clean_sequence}\n"
            self._logger.debug(f"Input data length: {len(input_data)}")
            self._logger.debug(f"Input data start: {input_data[:100]}")

            stdout, stderr = process.communicate(
                input=input_data,
                timeout=self._get_timeout(),
            )

            self._logger.debug(f"Return code: {process.returncode}")
            self._logger.debug(f"STDOUT length: {len(stdout)}")
            self._logger.debug(f"STDERR: {stderr}")
            self._logger.debug(f"STDOUT: {stdout}")

            if process.returncode != 0:
                error_msg = f"IgBLAST execution failed with return code {process.returncode}"
                if stderr:
                    error_msg += f": {stderr}"
                raise ExternalToolError(error_msg, tool_name=self.tool_name)

            # Parse output based on format
            if use_airr_format:
                parsed_result = self.airr_parser.parse(stdout, blast_type)
            else:
                parsed_result = self.tabular_parser.parse(
                    stdout, blast_type, clean_sequence
                )

            # Add database information to result
            parsed_result["databases_used"] = {
                "V": v_db,
                "D": d_db,
                "J": j_db,
                "C": c_db,
            }

            # Add query sequence to result for frontend visualization
            parsed_result["query_sequence"] = clean_sequence

            self._logger.debug("IgBLAST execution completed successfully")
            return parsed_result

        except subprocess.TimeoutExpired:
            error_msg = f"IgBLAST execution timed out after {self._get_timeout()} seconds"
            self._logger.error(error_msg)
            raise ExternalToolError(error_msg, tool_name=self.tool_name)

        except Exception as e:
            error_msg = f"IgBLAST execution failed: {str(e)}"
            self._logger.error(error_msg)
            raise ExternalToolError(error_msg, tool_name=self.tool_name)

    def _parse_output(self, output: str, blast_type: str) -> Dict[str, Any]:
        """Parse IgBLAST output (delegates to specific parsers)."""
        return self.tabular_parser.parse(output, blast_type)

    def _extract_chain_type(self, gene_name: str) -> str:
        """Extract chain type from gene name."""
        if gene_name.startswith("IGH"):
            return "heavy"
        elif gene_name.startswith(("IGK", "IGL")):
            return "light"
        elif gene_name.startswith(("TRA", "TRB", "TRG", "TRD")):
            return "tcr"
        else:
            return "unknown"

    def _get_subject_url(self, subject_id: str) -> str:
        """Generate URL for subject ID."""
        if not subject_id or subject_id == "N/A":
            return ""

        # Generate IMGT URLs for gene assignments
        if subject_id.startswith(("IGH", "IGK", "IGL")):
            return f"https://www.imgt.org/IMGTrepertoire/index.php?section=LocusGenes&repertoire=genetable&species=Homo+sapiens&group=IGH&locus={subject_id}"
        elif subject_id.startswith(("TRA", "TRB", "TRG", "TRD")):
            return f"https://www.imgt.org/IMGTrepertoire/index.php?section=LocusGenes&repertoire=genetable&species=Homo+sapiens&group=TCR&locus={subject_id}"
        else:
            return ""

    def _get_timeout(self) -> int:
        """Get timeout for IgBLAST execution."""
        return 300  # 5 minutes

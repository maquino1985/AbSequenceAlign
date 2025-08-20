"""
IgBLAST Adapter V2 - Clean, Test-Driven Implementation
Provides interface to IgBLAST for antibody sequence analysis.
"""

import logging
import re
import subprocess
from typing import Dict, Any, List

from backend.config import IGBLAST_INTERNAL_DATA_DIR
from backend.core.exceptions import ExternalToolError
from backend.infrastructure.adapters.base_adapter import (
    BaseExternalToolAdapter,
)
from backend.utils.chain_type_utils import ChainTypeUtils


class IgBlastAdapterV2(BaseExternalToolAdapter):
    """Clean IgBLAST adapter implementation with advanced features."""

    def __init__(self, docker_client=None):
        """Initialize the IgBLAST adapter."""
        super().__init__("igblast", "docker")
        self._logger = logging.getLogger(__name__)
        self._supported_blast_types = ["igblastn", "igblastp"]
        self._supported_organisms = self._discover_supported_organisms()

    def _find_executable(self) -> str:
        """Find the IgBLAST executable."""
        return "docker"

    def _validate_tool_installation(self) -> None:
        """Validate that IgBLAST is properly installed."""
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

    def _discover_supported_organisms(self) -> List[str]:
        """Discover supported organisms from database directory."""
        try:
            if not IGBLAST_INTERNAL_DATA_DIR.exists():
                self._logger.warning(
                    f"IgBLAST internal data directory not found: {IGBLAST_INTERNAL_DATA_DIR}"
                )
                return ["human", "mouse"]  # Default fallback

            organisms = []
            for item in IGBLAST_INTERNAL_DATA_DIR.iterdir():
                if item.is_dir():
                    organism_name = item.name

                    # Check for different naming patterns
                    # Human: airr_c_human_ig.V.nhr
                    # Mouse: mouse_gl_V.nhr
                    v_gene_file_human = (
                        item / f"airr_c_{organism_name}_ig.V.nhr"
                    )
                    v_gene_file_mouse = item / f"{organism_name}_gl_V.nhr"

                    if (
                        v_gene_file_human.exists()
                        or v_gene_file_mouse.exists()
                    ):
                        organisms.append(organism_name)

            if not organisms:
                self._logger.warning("No organism databases found")
                return ["human", "mouse"]

            self._logger.info(f"Discovered organisms: {organisms}")
            return organisms

        except Exception as e:
            self._logger.error(f"Error discovering organisms: {e}")
            return ["human", "mouse"]

    def _validate_sequence(self, sequence: str, blast_type: str) -> None:
        """Validate sequence format."""
        if not sequence:
            raise ValueError("Sequence cannot be empty")

        if blast_type == "igblastn":
            # Validate nucleotide sequence (A, C, G, T, N)
            if not re.match(r"^[ACGTNacgtn]+$", sequence):
                raise ValueError("Invalid nucleotide sequence")
        elif blast_type == "igblastp":
            # Validate protein sequence (standard amino acids)
            if not re.match(r"^[ACDEFGHIKLMNPQRSTVWY]+$", sequence):
                raise ValueError("Invalid protein sequence")

    def _detect_chain_type(self, sequence: str, organism: str) -> str:
        """
        Smart chain type detection using quick V gene scan.
        Determines if sequence is heavy or light chain based on V gene family.
        """
        try:
            # Quick V gene scan to determine chain type
            command = [
                "docker",
                "exec",
                "absequencealign-igblast",
                "igblastn",
                "-query",
                "/dev/stdin",
                "-organism",
                organism,
                "-outfmt",
                "7",  # Tabular format for quick parsing
                "-num_alignments_V",
                "1",  # Only need top V hit
            ]
            # Add V database only for quick scan (no D/J databases)
            if organism == "human":
                command.extend(
                    [
                        "-germline_db_V",
                        f"/data/internal_data/{organism}/airr_c_{organism}_ig.V",
                    ]
                )
            else:
                # Use actual database names for other organisms (mouse, etc.)
                # Mouse databases are named with 'gl' prefix: mouse_gl_V
                command.extend(
                    [
                        "-germline_db_V",
                        f"/data/internal_data/{organism}/{organism}_gl_V",
                    ]
                )

            # Execute quick scan
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate(
                input=f">query\n{sequence}\n", timeout=30
            )

            if process.returncode != 0:
                self._logger.warning(f"Chain type detection failed: {stderr}")
                return "unknown"
            self._logger.warning(f"Chain type detection output: {stdout}")

            # Parse V gene from output
            for line in stdout.split("\n"):
                if line.startswith("V\t") and "\t" in line:
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        v_gene = parts[2]
                        # Determine chain type based on V gene family
                        if v_gene.startswith("IGHV"):
                            return "heavy"
                        elif v_gene.startswith(("IGKV", "IGLV")):
                            return "light"
                        elif v_gene.startswith(
                            ("TRAV", "TRBV", "TRGV", "TRDV")
                        ):
                            return "tcr"
                        else:
                            return "unknown"

            return "unknown"

        except Exception as e:
            self._logger.warning(f"Chain type detection failed: {e}")
            return "unknown"

    def _build_command(self, **kwargs) -> List[str]:
        """Build IgBLAST command with smart database selection."""
        query_sequence = kwargs.get("query_sequence")
        organism = kwargs.get("organism")
        blast_type = kwargs.get("blast_type", "igblastn")
        use_airr_format = kwargs.get("use_airr_format", False)

        if not query_sequence:
            raise ValueError("query_sequence is required")
        if not organism:
            raise ValueError("organism is required")
        if blast_type not in self._supported_blast_types:
            raise ValueError(f"Unsupported IgBLAST type: {blast_type}")
        if organism not in self._supported_organisms:
            raise ValueError(f"Unsupported organism: {organism}")

        # Validate sequence
        self._validate_sequence(query_sequence, blast_type)

        # Build command
        command = [
            "docker",
            "exec",
            "absequencealign-igblast",
            blast_type,
            "-query",
            "/dev/stdin",
            "-organism",
            organism,
        ]

        # Choose output format
        if use_airr_format:
            command.extend(["-outfmt", "19"])  # AIRR format
        else:
            command.extend(["-outfmt", "7"])  # Tabular format

        # Add database paths based on organism and blast type
        if organism == "human":
            # Use actual database names for human (not symbolic links)
            command.extend(
                [
                    "-germline_db_V",
                    f"/data/internal_data/{organism}/airr_c_{organism}_ig.V",
                ]
            )

            if blast_type == "igblastn":
                command.extend(
                    [
                        "-germline_db_J",
                        f"/data/internal_data/{organism}/airr_c_{organism}_ig.J",
                        "-germline_db_D",
                        f"/data/internal_data/{organism}/airr_c_{organism}_igh.D",
                    ]
                )
        else:
            # Use actual database names for other organisms (mouse, etc.)
            # Mouse databases are named with 'gl' prefix: mouse_gl_V, mouse_gl_D, mouse_gl_J
            command.extend(
                [
                    "-germline_db_V",
                    f"/data/internal_data/{organism}/{organism}_gl_V",
                ]
            )

            if blast_type == "igblastn":
                command.extend(
                    [
                        "-germline_db_J",
                        f"/data/internal_data/{organism}/{organism}_gl_J",
                        "-germline_db_D",
                        f"/data/internal_data/{organism}/{organism}_gl_D",
                    ]
                )

        return command

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute IgBLAST with smart features."""
        try:
            command = self._build_command(**kwargs)
            self._logger.debug(f"Executing: {' '.join(command)}")

            query_sequence = kwargs.get("query_sequence")
            organism = kwargs.get("organism")
            blast_type = kwargs.get("blast_type", "igblastn")
            use_airr_format = kwargs.get("use_airr_format", False)
            enable_chain_detection = kwargs.get("enable_chain_detection", True)

            if not query_sequence:
                raise ValueError("query_sequence is required")

            # Execute with stdin piping
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate(
                input=f">query\n{query_sequence}\n",
                timeout=self._get_timeout(),
            )

            if process.returncode != 0:
                error_msg = f"IgBLAST execution failed with return code {process.returncode}"
                if stderr:
                    error_msg += f": {stderr}"
                raise ExternalToolError(error_msg, tool_name=self.tool_name)

            # Parse output based on format
            if use_airr_format:
                parsed_result = self._parse_airr_output(stdout, blast_type)
            else:
                parsed_result = self._parse_tabular_output(stdout, blast_type)

            # Add smart chain type detection if enabled
            if enable_chain_detection and blast_type == "igblastn":
                try:
                    detected_chain_type = self._detect_chain_type(
                        query_sequence, organism
                    )
                    parsed_result["detected_chain_type"] = detected_chain_type

                    # Update hits with detected chain type if not already present
                    for hit in parsed_result.get("hits", []):
                        if (
                            not hit.get("chain_type")
                            or hit["chain_type"] == "unknown"
                        ):
                            hit["chain_type"] = detected_chain_type
                except Exception as e:
                    self._logger.warning(
                        f"Chain type detection failed, continuing without it: {e}"
                    )
                    parsed_result["detected_chain_type"] = "unknown"

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
        return self._parse_tabular_output(output, blast_type)

    def _parse_tabular_output(
        self, output: str, blast_type: str
    ) -> Dict[str, Any]:
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
        current_hit = None

        for line in lines:
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
                continue

            if (
                line.startswith("V\t")
                or line.startswith("D\t")
                or line.startswith("J\t")
            ):
                # Parse hit information
                parts = line.split("\t")
                if len(parts) >= 13:
                    hit_type = parts[0]
                    query_id = parts[1]
                    subject_id = parts[2]
                    percent_identity = float(parts[3])
                    alignment_length = int(parts[4])
                    mismatches = int(parts[5])
                    gap_opens = int(parts[6])
                    gaps = int(parts[7])
                    q_start = int(parts[8])
                    q_end = int(parts[9])
                    s_start = int(parts[10])
                    s_end = int(parts[11])
                    evalue = float(parts[12])
                    bit_score = float(parts[13]) if len(parts) > 13 else 0.0

                    hit = {
                        "hit_type": hit_type,
                        "query_id": query_id,
                        "subject_id": subject_id,
                        "percent_identity": percent_identity,
                        "alignment_length": alignment_length,
                        "mismatches": mismatches,
                        "gap_opens": gap_opens,
                        "gaps": gaps,
                        "query_start": q_start,
                        "query_end": q_end,
                        "subject_start": s_start,
                        "subject_end": s_end,
                        "evalue": evalue,
                        "bit_score": bit_score,
                        "subject_url": self._get_subject_url(subject_id),
                    }

                    # Add gene information based on hit type
                    if hit_type == "V":
                        hit["v_gene"] = subject_id
                        hit["chain_type"] = ChainTypeUtils.extract_chain_type(
                            subject_id
                        )
                    elif hit_type == "D":
                        hit["d_gene"] = subject_id
                    elif hit_type == "J":
                        hit["j_gene"] = subject_id

                    result["hits"].append(hit)

            elif "V-(D)-J rearrangement summary" in line:
                # Parse rearrangement summary
                next_line = (
                    lines[lines.index(line) + 1]
                    if lines.index(line) + 1 < len(lines)
                    else ""
                )
                if next_line and not next_line.startswith("#"):
                    parts = next_line.split("\t")
                    if len(parts) >= 8:
                        result["analysis_summary"] = {
                            "v_gene": parts[0] if parts[0] != "N/A" else None,
                            "d_gene": parts[1] if parts[1] != "N/A" else None,
                            "j_gene": parts[2] if parts[2] != "N/A" else None,
                            "chain_type": (
                                parts[3] if parts[3] != "N/A" else None
                            ),
                            "stop_codon": (
                                parts[4] if parts[4] != "N/A" else None
                            ),
                            "v_j_frame": (
                                parts[5] if parts[5] != "N/A" else None
                            ),
                            "productive": (
                                parts[6] if parts[6] != "N/A" else None
                            ),
                            "strand": parts[7] if parts[7] != "N/A" else None,
                        }
            elif (
                not line.startswith("#")
                and "\t" in line
                and len(line.split("\t")) >= 8
            ):
                # Check if this is a rearrangement summary line (not a hit line)
                parts = line.split("\t")
                if parts[0] in [
                    "IGHV",
                    "IGKV",
                    "IGLV",
                    "TRAV",
                    "TRBV",
                    "TRGV",
                    "TRDV",
                ] or parts[0].startswith(
                    ("IGHV", "IGKV", "IGLV", "TRAV", "TRBV", "TRGV", "TRDV")
                ):
                    # This looks like a rearrangement summary line
                    if len(parts) >= 8:
                        result["analysis_summary"] = {
                            "v_gene": parts[0] if parts[0] != "N/A" else None,
                            "d_gene": parts[1] if parts[1] != "N/A" else None,
                            "j_gene": parts[2] if parts[2] != "N/A" else None,
                            "chain_type": (
                                parts[3] if parts[3] != "N/A" else None
                            ),
                            "stop_codon": (
                                parts[4] if parts[4] != "N/A" else None
                            ),
                            "v_j_frame": (
                                parts[5] if parts[5] != "N/A" else None
                            ),
                            "productive": (
                                parts[6] if parts[6] != "N/A" else None
                            ),
                            "strand": parts[7] if parts[7] != "N/A" else None,
                        }

            elif "CDR3" in line and "junction details" in line:
                # Parse CDR3 information
                next_line = (
                    lines[lines.index(line) + 1]
                    if lines.index(line) + 1 < len(lines)
                    else ""
                )
                if next_line and not next_line.startswith("#"):
                    # Extract CDR3 sequence from junction details
                    cdr3_match = re.search(r"([ACGT]+)", next_line)
                    if cdr3_match:
                        cdr3_sequence = cdr3_match.group(1)
                        result["analysis_summary"][
                            "cdr3_sequence"
                        ] = cdr3_sequence

                        # Try to find CDR3 position in query sequence
                        if "query_sequence" in result["query_info"]:
                            query_seq = result["query_info"]["query_sequence"]
                            cdr3_start = query_seq.find(cdr3_sequence)
                            if cdr3_start != -1:
                                result["analysis_summary"]["cdr3_start"] = (
                                    cdr3_start + 1
                                )
                                result["analysis_summary"]["cdr3_end"] = (
                                    cdr3_start + len(cdr3_sequence)
                                )

        result["total_hits"] = len(result["hits"])

        # If no analysis summary was found, try to extract from hits
        if not result["analysis_summary"] and result["hits"]:
            v_hits = [h for h in result["hits"] if h["hit_type"] == "V"]
            d_hits = [h for h in result["hits"] if h["hit_type"] == "D"]
            j_hits = [h for h in result["hits"] if h["hit_type"] == "J"]

            result["analysis_summary"] = {
                "v_gene": v_hits[0]["v_gene"] if v_hits else None,
                "d_gene": d_hits[0]["d_gene"] if d_hits else None,
                "j_gene": j_hits[0]["j_gene"] if j_hits else None,
                "chain_type": v_hits[0]["chain_type"] if v_hits else None,
                "stop_codon": None,
                "v_j_frame": None,
                "productive": None,
                "strand": None,
            }

        return result

    def _parse_airr_output(
        self, output: str, blast_type: str
    ) -> Dict[str, Any]:
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

        # Parse AIRR format (JSON-like structure)
        for line in lines:
            if line.startswith("{") and line.endswith("}"):
                try:
                    import json

                    airr_record = json.loads(line)

                    # Extract key information from AIRR record
                    hit = {
                        "v_gene": airr_record.get("v_call", "N/A"),
                        "d_gene": airr_record.get("d_call", "N/A"),
                        "j_gene": airr_record.get("j_call", "N/A"),
                        "chain_type": airr_record.get("locus", "N/A"),
                        "productive": airr_record.get("productive", "N/A"),
                        "cdr3_sequence": airr_record.get("cdr3", "N/A"),
                        "cdr3_start": airr_record.get("cdr3_start", None),
                        "cdr3_end": airr_record.get("cdr3_end", None),
                        "v_identity": airr_record.get("v_identity", 0.0),
                        "j_identity": airr_record.get("j_identity", 0.0),
                        "d_identity": airr_record.get("d_identity", 0.0),
                        "subject_url": self._get_subject_url(
                            airr_record.get("v_call", "")
                        ),
                    }

                    result["hits"].append(hit)
                    result["airr_data"] = airr_record

                except json.JSONDecodeError:
                    self._logger.warning(f"Failed to parse AIRR line: {line}")
                    continue

        result["total_hits"] = len(result["hits"])

        # Extract summary information from first hit
        if result["hits"]:
            first_hit = result["hits"][0]
            result["analysis_summary"] = {
                "v_gene": first_hit["v_gene"],
                "d_gene": first_hit["d_gene"],
                "j_gene": first_hit["j_gene"],
                "chain_type": first_hit["chain_type"],
                "productive": first_hit["productive"],
                "cdr3_sequence": first_hit["cdr3_sequence"],
            }

        return result

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

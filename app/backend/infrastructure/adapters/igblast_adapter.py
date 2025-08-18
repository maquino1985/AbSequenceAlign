"""
IgBLAST adapter for immunoglobulin and T-cell receptor sequence analysis.
Implements the ExternalToolAdapter interface to provide a clean abstraction.
IgBLAST is specifically designed for antibody and TCR sequence analysis.
"""

import subprocess
import tempfile
import os
from typing import Dict, Any, List, Optional
import logging

from backend.infrastructure.adapters.base_adapter import (
    BaseExternalToolAdapter,
)
from backend.core.exceptions import ExternalToolError
from backend.config import (
    IGBLAST_INTERNAL_DATA_DIR,
    get_igblast_v_db_path,
    get_igblast_d_db_path,
    get_igblast_j_db_path,
    get_igblast_c_db_path,
)
from backend.infrastructure.parsers.airr_parser import AIRRParser


class IgBlastAdapter(BaseExternalToolAdapter):
    """Adapter for the IgBLAST tool for immunoglobulin and TCR sequence analysis"""

    def __init__(self, docker_client=None):
        # Initialize Docker client if not provided
        if docker_client is None:
            try:
                import docker

                self.docker_client = docker.from_env()
            except ImportError:
                self._logger = logging.getLogger(f"{self.__class__.__name__}")
                self._logger.warning("Docker Python package not available")
                self.docker_client = None
            except Exception as e:
                self._logger = logging.getLogger(f"{self.__class__.__name__}")
                self._logger.warning(
                    f"Could not initialize Docker client: {e}"
                )
                self.docker_client = None
        else:
            self.docker_client = docker_client

        self._supported_blast_types = ["igblastn", "igblastp"]
        super().__init__("igblast")
        self._logger = logging.getLogger(f"{self.__class__.__name__}")
        self._supported_organisms = self._discover_supported_organisms()
        self._airr_parser = AIRRParser()

    def _discover_supported_organisms(self) -> List[str]:
        """Dynamically discover supported organisms from the database directory"""
        try:
            if not IGBLAST_INTERNAL_DATA_DIR.exists():
                self._logger.warning(
                    f"IgBLAST internal data directory not found: {IGBLAST_INTERNAL_DATA_DIR}"
                )
                return ["human", "mouse"]  # Default fallback

            # Look for organism subdirectories
            organisms = []
            for item in IGBLAST_INTERNAL_DATA_DIR.iterdir():
                if item.is_dir():
                    organism_name = item.name
                    # Check for both naming patterns: {organism}_V.nhr and {organism}_gl_V.nhr
                    v_gene_file = item / f"{organism_name}_V.nhr"
                    v_gene_file_gl = item / f"{organism_name}_gl_V.nhr"
                    if v_gene_file.exists() or v_gene_file_gl.exists():
                        organisms.append(organism_name)

            if not organisms:
                self._logger.warning(
                    "No organism databases found in IgBLAST internal data directory"
                )
                return ["human", "mouse"]  # Default fallback

            self._logger.info(f"Discovered supported organisms: {organisms}")
            return organisms

        except Exception as e:
            self._logger.error(f"Error discovering supported organisms: {e}")
            return ["human", "mouse"]  # Default fallback

    def _check_c_gene_db_exists(self, organism: str) -> bool:
        """Check if C gene database exists for the given organism"""
        try:
            # Check for common C gene database naming patterns
            c_db_path = get_igblast_c_db_path(organism)

            # Check if the database files exist
            if c_db_path.exists():
                # Check for the main database file (.nhr)
                nhr_file = c_db_path.with_suffix(".nhr")
                if nhr_file.exists():
                    self._logger.debug(
                        f"C gene database found for {organism}: {nhr_file}"
                    )
                    return True

            # Check for alternative naming patterns
            alt_patterns = [
                f"{organism}_C.nhr",
                f"{organism}_gl_C.nhr",
                f"ncbi_{organism}_c_genes.nhr",
                f"airr_c_{organism}.nhr",
            ]

            # For mouse, also check for strain-specific databases
            if organism == "mouse":
                alt_patterns.extend(
                    [
                        "airr_c_C57BL_6J.V.nhr",
                        "airr_c_C57BL_6.V.nhr",
                        "airr_c_BALB_c_ByJ.V.nhr",
                        "airr_c_BALB_c.V.nhr",
                    ]
                )

            for pattern in alt_patterns:
                alt_path = IGBLAST_INTERNAL_DATA_DIR / pattern
                if alt_path.exists():
                    self._logger.debug(
                        f"C gene database found for {organism} (alternative): {alt_path}"
                    )
                    return True

            self._logger.debug(f"C gene database not found for {organism}")
            return False

        except Exception as e:
            self._logger.warning(
                f"Error checking C gene database for {organism}: {e}"
            )
            return False

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
                "-v",
                f"{IGBLAST_INTERNAL_DATA_DIR.resolve()}:/blast/internal_data:ro",
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

        # Add germline database parameters based on organism and BLAST type
        if organism in self._supported_organisms:
            # Get database paths from configuration
            v_db_path = get_igblast_v_db_path(organism)
            command.extend(
                [
                    "-germline_db_V",
                    f"/blast/internal_data/{v_db_path.relative_to(IGBLAST_INTERNAL_DATA_DIR)}",
                ]
            )

            # D and J gene databases are only used for nucleotide searches
            if blast_type == "igblastn":
                d_db_path = get_igblast_d_db_path(organism)
                j_db_path = get_igblast_j_db_path(organism)
                c_db_path = get_igblast_c_db_path(organism)

                command.extend(
                    [
                        "-germline_db_D",
                        f"/blast/internal_data/{d_db_path.relative_to(IGBLAST_INTERNAL_DATA_DIR)}",
                    ]
                )
                command.extend(
                    [
                        "-germline_db_J",
                        f"/blast/internal_data/{j_db_path.relative_to(IGBLAST_INTERNAL_DATA_DIR)}",
                    ]
                )

                # Add constant region database for C gene detection only if it exists
                # Check if the C gene database files exist in the Docker container
                c_db_exists = self._check_c_gene_db_exists(organism)
                if c_db_exists:
                    command.extend(
                        [
                            "-c_region_db",
                            f"/blast/internal_data/{c_db_path.relative_to(IGBLAST_INTERNAL_DATA_DIR)}",
                        ]
                    )
                    self._logger.debug(
                        f"Using C region database for {organism}: {c_db_path}"
                    )
                else:
                    self._logger.warning(
                        f"C gene database not available for {organism}. C gene detection will be disabled."
                    )
            else:
                self._logger.debug(
                    f"Protein search - C gene detection not available for {blast_type}"
                )
        else:
            raise ValueError(
                f"Organism '{organism}' is not supported. Available organisms: {self._supported_organisms}"
            )

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
            # Use AIRR format for nucleotide searches (has gene assignments)
            # Use default tabular format for protein searches (AIRR not supported)
            if blast_type == "igblastn":
                command.extend(["-outfmt", "19"])  # AIRR format
                self._logger.info(
                    "Using AIRR format (outfmt 19) for IgBLAST nucleotide search"
                )
            else:
                command.extend(["-outfmt", "7"])  # Default tabular format
                self._logger.info(
                    "Using tabular format (outfmt 7) for IgBLAST protein search - AIRR not supported"
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

    def _get_igblast_subject_url(self, subject_id: str) -> str:
        """
        Generate a URL to the source database entry for IgBLAST gene assignments.

        Args:
            subject_id: The gene name from IgBLAST results (e.g., "IGHV3-9*01")

        Returns:
            URL to the source database entry
        """
        if not subject_id:
            return ""

        # Handle IMGT gene names (most common for IgBLAST)
        if subject_id.startswith(
            (
                "IGHV",
                "IGHD",
                "IGHJ",
                "IGHC",
                "IGKV",
                "IGKJ",
                "IGKC",
                "IGLV",
                "IGLJ",
                "IGLC",
            )
        ):
            # Extract the gene family and number
            # e.g., "IGHV3-9*01" -> "IGHV3-9"
            gene_family = subject_id.split("*")[0]
            return f"https://www.imgt.org/IMGTrepertoire/Proteins/protein.php?species=Homo%20sapiens&group=IGH&receptor_type=IGH&type=V&prototype={gene_family}"

        # Handle other gene naming conventions
        elif subject_id.startswith(
            ("TRBV", "TRBD", "TRBJ", "TRBC", "TRAV", "TRAJ", "TRAC")
        ):
            # T-cell receptor genes
            gene_family = subject_id.split("*")[0]
            return f"https://www.imgt.org/IMGTrepertoire/Proteins/protein.php?species=Homo%20sapiens&group=TR&receptor_type=TR&type=V&prototype={gene_family}"

        # Default fallback - search IMGT database
        else:
            return f"https://www.imgt.org/IMGTrepertoire/Proteins/protein.php?species=Homo%20sapiens&group=IGH&receptor_type=IGH&type=V&prototype={subject_id}"

        return ""

    def _parse_output(self, output: str, **kwargs) -> Dict[str, Any]:
        """Parse IgBLAST output"""
        blast_type = kwargs.get("blast_type", "igblastn")
        outfmt = kwargs.get("outfmt", "7")

        if outfmt == "7" or outfmt == "19":
            return self._parse_tabular_output(output, blast_type)
        else:
            return self._parse_standard_output(output, blast_type)

    def _parse_tabular_output(
        self, output: str, blast_type: str
    ) -> Dict[str, Any]:
        """Parse IgBLAST output (AIRR for nucleotide, tabular for protein)"""

        if blast_type == "igblastn":
            return self._parse_airr_output(output, blast_type)
        else:
            return self._parse_default_tabular_output(output, blast_type)

    def _parse_airr_output(
        self, output: str, blast_type: str
    ) -> Dict[str, Any]:
        """Parse IgBLAST AIRR format output (outfmt 19) using advanced parser"""

        self._logger.info(f"Parsing AIRR output for {blast_type}")
        self._logger.debug(f"AIRR output length: {len(output)} characters")

        if not output.strip():
            self._logger.warning("Empty AIRR output received")
            return self._parse_airr_output_fallback(output, blast_type)

        try:
            # Use the advanced AIRR parser
            airr_result = self._airr_parser.parse_airr_output(output)

            self._logger.info(
                f"Successfully parsed AIRR output: {len(airr_result.rearrangements)} rearrangements"
            )

            # Convert to backward-compatible format for existing API
            hits = []
            query_info = {}

            for rearrangement in airr_result.rearrangements:
                # Convert advanced AIRR data to legacy hit format for backward compatibility
                hit = self._convert_rearrangement_to_hit(rearrangement)
                hits.append(hit)

                # Use first rearrangement for query info
                if not query_info:
                    query_info["query_id"] = rearrangement.sequence_id

            # Create analysis summary with enhanced data
            analysis_summary = self._create_enhanced_analysis_summary(
                airr_result
            )

            result = {
                "blast_type": blast_type,
                "query_info": query_info,
                "hits": hits,
                "analysis_summary": analysis_summary,
                "total_hits": len(hits),
                # Include the full AIRR result for advanced users
                "airr_result": (
                    airr_result.model_dump()
                    if airr_result.rearrangements
                    else None
                ),
            }

            self._logger.info(
                f"Successfully processed AIRR data: {len(hits)} hits, AIRR result: {result['airr_result'] is not None}"
            )
            return result

        except Exception as e:
            self._logger.error(
                f"Error parsing AIRR output with advanced parser: {e}"
            )
            self._logger.error(f"AIRR output preview: {output[:500]}...")
            # Fallback to basic parsing
            return self._parse_airr_output_fallback(output, blast_type)

    def _convert_rearrangement_to_hit(self, rearrangement) -> Dict[str, Any]:
        """Convert advanced AIRR rearrangement to legacy hit format"""

        # Extract CDR3 information from junction region
        cdr3_sequence = None
        cdr3_start = None
        cdr3_end = None

        if rearrangement.junction_region:
            # Try to extract CDR3 from various sources
            cdr3_sequence = (
                rearrangement.junction_region.cdr3
                or rearrangement.junction_region.cdr3_aa
                or rearrangement.junction_region.junction
                or rearrangement.junction_region.junction_aa
            )
            cdr3_start = rearrangement.junction_region.cdr3_start
            cdr3_end = rearrangement.junction_region.cdr3_end

            # If CDR3 sequence is not directly available, try to construct it from N regions
            if not cdr3_sequence and rearrangement.junction_region.np1:
                np1 = rearrangement.junction_region.np1 or ""
                np2 = rearrangement.junction_region.np2 or ""
                if np1 or np2:
                    cdr3_sequence = f"{np1}{np2}"

            # If CDR3 positions are not available, estimate from V and J gene positions
            if (
                cdr3_start is None
                and rearrangement.v_sequence_end
                and rearrangement.j_sequence_start
            ):
                cdr3_start = rearrangement.v_sequence_end + 1
            if cdr3_end is None and rearrangement.j_sequence_start:
                cdr3_end = rearrangement.j_sequence_start - 1

        # Calculate alignment length from V gene alignment
        alignment_length = 0
        if (
            rearrangement.v_alignment
            and rearrangement.v_alignment.start
            and rearrangement.v_alignment.end
        ):
            alignment_length = (
                rearrangement.v_alignment.end
                - rearrangement.v_alignment.start
                + 1
            )
        elif rearrangement.v_sequence_start and rearrangement.v_sequence_end:
            alignment_length = (
                rearrangement.v_sequence_end
                - rearrangement.v_sequence_start
                + 1
            )

        return {
            "query_id": rearrangement.sequence_id,
            "subject_id": rearrangement.v_call or "",
            "subject_url": self._get_igblast_subject_url(
                rearrangement.v_call or ""
            ),
            "identity": (
                rearrangement.v_alignment.identity
                if rearrangement.v_alignment
                else 0.0
            ),
            "alignment_length": alignment_length,
            "mismatches": 0,  # Not directly available in AIRR
            "gap_opens": 0,  # Not directly available in AIRR
            "query_start": rearrangement.v_sequence_start or 0,
            "query_end": rearrangement.v_sequence_end or 0,
            "subject_start": rearrangement.v_germline_start or 0,
            "subject_end": rearrangement.v_germline_end or 0,
            "evalue": 0.0,  # Not directly available in AIRR
            "bit_score": (
                rearrangement.v_alignment.score
                if rearrangement.v_alignment
                else 0.0
            ),
            "v_gene": rearrangement.v_call,
            "d_gene": rearrangement.d_call,
            "j_gene": rearrangement.j_call,
            "c_gene": rearrangement.c_call,
            "cdr3_start": cdr3_start,
            "cdr3_end": cdr3_end,
            "cdr3_sequence": cdr3_sequence,
            # Add advanced fields for enhanced analysis
            "productive": (
                str(rearrangement.productive.value)
                if rearrangement.productive
                else None
            ),
            "locus": (
                str(rearrangement.locus.value) if rearrangement.locus else None
            ),
            "complete_vdj": rearrangement.complete_vdj,
            "stop_codon": rearrangement.stop_codon,
            "vj_in_frame": rearrangement.vj_in_frame,
        }

    def _create_enhanced_analysis_summary(self, airr_result) -> Dict[str, Any]:
        """Create enhanced analysis summary from AIRR result"""

        if not airr_result.rearrangements:
            return {"total_hits": 0}

        # Use the first (best) rearrangement for summary
        best = airr_result.rearrangements[0]

        summary = {
            "best_v_gene": best.v_call,
            "best_d_gene": best.d_call,
            "best_j_gene": best.j_call,
            "best_c_gene": best.c_call,
            "total_hits": len(airr_result.rearrangements),
            # Enhanced summary information
            "productive_sequences": airr_result.productive_sequences,
            "unique_v_genes": airr_result.unique_v_genes,
            "unique_d_genes": airr_result.unique_d_genes,
            "unique_j_genes": airr_result.unique_j_genes,
            "locus": str(best.locus.value) if best.locus else None,
        }

        # Add CDR3 information
        if best.junction_region:
            summary.update(
                {
                    "cdr3_sequence": (
                        best.junction_region.cdr3
                        or best.junction_region.junction
                        or best.junction_region.np2
                    ),
                    "cdr3_start": best.junction_region.cdr3_start,
                    "cdr3_end": best.junction_region.cdr3_end,
                    "junction_length": best.junction_region.junction_length,
                    "cdr3_aa": best.junction_region.cdr3_aa,
                    "junction_aa": best.junction_region.junction_aa,
                }
            )

        # Add framework and CDR region information
        if best.fwr1:
            summary["fwr1_sequence"] = best.fwr1.sequence_aa
        if best.cdr1:
            summary["cdr1_sequence"] = best.cdr1.sequence_aa
        if best.fwr2:
            summary["fwr2_sequence"] = best.fwr2.sequence_aa
        if best.cdr2:
            summary["cdr2_sequence"] = best.cdr2.sequence_aa
        if best.fwr3:
            summary["fwr3_sequence"] = best.fwr3.sequence_aa

        return summary

    def _parse_default_tabular_output(
        self, output: str, blast_type: str
    ) -> Dict[str, Any]:
        """Parse default IgBLAST tabular output (outfmt 7) for protein searches"""
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

            # Default IgBLAST format: chain_type, qseqid, sseqid, pident, length, mismatch, gapopen, gaps, qstart, qend, sstart, send, evalue, bitscore
            min_fields = 14

            if len(fields) >= min_fields:
                hit = {
                    "query_id": fields[1],  # qseqid
                    "subject_id": fields[2],  # sseqid
                    "identity": float(fields[3]),  # pident
                    "alignment_length": int(fields[4]),  # length
                    "mismatches": int(fields[5]),  # mismatch
                    "gap_opens": int(fields[6]),  # gapopen
                    "query_start": int(fields[8]),  # qstart (skip gaps field)
                    "query_end": int(fields[9]),  # qend
                    "subject_start": int(fields[10]),  # sstart
                    "subject_end": int(fields[11]),  # send
                    "evalue": float(fields[12]),  # evalue
                    "bit_score": float(fields[13]),  # bitscore
                    "v_gene": (
                        fields[2] if fields[0] == "V" else None
                    ),  # Use subject_id for V gene
                }

                # For protein searches, limited gene assignment info available
                hit["d_gene"] = None  # Not applicable for protein searches
                hit["j_gene"] = (
                    None  # Not easily extractable from tabular format
                )
                hit["c_gene"] = (
                    None  # Not easily extractable from tabular format
                )
                hit["cdr3_start"] = None
                hit["cdr3_end"] = None
                hit["cdr3_sequence"] = None

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
        """Validate input sequence (case insensitive)"""
        if not sequence or not isinstance(sequence, str):
            raise ValueError("Sequence must be a non-empty string")

        # Clean and normalize sequence (case insensitive)
        # Remove newlines, spaces, tabs, and other whitespace
        sequence_clean = "".join(sequence.split()).upper()

        if not sequence_clean:
            raise ValueError("Sequence cannot be empty after cleaning")

        if blast_type == "igblastn":
            # DNA/RNA sequence validation - support both DNA (ATGC) and RNA (ATGCU)
            valid_nt = set("ATGCUN")  # N for ambiguous nucleotides
            invalid_chars = set(sequence_clean) - valid_nt
            if invalid_chars:
                raise ValueError(
                    f"Invalid nucleotide characters: {invalid_chars}"
                )
        elif blast_type == "igblastp":
            # Protein sequence validation
            valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
            invalid_chars = set(sequence_clean) - valid_aa
            if invalid_chars:
                raise ValueError(
                    f"Invalid amino acid characters: {invalid_chars}"
                )

    def _create_query_file(self, sequence: str) -> str:
        """Create a temporary FASTA file for the query sequence"""
        # Clean the sequence before writing to file
        clean_sequence = "".join(sequence.split()).upper()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as f:
            f.write(f">query\n{clean_sequence}\n")
            return f.name

    def get_supported_organisms(self) -> List[str]:
        """Get list of supported organisms"""
        return self._supported_organisms.copy()

    def get_supported_blast_types(self) -> List[str]:
        """Get list of supported IgBLAST types"""
        return self._supported_blast_types.copy()

    def _parse_airr_output_fallback(
        self, output: str, blast_type: str
    ) -> Dict[str, Any]:
        """Fallback AIRR parsing method using the original logic"""
        lines = output.strip().split("\n")
        hits = []
        query_info = {}
        analysis_summary = {}

        if len(lines) < 2:  # Need at least header + data
            return {
                "blast_type": blast_type,
                "query_info": query_info,
                "hits": hits,
                "analysis_summary": analysis_summary,
                "total_hits": 0,
            }

        # First line is header, second line is data
        header = lines[0].split("\t")

        # Find the data line (skip empty lines)
        data_line = None
        for line in lines[1:]:
            if line.strip():
                data_line = line.split("\t")
                break

        if not data_line:
            return {
                "blast_type": blast_type,
                "query_info": query_info,
                "hits": hits,
                "analysis_summary": analysis_summary,
                "total_hits": 0,
            }

        # Pad data_line with empty strings if it's shorter than header
        while len(data_line) < len(header):
            data_line.append("")

        # Create a dictionary from header and data
        airr_data = dict(zip(header, data_line))

        # Extract query info
        query_info["query_id"] = airr_data.get("sequence_id", "")

        # Convert AIRR format to our hit format
        hit = {
            "query_id": airr_data.get("sequence_id", ""),
            "subject_id": airr_data.get("v_call", ""),
            "identity": (
                float(airr_data.get("v_identity", 0))
                if airr_data.get("v_identity")
                else 0.0
            ),
            "alignment_length": (
                int(airr_data.get("v_alignment_end", 0))
                - int(airr_data.get("v_alignment_start", 0))
                + 1
                if airr_data.get("v_alignment_start")
                and airr_data.get("v_alignment_end")
                else 0
            ),
            "mismatches": 0,  # Not directly available in AIRR
            "gap_opens": 0,  # Not directly available in AIRR
            "query_start": (
                int(airr_data.get("v_sequence_start", 0))
                if airr_data.get("v_sequence_start")
                else 0
            ),
            "query_end": (
                int(airr_data.get("v_sequence_end", 0))
                if airr_data.get("v_sequence_end")
                else 0
            ),
            "subject_start": (
                int(airr_data.get("v_germline_start", 0))
                if airr_data.get("v_germline_start")
                else 0
            ),
            "subject_end": (
                int(airr_data.get("v_germline_end", 0))
                if airr_data.get("v_germline_end")
                else 0
            ),
            "evalue": 0.0,  # Not directly available in AIRR
            "bit_score": (
                float(airr_data.get("v_score", 0))
                if airr_data.get("v_score")
                else 0.0
            ),
            "v_gene": (
                airr_data.get("v_call") if airr_data.get("v_call") else None
            ),
            "d_gene": (
                airr_data.get("d_call") if airr_data.get("d_call") else None
            ),
            "j_gene": (
                airr_data.get("j_call") if airr_data.get("j_call") else None
            ),
            "c_gene": (
                airr_data.get("c_call") if airr_data.get("c_call") else None
            ),
            "cdr3_start": self._extract_cdr3_start(airr_data),
            "cdr3_end": self._extract_cdr3_end(airr_data),
            # CDR3 sequence is often in the junction field or np2 field for IgBLAST
            "cdr3_sequence": (
                airr_data.get("junction")
                or airr_data.get("cdr3")
                or airr_data.get("np2")
                or None
            ),
        }

        hits.append(hit)

        # Create analysis summary
        analysis_summary = {
            "best_v_gene": hit.get("v_gene"),
            "best_d_gene": hit.get("d_gene"),
            "best_j_gene": hit.get("j_gene"),
            "best_c_gene": hit.get("c_gene"),
            "cdr3_sequence": hit.get("cdr3_sequence"),
            "cdr3_start": hit.get("cdr3_start"),
            "cdr3_end": hit.get("cdr3_end"),
            "total_hits": len(hits),
        }

        return {
            "blast_type": blast_type,
            "query_info": query_info,
            "hits": hits,
            "analysis_summary": analysis_summary,
            "total_hits": len(hits),
        }

    def _extract_cdr3_start(self, airr_data: Dict[str, str]) -> Optional[int]:
        """Extract CDR3 start position from AIRR data."""
        # Try direct field first
        if airr_data.get("cdr3_start") and airr_data.get("cdr3_start").strip():
            try:
                return int(airr_data["cdr3_start"])
            except (ValueError, TypeError):
                pass

        # Try to infer from other position fields
        # CDR3 typically starts after FWR3 ends
        fwr3_end = airr_data.get("fwr3_end")
        if fwr3_end and fwr3_end.strip():
            try:
                return int(fwr3_end) + 1
            except (ValueError, TypeError):
                pass

        # Try to use V gene end position as approximation
        v_end = airr_data.get("v_sequence_end")
        if v_end and v_end.strip():
            try:
                # CDR3 usually starts near the end of V gene
                return int(v_end) - 10  # Approximate offset
            except (ValueError, TypeError):
                pass

        return None

    def _extract_cdr3_end(self, airr_data: Dict[str, str]) -> Optional[int]:
        """Extract CDR3 end position from AIRR data."""
        # Try direct field first
        if airr_data.get("cdr3_end") and airr_data.get("cdr3_end").strip():
            try:
                return int(airr_data["cdr3_end"])
            except (ValueError, TypeError):
                pass

        # Try to infer from other position fields
        # CDR3 typically ends before FWR4 starts
        fwr4_start = airr_data.get("fwr4_start")
        if fwr4_start and fwr4_start.strip():
            try:
                return int(fwr4_start) - 1
            except (ValueError, TypeError):
                pass

        # Try to use J gene start position as approximation
        j_start = airr_data.get("j_sequence_start")
        if j_start and j_start.strip():
            try:
                # CDR3 usually ends near the start of J gene
                return int(j_start) + 10  # Approximate offset
            except (ValueError, TypeError):
                pass

        # Try to calculate from CDR3 start + junction length
        cdr3_start = self._extract_cdr3_start(airr_data)
        junction_length = airr_data.get("junction_length")
        if (
            cdr3_start is not None
            and junction_length
            and junction_length.strip()
        ):
            try:
                return cdr3_start + int(junction_length) - 1
            except (ValueError, TypeError):
                pass

        return None

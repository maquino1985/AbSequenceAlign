"""
HMMER adapter for isotype detection and constant region analysis.
Implements the ExternalToolAdapter interface to provide a clean abstraction.
"""

import subprocess
import tempfile
import os
from typing import Dict, Any, List, Optional
import logging

from ...core.base_classes import AbstractExternalToolAdapter
from ...core.exceptions import (
    HmmerError,
)


class HmmerAdapter(AbstractExternalToolAdapter):
    """Adapter for the HMMER tool for isotype detection"""

    def __init__(self, hmm_dir: Optional[str] = None):
        super().__init__("hmmer")
        self._logger = logging.getLogger(f"{self.__class__.__name__}")
        self.hmm_dir = hmm_dir or self._get_default_hmm_dir()
        self._supported_isotypes = [
            "IGHG1",
            "IGHG2",
            "IGHG3",
            "IGHG4",
            "IGHA1",
            "IGHA2",
            "IGHD",
            "IGHE",
            "IGHM",
        ]

    def _check_availability(self) -> bool:
        """Check if HMMER is available on the system"""
        try:
            result = subprocess.run(
                ["hmmsearch", "--help"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            self._logger.warning("HMMER not available via command line")
            return False

    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute HMMER on the input sequence"""
        if not self._validate_input(input_data):
            raise HmmerError("Invalid input data", tool_name=self.tool_name)

        try:
            # Parse input data (expecting FASTA format)
            sequence = self._parse_fasta_sequence(input_data)

            # Detect isotype
            isotype_result = self._detect_isotype(sequence)

            return self._create_result(True, data=isotype_result)

        except Exception as e:
            raise HmmerError(
                f"HMMER execution failed: {str(e)}", tool_name=self.tool_name
            )

    def detect_isotype(self, sequence: str) -> Dict[str, Any]:
        """Detect antibody isotype using HMMER"""
        if not self._validate_sequence(sequence):
            raise HmmerError("Invalid sequence", tool_name=self.tool_name)

        try:
            return self._detect_isotype(sequence)
        except Exception as e:
            raise HmmerError(
                f"Isotype detection failed: {str(e)}", tool_name=self.tool_name
            )

    def _get_default_hmm_dir(self) -> str:
        """Get the default HMM directory"""
        # Try to get from environment variable
        hmm_dir = os.environ.get("ISOTYPE_HMM_DIR")
        if hmm_dir and os.path.exists(hmm_dir):
            return hmm_dir

        # Try common locations
        common_paths = [
            "/usr/local/share/hmmer/isotype_hmms",
            "/opt/hmmer/isotype_hmms",
            "./data/isotype_hmms",
            "./app/backend/data/isotype_hmms",
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        # Return a default path (will be validated later)
        return "./data/isotype_hmms"

    def _validate_sequence(self, sequence: str) -> bool:
        """Validate that the sequence is suitable for isotype detection"""
        if not sequence or not isinstance(sequence, str):
            return False

        # Check for valid amino acids
        valid_chars = set("ACDEFGHIKLMNPQRSTVWYX")
        if not all(char.upper() in valid_chars for char in sequence):
            return False

        # Check minimum length for isotype detection
        if len(sequence) < 50:
            return False

        return True

    def _parse_fasta_sequence(self, fasta_data: str) -> str:
        """Parse FASTA format and extract sequence"""
        lines = fasta_data.strip().split("\n")
        sequence_lines = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith(">"):
                sequence_lines.append(line)

        if not sequence_lines:
            raise HmmerError(
                "No sequence found in FASTA data", tool_name=self.tool_name
            )

        return "".join(sequence_lines)

    def _detect_isotype(self, sequence: str) -> Dict[str, Any]:
        """Detect isotype using HMMER"""
        if not os.path.exists(self.hmm_dir):
            raise HmmerError(
                f"HMM directory not found: {self.hmm_dir}",
                tool_name=self.tool_name,
            )

        # Create temporary FASTA file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as fasta_file:
            fasta_file.write(f">query\n{sequence}\n")
            fasta_path = fasta_file.name

        try:
            best_isotype = None
            best_score = float("-inf")
            best_evalue = float("inf")
            all_results = []

            # Test against each isotype HMM
            for isotype in self._supported_isotypes:
                hmm_file = os.path.join(self.hmm_dir, f"{isotype}.hmm")

                if not os.path.exists(hmm_file):
                    self._logger.debug(f"HMM file not found: {hmm_file}")
                    continue

                try:
                    result = self._run_hmmsearch(fasta_path, hmm_file, isotype)
                    all_results.append(result)

                    # Update best result
                    if result["score"] > best_score:
                        best_score = result["score"]
                        best_evalue = result["evalue"]
                        best_isotype = isotype

                except Exception as e:
                    self._logger.warning(f"Failed to process {isotype}: {e}")
                    continue

            # Clean up temporary file
            os.unlink(fasta_path)

            return {
                "best_isotype": best_isotype,
                "best_score": best_score,
                "best_evalue": best_evalue,
                "all_results": all_results,
                "sequence_length": len(sequence),
            }

        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(fasta_path):
                os.unlink(fasta_path)
            raise e

    def _run_hmmsearch(
        self, fasta_path: str, hmm_path: str, isotype: str
    ) -> Dict[str, Any]:
        """Run hmmsearch command"""
        try:
            cmd = [
                "hmmsearch",
                "--domtblout",
                "/dev/stdout",  # Output to stdout
                "--noali",  # Don't output alignments
                hmm_path,
                fasta_path,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
            )

            if result.returncode != 0:
                raise HmmerError(
                    f"hmmsearch failed for {isotype}: {result.stderr}",
                    tool_name=self.tool_name,
                    command=" ".join(cmd),
                    exit_code=result.returncode,
                    stderr=result.stderr,
                )

            # Parse hmmsearch output
            return self._parse_hmmsearch_output(result.stdout, isotype)

        except subprocess.TimeoutExpired:
            raise HmmerError(
                f"hmmsearch timeout for {isotype}",
                tool_name=self.tool_name,
                command=" ".join(cmd),
            )
        except Exception as e:
            raise HmmerError(
                f"hmmsearch execution failed for {isotype}: {str(e)}",
                tool_name=self.tool_name,
            )

    def _parse_hmmsearch_output(
        self, output: str, isotype: str
    ) -> Dict[str, Any]:
        """Parse hmmsearch domain table output"""
        lines = output.strip().split("\n")

        # Skip comment lines
        data_lines = [line for line in lines if not line.startswith("#")]

        if not data_lines:
            return {
                "isotype": isotype,
                "score": float("-inf"),
                "evalue": float("inf"),
                "domains": [],
            }

        # Parse the first (best) hit
        # Format: target_name target_accession query_name query_accession hmm_from
        # hmm_to
        # ali_from ali_to env_from env_to modlen description_of_target domain_score
        # domain_bias domain_evalue domain_ievalue domain_cevalue domain_best_score
        # domain_best_bias domain_best_evalue domain_best_ievalue domain_best_cevalue
        fields = data_lines[0].split()

        if len(fields) < 22:
            return {
                "isotype": isotype,
                "score": float("-inf"),
                "evalue": float("inf"),
                "domains": [],
            }

        try:
            score = float(fields[13])  # domain_score
            evalue = float(fields[12])  # domain_evalue
            hmm_from = int(fields[5])  # hmm_from
            hmm_to = int(fields[6])  # hmm_to
            ali_from = int(fields[7])  # ali_from
            ali_to = int(fields[8])  # ali_to

            return {
                "isotype": isotype,
                "score": score,
                "evalue": evalue,
                "hmm_range": (hmm_from, hmm_to),
                "alignment_range": (ali_from, ali_to),
                "domains": [
                    {
                        "score": score,
                        "evalue": evalue,
                        "hmm_range": (hmm_from, hmm_to),
                        "alignment_range": (ali_from, ali_to),
                    }
                ],
            }

        except (ValueError, IndexError) as e:
            self._logger.warning(
                f"Failed to parse hmmsearch output for {isotype}: {e}"
            )
            return {
                "isotype": isotype,
                "score": float("-inf"),
                "evalue": float("inf"),
                "domains": [],
            }

    def get_supported_isotypes(self) -> List[str]:
        """Get list of supported isotypes"""
        return self._supported_isotypes.copy()

    def set_hmm_directory(self, hmm_dir: str) -> None:
        """Set the HMM directory"""
        if not os.path.exists(hmm_dir):
            raise HmmerError(
                f"HMM directory does not exist: {hmm_dir}",
                tool_name=self.tool_name,
            )
        self.hmm_dir = hmm_dir

    def validate_hmm_files(self) -> Dict[str, bool]:
        """Validate that all HMM files exist"""
        validation = {}
        for isotype in self._supported_isotypes:
            hmm_file = os.path.join(self.hmm_dir, f"{isotype}.hmm")
            validation[isotype] = os.path.exists(hmm_file)
        return validation

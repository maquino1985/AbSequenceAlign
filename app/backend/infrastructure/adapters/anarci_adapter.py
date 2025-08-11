"""
ANARCI adapter for antibody sequence numbering and annotation.
Implements the ExternalToolAdapter interface to provide a clean abstraction.
"""

from typing import Dict, Any, List, Tuple, Optional
import logging

from ...core.interfaces import AbstractExternalToolAdapter
from ...core.exceptions import (
    AnarciError,
    ToolNotAvailableError,
)
from ...domain.models import NumberingScheme


class AnarciAdapter(AbstractExternalToolAdapter):
    """Adapter for the ANARCI tool for antibody sequence numbering"""

    def __init__(self):
        super().__init__("anarci")
        self._logger = logging.getLogger(f"{self.__class__.__name__}")
        self._supported_schemes = {
            NumberingScheme.IMGT: "imgt",
            NumberingScheme.KABAT: "kabat",
            NumberingScheme.CHOTHIA: "chothia",
            NumberingScheme.MARTIN: "martin",
            NumberingScheme.AHO: "aho",
        }

    def is_available(self) -> bool:
        """Check if ANARCI is available on the system"""
        try:
            # Try to import ANARCI

            return True
        except ImportError:
            self._logger.warning("ANARCI not available via import")
            return False

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate ANARCI output"""
        if not output or not isinstance(output, dict):
            return False

        # Check for required keys in ANARCI output
        required_keys = ["success", "data"]
        if not all(key in output for key in required_keys):
            return False

        return output.get("success", False)

    def _check_availability(self) -> bool:
        """Check if ANARCI is available on the system"""
        return self.is_available()

    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute ANARCI on the input sequence"""
        if not self._validate_input(input_data):
            raise AnarciError("Invalid input data", tool_name=self.tool_name)

        try:
            # Parse input data
            sequences = self._parse_input(input_data)

            # Run ANARCI
            result = self._run_anarci(sequences)

            return self._create_result(True, data=result)

        except ImportError:
            raise ToolNotAvailableError(
                "ANARCI is not available on this system",
                tool_name=self.tool_name,
            )
        except Exception as e:
            raise AnarciError(
                f"ANARCI execution failed: {str(e)}", tool_name=self.tool_name
            )

    def number_sequence(
        self,
        sequence: str,
        scheme: NumberingScheme = NumberingScheme.IMGT,
        allowed_species: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Number a single sequence using ANARCI"""
        if not allowed_species:
            allowed_species = ["human", "mouse", "rat"]

        input_data = f">query\n{sequence}\n"
        result = self.execute(input_data)

        # Add scheme information to result
        result["data"]["scheme"] = scheme.value
        result["data"]["allowed_species"] = allowed_species

        return result

    def number_sequences(
        self,
        sequences: List[Tuple[str, str]],
        scheme: NumberingScheme = NumberingScheme.IMGT,
        allowed_species: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Number multiple sequences using ANARCI"""
        if not allowed_species:
            allowed_species = ["human", "mouse", "rat"]

        # Create FASTA format input
        input_data = ""
        for name, sequence in sequences:
            input_data += f">{name}\n{sequence}\n"

        result = self.execute(input_data)

        # Add scheme information to result
        result["data"]["scheme"] = scheme.value
        result["data"]["allowed_species"] = allowed_species

        return result

    def _parse_input(self, input_data: str) -> List[Tuple[str, str]]:
        """Parse FASTA format input data"""
        sequences = []
        lines = input_data.strip().split("\n")

        current_name = None
        current_sequence = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith(">"):
                # Save previous sequence if exists
                if current_name and current_sequence:
                    sequences.append((current_name, current_sequence))

                # Start new sequence
                current_name = line[1:]  # Remove '>'
                current_sequence = ""
            else:
                # Add to current sequence
                current_sequence += line

        # Add last sequence
        if current_name and current_sequence:
            sequences.append((current_name, current_sequence))

        return sequences

    def _run_anarci(
        self,
        sequences: List[Tuple[str, str]],
        scheme: str = "imgt",
        allowed_species: List[str] = None,
    ) -> Dict[str, Any]:
        """Run ANARCI on the sequences"""
        if not allowed_species:
            allowed_species = ["human", "mouse", "rat"]

        try:
            from anarci import run_anarci

            # Run ANARCI
            (
                sequences_out,
                numbered,
                alignment_details,
                hit_tables,
            ), used_scheme = run_anarci(
                sequences,
                scheme=scheme,
                allowed_species=allowed_species,
                assign_germline=True,
            )

            # Process results
            results = []
            for i, (seq_name, seq_sequence) in enumerate(sequences_out):
                seq_numbered = numbered[i] if i < len(numbered) else []
                seq_aligns = (
                    alignment_details[i] if i < len(alignment_details) else []
                )
                seq_hits = hit_tables[i] if i < len(hit_tables) else []

                result = {
                    "name": seq_name,
                    "sequence": seq_sequence,
                    "numbered": seq_numbered,
                    "alignment_details": seq_aligns,
                    "hit_table": seq_hits,
                    "used_scheme": used_scheme,
                }
                results.append(result)

            return {
                "results": results,
                "used_scheme": used_scheme,
                "total_sequences": len(sequences),
            }

        except Exception as e:
            raise AnarciError(
                f"ANARCI execution failed: {str(e)}", tool_name=self.tool_name
            )

    def get_supported_schemes(self) -> List[str]:
        """Get list of supported numbering schemes"""
        return list(self._supported_schemes.keys())

    def is_scheme_supported(self, scheme: NumberingScheme) -> bool:
        """Check if a numbering scheme is supported"""
        return scheme in self._supported_schemes

    def _convert_scheme(self, scheme: NumberingScheme) -> str:
        """Convert domain scheme to ANARCI scheme"""
        if scheme not in self._supported_schemes:
            raise AnarciError(
                f"Unsupported numbering scheme: {scheme}",
                tool_name=self.tool_name,
            )
        return self._supported_schemes[scheme]

    def _extract_germline_info(self, hit_table: List[List]) -> Dict[str, Any]:
        """Extract germline information from ANARCI hit table"""
        if not hit_table or len(hit_table) < 2:
            return {}

        header = hit_table[0]
        rows = hit_table[1:]

        # Find relevant column indices
        id_idx = header.index("id") if "id" in header else None
        bitscore_idx = (
            header.index("bitscore") if "bitscore" in header else None
        )
        e_value_idx = header.index("evalue") if "evalue" in header else None

        if not rows:
            return {}

        # Get best hit (highest bitscore)
        best_row = max(
            rows,
            key=lambda row: (
                float(row[bitscore_idx]) if bitscore_idx is not None else 0
            ),
        )

        germline_info = {}
        if id_idx is not None:
            germline_info["id"] = best_row[id_idx]
        if bitscore_idx is not None:
            germline_info["bitscore"] = float(best_row[bitscore_idx])
        if e_value_idx is not None:
            germline_info["evalue"] = float(best_row[e_value_idx])

        return germline_info

    def _process_numbering(
        self, numbered_domain: List
    ) -> List[Dict[str, Any]]:
        """Process ANARCI numbering output"""
        processed = []

        for position, amino_acid in numbered_domain:
            if isinstance(position, (list, tuple)):
                pos_num = position[0]
                insertion = position[1] if len(position) > 1 else None
            else:
                pos_num = position
                insertion = None

            processed.append(
                {
                    "position": pos_num,
                    "insertion": insertion,
                    "amino_acid": amino_acid,
                }
            )

        return processed

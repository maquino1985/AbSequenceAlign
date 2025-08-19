"""
IgBLAST service for antibody and TCR sequence analysis.
Provides high-level interface for immunoglobulin-specific BLAST operations.
"""

import logging
from typing import Dict, Any, List, Optional

from backend.infrastructure.adapters.igblast_adapter_v3 import IgBlastAdapterV3


class IgBlastService:
    """Service for coordinating IgBLAST antibody sequence analysis"""

    def __init__(self, igblast_adapter=None):
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

        # Initialize adapter with dependency injection for testing
        if igblast_adapter is None:
            try:
                self.igblast_adapter = IgBlastAdapterV3()
            except Exception as e:
                self._logger.warning(
                    f"Could not initialize IgBlastAdapterV3: {e}"
                )
                self.igblast_adapter = None
        else:
            self.igblast_adapter = igblast_adapter

    def analyze_antibody_sequence(
        self,
        query_sequence: str,
        organism: str = "human",
        blast_type: str = "igblastn",
        evalue: float = 1e-10,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Analyze antibody sequence using IgBLAST.

        Args:
            query_sequence: The query sequence to analyze
            organism: Target organism (human, mouse, rat, etc.)
            blast_type: Type of IgBLAST search (igblastn, igblastp)
            evalue: E-value threshold
            **kwargs: Additional IgBLAST parameters

        Returns:
            Dictionary containing analysis results
        """
        self._logger.info(
            f"Analyzing antibody sequence for organism: {organism}"
        )

        # Validate sequence
        if not self.validate_antibody_sequence(
            query_sequence, self._get_sequence_type(blast_type)
        ):
            raise ValueError("Invalid antibody sequence provided")

        # Execute IgBLAST analysis
        if self.igblast_adapter is None:
            raise ValueError(
                "IgBLAST adapter is not available. Please check if IgBLAST is properly installed."
            )

        # Get database paths for the organism
        databases = self.igblast_adapter.get_available_databases()
        if organism not in databases:
            raise ValueError(
                f"Organism '{organism}' not supported. Available organisms: {list(databases.keys())}"
            )

        organism_dbs = databases[organism]

        # Execute with appropriate databases
        if blast_type == "igblastp":
            # For protein IgBLAST, only use V database
            results = self.igblast_adapter.execute(
                query_sequence=query_sequence,
                v_db=organism_dbs["V"]["path"],
                blast_type=blast_type,
                **kwargs,
            )
        else:
            # For nucleotide IgBLAST, use V, D, J databases
            results = self.igblast_adapter.execute(
                query_sequence=query_sequence,
                v_db=organism_dbs["V"]["path"],
                d_db=organism_dbs["D"]["path"],
                j_db=organism_dbs["J"]["path"],
                blast_type=blast_type,
                **kwargs,
            )

        return results

    def get_supported_organisms(self) -> List[str]:
        """
        Get list of supported organisms for IgBLAST analysis.

        Returns:
            List of supported organism names
        """
        if self.igblast_adapter is None:
            self._logger.warning(
                "IgBLAST adapter is not available, returning default organisms"
            )
            return ["human", "mouse"]  # Default fallback organisms

        try:
            databases = self.igblast_adapter.get_available_databases()
            return list(databases.keys())
        except Exception as e:
            self._logger.error(f"Failed to get supported organisms: {e}")
            return ["human", "mouse"]  # Fallback organisms

    def validate_antibody_sequence(
        self, sequence: str, sequence_type: str
    ) -> bool:
        """
        Validate an antibody sequence.

        Args:
            sequence: The sequence to validate
            sequence_type: Type of sequence ('protein' or 'nucleotide')

        Returns:
            True if sequence is valid, False otherwise
        """
        try:
            # Clean and normalize the sequence (case insensitive)
            # Remove newlines, spaces, tabs, and other whitespace
            sequence_clean = "".join(sequence.split()).upper()

            # Check for empty sequence
            if not sequence_clean:
                return False

            if sequence_type == "protein":
                valid_chars = set("ACDEFGHIKLMNPQRSTVWY")
            else:  # nucleotide
                # Support both DNA (ATGC) and RNA (ATGCU) nucleotides
                valid_chars = set("ATGCUN")  # N for ambiguous nucleotides

            invalid_chars = set(sequence_clean) - valid_chars

            return len(invalid_chars) == 0

        except Exception:
            return False

    def extract_cdr3(
        self, results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract CDR3 information from IgBLAST results.

        Args:
            results: IgBLAST analysis results

        Returns:
            CDR3 information dictionary or None if not found
        """
        if not results or "hits" not in results or not results["hits"]:
            return None

        best_hit = results["hits"][0]

        cdr3_info = {
            "sequence": best_hit.get("cdr3_sequence"),
            "start": best_hit.get("cdr3_start"),
            "end": best_hit.get("cdr3_end"),
        }

        # Return None if no CDR3 information
        if not any(cdr3_info.values()):
            return None

        return cdr3_info

    def get_gene_assignments(
        self, results: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """
        Extract gene assignments from IgBLAST results.

        Args:
            results: IgBLAST analysis results

        Returns:
            Gene assignments dictionary or None if not found
        """
        if not results or "hits" not in results or not results["hits"]:
            return None

        best_hit = results["hits"][0]

        gene_assignments = {
            "v_gene": best_hit.get("v_gene"),
            "d_gene": best_hit.get("d_gene"),
            "j_gene": best_hit.get("j_gene"),
            "c_gene": best_hit.get("c_gene"),
        }

        # Return None if no gene assignments
        if not any(gene_assignments.values()):
            return None

        return gene_assignments

    def get_antibody_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of antibody analysis results.

        Args:
            results: IgBLAST analysis results

        Returns:
            Summary dictionary
        """
        summary = {
            "total_hits": results.get("total_hits", 0),
            "best_identity": 0.0,
            "gene_assignments": None,
            "cdr3_info": None,
        }

        if results.get("hits"):
            best_hit = results["hits"][0]
            summary["best_identity"] = best_hit.get("identity", 0.0)
            summary["gene_assignments"] = self.get_gene_assignments(results)
            summary["cdr3_info"] = self.extract_cdr3(results)

        return summary

    def _get_sequence_type(self, blast_type: str) -> str:
        """Get sequence type from IgBLAST type."""
        return "protein" if blast_type == "igblastp" else "nucleotide"

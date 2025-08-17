"""
BLAST service for coordinating sequence similarity searches.
Provides high-level interface for BLAST and IgBLAST operations.
"""

from typing import Dict, Any, List, Optional
import logging
import tempfile
import os

from backend.infrastructure.adapters import BlastAdapter, IgBlastAdapter
from backend.infrastructure.repositories.blast_repository import (
    BlastRepository,
)


class BlastService:
    """Service for coordinating BLAST sequence similarity searches"""

    def __init__(
        self, blast_adapter=None, igblast_adapter=None, job_repository=None
    ):
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

        # Initialize adapters with dependency injection for testing
        if blast_adapter is None:
            try:
                self.blast_adapter = BlastAdapter()
            except Exception as e:
                self._logger.warning(f"Could not initialize BlastAdapter: {e}")
                self.blast_adapter = None
        else:
            self.blast_adapter = blast_adapter

        if igblast_adapter is None:
            try:
                self.igblast_adapter = IgBlastAdapter()
            except Exception as e:
                self._logger.warning(
                    f"Could not initialize IgBlastAdapter: {e}"
                )
                self.igblast_adapter = None
        else:
            self.igblast_adapter = igblast_adapter

        self.job_repository = job_repository or BlastRepository()

    def search_public_databases(
        self,
        query_sequence: str,
        databases: List[str],
        blast_type: str = "blastp",
        evalue: float = 1e-10,
        max_target_seqs: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Search sequences against public databases.

        Args:
            query_sequence: The query sequence to search
            databases: List of database names to search against
            blast_type: Type of BLAST search (blastp, blastn, etc.)
            evalue: E-value threshold
            max_target_seqs: Maximum number of target sequences to return
            **kwargs: Additional BLAST parameters

        Returns:
            Dictionary containing search results
        """
        self._logger.info(f"Searching against public databases: {databases}")

        # Validate sequence
        if not self.validate_sequence(
            query_sequence, self._get_sequence_type(blast_type)
        ):
            raise ValueError("Invalid sequence provided")

        # Execute BLAST search
        results = self.blast_adapter.execute(
            query_sequence=query_sequence,
            database=",".join(databases),
            blast_type=blast_type,
            evalue=evalue,
            max_target_seqs=max_target_seqs,
            **kwargs,
        )

        return results

    def search_internal_database(
        self,
        query_sequence: str,
        blast_type: str = "blastp",
        evalue: float = 1e-10,
        max_target_seqs: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Search sequences against internal database.

        Args:
            query_sequence: The query sequence to search
            blast_type: Type of BLAST search
            evalue: E-value threshold
            max_target_seqs: Maximum number of target sequences to return
            **kwargs: Additional BLAST parameters

        Returns:
            Dictionary containing search results
        """
        self._logger.info("Searching against internal database")

        # Validate sequence
        if not self.validate_sequence(
            query_sequence, self._get_sequence_type(blast_type)
        ):
            raise ValueError("Invalid sequence provided")

        # Get internal database path
        internal_db = self._get_internal_database_path(blast_type)

        # Execute BLAST search
        results = self.blast_adapter.execute(
            query_sequence=query_sequence,
            database=internal_db,
            blast_type=blast_type,
            evalue=evalue,
            max_target_seqs=max_target_seqs,
            **kwargs,
        )

        return results

    def create_custom_database(
        self,
        sequences: List[Dict[str, str]],
        database_name: str,
        database_type: str = "protein",
    ) -> Dict[str, Any]:
        """
        Create a custom BLAST database from provided sequences.

        Args:
            sequences: List of sequence dictionaries with 'name' and 'sequence' keys
            database_name: Name for the custom database
            database_type: Type of database ('protein' or 'nucleotide')

        Returns:
            Dictionary containing database creation results
        """
        self._logger.info(f"Creating custom database: {database_name}")

        # Create temporary FASTA file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as f:
            for seq_data in sequences:
                f.write(f">{seq_data['name']}\n{seq_data['sequence']}\n")
            temp_fasta = f.name

        try:
            # Create BLAST database
            self.blast_adapter._create_blast_database(
                temp_fasta, database_name
            )

            return {
                "database_name": database_name,
                "database_type": database_type,
                "sequences_count": len(sequences),
                "status": "created",
            }

        finally:
            # Cleanup temporary file
            os.unlink(temp_fasta)

    def get_available_databases(self) -> Dict[str, Any]:
        """
        Get list of available databases.

        Returns:
            Dictionary containing available databases by category
        """
        return {
            "public": {
                "nr": "NCBI non-redundant protein database",
                "pdb": "Protein Data Bank",
                "swissprot": "Swiss-Prot protein database",
                "refseq_protein": "RefSeq protein database",
            },
            "custom": self._get_custom_databases(),
            "internal": self._get_internal_databases(),
        }

    def validate_sequence(self, sequence: str, sequence_type: str) -> bool:
        """
        Validate a sequence.

        Args:
            sequence: The sequence to validate
            sequence_type: Type of sequence ('protein' or 'nucleotide')

        Returns:
            True if sequence is valid, False otherwise
        """
        try:
            if sequence_type == "protein":
                valid_chars = set("ACDEFGHIKLMNPQRSTVWY")
            else:  # nucleotide
                valid_chars = set("ATGCU")

            sequence_upper = sequence.upper().strip()
            invalid_chars = set(sequence_upper) - valid_chars

            return len(invalid_chars) == 0

        except Exception:
            return False

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a BLAST job.

        Args:
            job_id: The job ID to check

        Returns:
            Job status dictionary or None if not found
        """
        return self.job_repository.get_job(job_id)

    def _get_sequence_type(self, blast_type: str) -> str:
        """Get sequence type from BLAST type."""
        protein_types = ["blastp", "blastx", "tblastn"]
        return "protein" if blast_type in protein_types else "nucleotide"

    def _get_internal_database_path(self, blast_type: str) -> str:
        """Get internal database path for BLAST type."""
        # This would be implemented based on your database structure
        base_path = "/data/blast_databases"
        if blast_type in ["blastp", "blastx", "tblastn"]:
            return f"{base_path}/internal_protein"
        else:
            return f"{base_path}/internal_nucleotide"

    def _get_custom_databases(self) -> Dict[str, str]:
        """Get list of custom databases."""
        # This would be implemented to read from a configuration or database
        return {}

    def _get_internal_databases(self) -> Dict[str, str]:
        """Get list of internal databases."""
        # This would be implemented to read from a configuration or database
        return {
            "internal_protein": "Internal protein sequences",
            "internal_nucleotide": "Internal nucleotide sequences",
        }

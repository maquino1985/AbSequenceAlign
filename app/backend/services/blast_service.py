"""
BLAST service for coordinating sequence similarity searches.
Provides high-level interface for BLAST and IgBLAST operations.
"""

from typing import Dict, Any, List, Optional
import logging
import tempfile
import os

from backend.infrastructure.adapters import BlastAdapter
from backend.infrastructure.adapters.igblast_adapter_v3 import IgBlastAdapterV3
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
                # Try to initialize Docker client for BLAST
                docker_client = None
                try:
                    import docker

                    docker_client = docker.from_env()
                except ImportError:
                    self._logger.warning("Docker Python package not available")
                except Exception as e:
                    self._logger.warning(
                        f"Could not initialize Docker client: {e}"
                    )

                self.blast_adapter = BlastAdapter(docker_client=docker_client)
            except Exception as e:
                self._logger.warning(f"Could not initialize BlastAdapter: {e}")
                self.blast_adapter = None
        else:
            self.blast_adapter = blast_adapter

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
            "public": self._get_public_databases(),
            "custom": self._get_custom_databases(),
            "internal": self._get_internal_databases(),
        }

    def _get_public_databases(self) -> Dict[str, str]:
        """
        Dynamically discover available public databases from the BLAST database directory.

        Returns:
            Dictionary mapping database names to descriptions
        """
        from backend.config import BLAST_DB_DIR

        databases = {}

        if not BLAST_DB_DIR.exists():
            self._logger.warning(
                f"BLAST database directory does not exist: {BLAST_DB_DIR}"
            )
            return databases

        # Look for protein databases (.phr, .pin, .psq files)
        # Scan both root directory and subdirectories for .phr files
        for file_path in BLAST_DB_DIR.rglob("*.phr"):
            db_name = file_path.stem  # Remove .phr extension

            # Check if corresponding .pin and .psq files exist
            pin_file = file_path.with_suffix(".pin")
            psq_file = file_path.with_suffix(".psq")

            if pin_file.exists() and psq_file.exists():
                # Map common database names to descriptions
                descriptions = {
                    "swissprot": "Swiss-Prot protein database",
                    "pdbaa": "Protein Data Bank",
                    "nr": "NCBI non-redundant protein database",
                    "refseq_protein": "RefSeq protein database",
                }

                description = descriptions.get(
                    db_name, f"{db_name} protein database"
                )
                databases[db_name] = description

        # Look for nucleotide databases (.nhr, .nin, .nsq files)
        # First, collect all database base names (without .00, .01 suffixes)
        nucleotide_dbs = {}

        # Scan both root directory and subdirectories for .nhr files
        for file_path in BLAST_DB_DIR.rglob("*.nhr"):
            db_name = file_path.stem  # Remove .nhr extension

            # Skip IgBLAST-specific databases
            if any(
                skip_pattern in db_name.lower()
                for skip_pattern in [
                    "ncbi_human_c_genes",
                    "ncbi_mouse_c_genes",
                    "mouse_c_genes",
                    "human_c_genes",
                    "airr_c_",
                    "gl_",
                    "_gl_",
                ]
            ):
                continue

            # Check if corresponding .nin and .nsq files exist
            nin_file = file_path.with_suffix(".nin")
            nsq_file = file_path.with_suffix(".nsq")

            if nin_file.exists() and nsq_file.exists():
                # Handle split databases (e.g., GCF_000001405.39_top_level.00, GCF_000001405.39_top_level.01)
                if db_name.endswith(".00"):
                    base_name = db_name[:-3]  # Remove .00
                    # Check if .01 version exists
                    db_01_name = base_name + ".01"
                    db_01_nhr = file_path.parent / f"{db_01_name}.nhr"
                    db_01_nin = file_path.parent / f"{db_01_name}.nin"
                    db_01_nsq = file_path.parent / f"{db_01_name}.nsq"

                    if (
                        db_01_nhr.exists()
                        and db_01_nin.exists()
                        and db_01_nsq.exists()
                    ):
                        # This is a split database, use the base name
                        nucleotide_dbs[base_name] = file_path
                    else:
                        # Only .00 exists, use the full name
                        nucleotide_dbs[db_name] = file_path
                elif db_name.endswith(".01"):
                    # Skip .01 files as they'll be handled with .00
                    continue
                else:
                    # Regular database name
                    nucleotide_dbs[db_name] = file_path

        # Now create descriptions for the nucleotide databases
        for db_name, file_path in nucleotide_dbs.items():
            # Map common database names to human-readable descriptions
            descriptions = {
                "nt": "NCBI non-redundant nucleotide database",
                "refseq_nucleotide": "RefSeq nucleotide database",
                "16S_ribosomal_RNA": "16S ribosomal RNA database",
                "refseq_select_rna": "RefSeq Select RNA database",
                "GCF_000001405.39_top_level": "Human genome (GRCh38.p13)",
                "GCF_000001635.27_top_level": "Mouse genome (GRCm39)",
                "euk_cdna": "Human+Mouse+Rabbit+Cyno cDNA database",
            }

            description = descriptions.get(
                db_name, f"{db_name} nucleotide database"
            )
            databases[db_name] = description

        self._logger.info(
            f"Found {len(databases)} available databases: {list(databases.keys())}"
        )
        return databases

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
        # For now, return empty since we don't have functional internal databases
        # This should be implemented to read from a configuration or database
        return {}

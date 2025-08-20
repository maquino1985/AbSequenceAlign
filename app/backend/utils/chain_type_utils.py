"""
Chain Type Utilities for IgBLAST Adapters

This module provides centralized utilities for extracting chain type information
from gene names, ensuring consistency across all adapter implementations.
"""


class ChainTypeUtils:
    """Utility class for chain type extraction and related operations."""

    @staticmethod
    def extract_chain_type(gene_name: str) -> str:
        """
        Extract chain type from gene name.

        Args:
            gene_name: The gene name (e.g., "IGHV1-2*01", "IGKV1-2*01")

        Returns:
            The chain type as a locus name ("IGH", "IGK", "IGL", "TCR", "unknown")
        """
        if not gene_name:
            return "unknown"

        if gene_name.startswith("IGH"):
            return "IGH"
        if gene_name.startswith("IGK"):
            return "IGK"
        if gene_name.startswith("IGL"):
            return "IGL"
        if gene_name.startswith(("TRA", "TRB", "TRG", "TRD")):
            return "TCR"

        return "unknown"

    @staticmethod
    def is_heavy_chain(gene_name: str) -> bool:
        """
        Check if a gene name represents a heavy chain.

        Args:
            gene_name: The gene name to check

        Returns:
            True if the gene represents a heavy chain (IGH), False otherwise
        """
        return ChainTypeUtils.extract_chain_type(gene_name) == "IGH"

    @staticmethod
    def is_light_chain(gene_name: str) -> bool:
        """
        Check if a gene name represents a light chain.

        Args:
            gene_name: The gene name to check

        Returns:
            True if the gene represents a light chain (IGK or IGL), False otherwise
        """
        chain_type = ChainTypeUtils.extract_chain_type(gene_name)
        return chain_type in ["IGK", "IGL"]

    @staticmethod
    def is_tcr_chain(gene_name: str) -> bool:
        """
        Check if a gene name represents a TCR chain.

        Args:
            gene_name: The gene name to check

        Returns:
            True if the gene represents a TCR chain, False otherwise
        """
        return ChainTypeUtils.extract_chain_type(gene_name) == "TCR"

"""
Base parser for IgBLAST output parsers.

Provides shared utilities (e.g., IMGT subject URL generation, chain type extraction)
and defines the abstract parse() interface for concrete parsers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseIgBlastParser(ABC):
    """Abstract base class for IgBLAST parsers."""

    def __init__(self) -> None:
        # Optional organism hint used for subject URL species selection
        # Expected values: "human", "mouse", "rat", "rabbit", "rhesus"
        self.organism: str | None = None

    @abstractmethod
    def parse(self, output: str, blast_type: str) -> Dict[str, Any]:
        """Parse IgBLAST output and return a normalized result dictionary."""
        ...

    def _get_subject_url(self, gene_name: str) -> str:
        """Generate IMGT URL for gene name.

        Returns empty string when the gene_name is empty or not recognized.
        """
        if not gene_name:
            return ""

        # Extract the gene without allele information for URL locus
        base_gene = gene_name.split("*")[0]

        # Choose species from organism hint; default to human if unknown
        organism = (self.organism or "human").lower()
        species_by_organism = {
            "human": "Homo+sapiens",
            "mouse": "Mus+musculus",
            "rat": "Rattus+norvegicus",
            "rabbit": "Oryctolagus+cuniculus",
            "rhesus": "Macaca+mulatta",
        }
        species = species_by_organism.get(organism, "Homo+sapiens")

        # Determine group for IMGT
        if base_gene.startswith("IG"):  # IGH/IGK/IGL
            group = base_gene[:3]
        elif base_gene.startswith("TR"):  # TCR genes
            # Many IMGT pages use group=TCR; keep that as a conservative default
            group = "TCR"
        else:
            return ""

        return (
            "https://www.imgt.org/IMGTrepertoire/index.php?section=LocusGenes"
            f"&repertoire=genetable&species={species}&group={group}&locus={base_gene}"
        )

    def _extract_chain_type(self, gene_name: str) -> str:
        """Infer chain type from a gene name (best-effort)."""
        if not gene_name:
            return "unknown"
        if gene_name.startswith("IGH"):
            return "heavy"
        if gene_name.startswith(("IGK", "IGL")):
            return "light"
        if gene_name.startswith(("TRA", "TRB", "TRG", "TRD")):
            return "tcr"
        return "unknown"

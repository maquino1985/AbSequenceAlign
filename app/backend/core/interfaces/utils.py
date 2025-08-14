"""
Utility interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class RegionExtractionInterface(ABC):
    """Interface for region extraction utilities"""

    @abstractmethod
    def extract_regions(self, sequence: str, numbering_scheme: str = "imgt") -> Dict[str, Any]:
        """Extract regions from a sequence"""
        pass

    @abstractmethod
    def extract_cdr_regions(self, sequence: str, numbering_scheme: str = "imgt") -> List[Dict[str, Any]]:
        """Extract CDR regions from a sequence"""
        pass

    @abstractmethod
    def extract_fr_regions(self, sequence: str, numbering_scheme: str = "imgt") -> List[Dict[str, Any]]:
        """Extract framework regions from a sequence"""
        pass


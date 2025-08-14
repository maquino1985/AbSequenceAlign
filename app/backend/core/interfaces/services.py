"""
Service interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AnnotationService(ABC):
    """Interface for annotation services"""

    @abstractmethod
    def annotate_sequence(self, sequence: str, numbering_scheme: str = "imgt") -> Dict[str, Any]:
        """Annotate a single sequence"""
        pass

    @abstractmethod
    def annotate_sequences(self, sequences: List[str], numbering_scheme: str = "imgt") -> List[Dict[str, Any]]:
        """Annotate multiple sequences"""
        pass


class BiologicService(ABC):
    """Interface for biologic services"""

    @abstractmethod
    def create_biologic(self, biologic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a biologic entity"""
        pass

    @abstractmethod
    def get_biologic(self, biologic_id: str) -> Optional[Dict[str, Any]]:
        """Get a biologic entity by ID"""
        pass

    @abstractmethod
    def update_biologic(self, biologic_id: str, biologic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a biologic entity"""
        pass

    @abstractmethod
    def delete_biologic(self, biologic_id: str) -> bool:
        """Delete a biologic entity"""
        pass

    @abstractmethod
    def list_biologics(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List biologic entities"""
        pass


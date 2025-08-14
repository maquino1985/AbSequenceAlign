"""
Processor interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class Processor(ABC):
    """Simple processor interface - just process data and return result"""

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process the input data and return the result"""
        pass


class SequenceProcessor(ABC):
    """Simple interface for processing sequences"""
    
    @abstractmethod
    def process(self, sequences: Dict[str, str]) -> Any:
        """Process sequences and return result"""
        pass


class AnnotationProcessor(ABC):
    """Simple interface for annotation processing"""
    
    @abstractmethod
    def process(self, sequences: Dict[str, str], numbering_scheme: str = "imgt") -> Any:
        """Process sequences for annotation and return result"""
        pass


class BiologicProcessor(ABC):
    """Interface for biologic processing"""
    
    @abstractmethod
    def process_biologic(self, biologic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process biologic data"""
        pass

    @abstractmethod
    def validate_biologic(self, biologic_data: Dict[str, Any]) -> bool:
        """Validate biologic data"""
        pass

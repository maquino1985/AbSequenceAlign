"""
Adapter interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging


class AbstractExternalToolAdapter(ABC):
    """Abstract base class for external tool adapters"""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the external tool is available"""
        pass

    @abstractmethod
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute the external tool with input data"""
        pass

    @abstractmethod
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the tool output"""
        pass

    def _validate_input(self, input_data: str) -> bool:
        """Validate input data"""
        return input_data is not None and len(input_data.strip()) > 0

    def _create_result(
        self, success: bool, data: Any = None, error: str = None
    ) -> Dict[str, Any]:
        """Create a standardized result dictionary"""
        return {
            "success": success,
            "data": data,
            "error": error,
            "tool_name": self.tool_name,
        }


class ExternalToolAdapter(AbstractExternalToolAdapter):
    """Interface for external tool adapters"""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the external tool is available"""
        pass

    @abstractmethod
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute the external tool with input data"""
        pass

    @abstractmethod
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the tool output"""
        pass


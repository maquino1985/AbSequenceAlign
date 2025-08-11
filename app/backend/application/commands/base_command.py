"""
Base command class for all annotation and alignment commands.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CommandResult:
    """Result of command execution"""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseCommand(ABC):
    """Base class for all commands"""

    def __init__(self, request_data: Dict[str, Any]):
        """
        Initialize command with request data.

        Args:
            request_data: The request data to process
        """
        self.request_data = request_data
        self.execution_start: Optional[datetime] = None
        self.execution_end: Optional[datetime] = None

    @abstractmethod
    def validate(self) -> bool:
        """Validate the command data"""
        pass

    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command"""
        pass

    def get_execution_time(self) -> Optional[float]:
        """Get command execution time in seconds"""
        if self.execution_start and self.execution_end:
            return (self.execution_end - self.execution_start).total_seconds()
        return None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(data={self.request_data})"

    def __repr__(self) -> str:
        return self.__str__()

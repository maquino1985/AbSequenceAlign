"""
Base handler class for all command handlers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..commands.base_command import BaseCommand, CommandResult


class BaseHandler(ABC):
    """Base class for all command handlers"""

    def __init__(self):
        """Initialize the handler"""
        pass

    @abstractmethod
    async def handle(self, command: BaseCommand) -> Dict[str, Any]:
        """
        Handle a command and return the result.

        Args:
            command: The command to handle

        Returns:
            Dictionary containing the result data
        """
        pass

    def _create_error_response(self, error: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {"success": False, "error": error, "data": None}

    def _create_success_response(self, data: Any) -> Dict[str, Any]:
        """Create a standardized success response"""
        return {"success": True, "error": None, "data": data}

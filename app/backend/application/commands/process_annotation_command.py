"""
Command for processing complete annotation workflow.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .base_command import BaseCommand, CommandResult
from backend.logger import logger


class ProcessAnnotationCommand(BaseCommand):
    """Command for processing a complete annotation workflow"""

    def __init__(self, request_data: Dict[str, Any]):
        super().__init__(request_data)
        self.sequences: Dict[str, Any] = {}
        self.numbering_scheme: str = "IMGT"
        self.persist_to_database: bool = False
        self.organism: Optional[str] = None

    def validate(self) -> bool:
        """Validate the annotation workflow request data"""
        try:
            # Extract and validate sequences data
            if "sequences" not in self.request_data:
                logger.error("Missing sequences data in request")
                return False

            sequences_data = self.request_data["sequences"]
            if not isinstance(sequences_data, dict) or not sequences_data:
                logger.error("Sequences data must be a non-empty dictionary")
                return False

            # Extract numbering scheme if provided
            if "numbering_scheme" in self.request_data:
                scheme = self.request_data["numbering_scheme"]
                valid_schemes = ["imgt", "kabat", "chothia", "martin", "aho", "cgg"]
                if scheme.lower() not in valid_schemes:
                    logger.error(f"Invalid numbering scheme: {scheme}")
                    return False
                self.numbering_scheme = scheme.lower()

            # Extract persistence flag if provided
            if "persist_to_database" in self.request_data:
                self.persist_to_database = bool(
                    self.request_data["persist_to_database"]
                )

            # Extract organism if provided
            if "organism" in self.request_data:
                self.organism = self.request_data["organism"]

            # Basic validation passed
            return True

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def execute(self) -> CommandResult:
        """Execute the annotation workflow command"""
        self.execution_start = datetime.now()

        try:
            # Validate the command
            if not self.validate():
                return CommandResult(
                    success=False,
                    error="Invalid annotation workflow request data",
                )

            # Extract sequences data
            self.sequences = self.request_data["sequences"]

            # Command is ready for execution
            self.execution_end = datetime.now()

            return CommandResult(
                success=True,
                data={
                    "sequences": self.sequences,
                    "numbering_scheme": self.numbering_scheme,
                    "persist_to_database": self.persist_to_database,
                    "organism": self.organism,
                },
                execution_time=self.get_execution_time(),
                metadata={
                    "command_type": "process_annotation",
                    "sequence_count": len(self.sequences),
                },
            )

        except Exception as e:
            self.execution_end = datetime.now()
            logger.error(f"Command execution error: {e}")
            return CommandResult(
                success=False,
                error=str(e),
                execution_time=self.get_execution_time(),
            )

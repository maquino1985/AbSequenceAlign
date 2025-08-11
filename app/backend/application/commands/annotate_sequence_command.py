"""
Command for annotating biologic sequences.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .base_command import BaseCommand, CommandResult
from backend.domain.entities import BiologicEntity
from backend.domain.models import NumberingScheme
from backend.logger import logger


class AnnotateSequenceCommand(BaseCommand):
    """Command for annotating a single biologic sequence"""

    def __init__(self, request_data: Dict[str, Any]):
        super().__init__(request_data)
        self.sequence: Optional[BiologicEntity] = None
        self.numbering_scheme: str = "IMGT"

    def validate(self) -> bool:
        """Validate the annotation request data"""
        try:
            # Extract and validate sequence data
            if "sequence" not in self.request_data:
                logger.error("Missing sequence data in request")
                return False

            # Extract numbering scheme if provided
            if "numbering_scheme" in self.request_data:
                scheme = self.request_data["numbering_scheme"]
                if scheme not in ["IMGT", "KABAT", "CHOTHIA"]:
                    logger.error(f"Invalid numbering scheme: {scheme}")
                    return False
                self.numbering_scheme = scheme

            # Basic validation passed
            return True

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def execute(self) -> CommandResult:
        """Execute the annotation command"""
        self.execution_start = datetime.now()

        try:
            # Validate the command
            if not self.validate():
                return CommandResult(
                    success=False, error="Invalid annotation request data"
                )

            # Extract sequence data
            sequence_data = self.request_data["sequence"]

            # Convert to domain entity (this would be done by a converter service)
            # For now, we'll assume it's already a BiologicEntity
            if isinstance(sequence_data, BiologicEntity):
                self.sequence = sequence_data
            else:
                # TODO: Use converter service to convert from dict to BiologicEntity
                logger.warning("Sequence data conversion not implemented")
                return CommandResult(
                    success=False,
                    error="Sequence data conversion not implemented",
                )

            # Command is ready for execution
            self.execution_end = datetime.now()

            return CommandResult(
                success=True,
                data={
                    "sequence": self.sequence,
                    "numbering_scheme": self.numbering_scheme,
                },
                execution_time=self.get_execution_time(),
                metadata={"command_type": "annotate_sequence"},
            )

        except Exception as e:
            self.execution_end = datetime.now()
            logger.error(f"Command execution error: {e}")
            return CommandResult(
                success=False,
                error=str(e),
                execution_time=self.get_execution_time(),
            )

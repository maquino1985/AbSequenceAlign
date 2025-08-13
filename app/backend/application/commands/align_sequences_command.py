"""
Command for aligning biologic sequences.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_command import BaseCommand, CommandResult
from backend.domain.entities import BiologicEntity
from backend.logger import logger


class AlignSequencesCommand(BaseCommand):
    """Command for aligning multiple biologic sequences"""

    def __init__(self, request_data: Dict[str, Any]):
        super().__init__(request_data)
        self.sequences: List[BiologicEntity] = []
        self.alignment_strategy: str = "multiple"
        self.region_type: Optional[str] = None

    def validate(self) -> bool:
        """Validate the alignment request data"""
        try:
            # Extract and validate sequences data
            if "sequences" not in self.request_data:
                logger.error("Missing sequences data in request")
                return False

            sequences_data = self.request_data["sequences"]
            if not isinstance(sequences_data, list) or len(sequences_data) < 2:
                logger.error("At least 2 sequences required for alignment")
                return False

            # Extract alignment strategy if provided
            if "strategy" in self.request_data:
                strategy = self.request_data["strategy"]
                if strategy not in ["pairwise", "multiple", "region_specific"]:
                    logger.error(f"Invalid alignment strategy: {strategy}")
                    return False
                self.alignment_strategy = strategy

            # Extract region type if provided
            if "region_type" in self.request_data:
                region_type = self.request_data["region_type"]
                if region_type not in ["CDR", "FR", "full"]:
                    logger.error(f"Invalid region type: {region_type}")
                    return False
                self.region_type = region_type

            # Basic validation passed
            return True

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def execute(self) -> CommandResult:
        """Execute the alignment command"""
        self.execution_start = datetime.now()

        try:
            # Validate the command
            if not self.validate():
                return CommandResult(
                    success=False, error="Invalid alignment request data"
                )

            # Extract sequences data
            sequences_data = self.request_data["sequences"]

            # Convert to domain entities (this would be done by a converter service)
            # For now, we'll assume they're already BiologicEntity objects
            for seq_data in sequences_data:
                if isinstance(seq_data, BiologicEntity):
                    self.sequences.append(seq_data)
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
                    "sequences": self.sequences,
                    "strategy": self.alignment_strategy,
                    "region_type": self.region_type,
                },
                execution_time=self.get_execution_time(),
                metadata={
                    "command_type": "align_sequences",
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

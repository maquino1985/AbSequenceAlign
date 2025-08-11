"""
Handler for complete annotation workflow commands.
"""

from typing import Dict, Any

from .base_handler import BaseHandler
from ..commands.base_command import BaseCommand
from ..services.annotation_service import AnnotationService
from ..services.validation_service import ValidationService
from ..services.response_service import ResponseService
from ..services.biologic_service import BiologicService
from backend.logger import logger


class WorkflowHandler(BaseHandler):
    """Handler for complete annotation workflow commands"""

    def __init__(
        self,
        annotation_service: AnnotationService,
        validation_service: ValidationService,
        response_service: ResponseService,
        biologic_service: BiologicService,
    ):
        """
        Initialize the workflow handler.

        Args:
            annotation_service: Service for sequence annotation
            validation_service: Service for data validation
            response_service: Service for response formatting
            biologic_service: Service for database operations
        """
        super().__init__()
        self.annotation_service = annotation_service
        self.validation_service = validation_service
        self.response_service = response_service
        self.biologic_service = biologic_service

    async def handle(self, command: BaseCommand) -> Dict[str, Any]:
        """
        Handle a workflow command.

        Args:
            command: The workflow command to handle

        Returns:
            Dictionary containing the workflow result
        """
        try:
            logger.info(f"Handling workflow command: {command}")

            # Execute the command to validate and prepare data
            command_result = command.execute()
            if not command_result.success:
                return self._create_error_response(command_result.error)

            # Extract data from command result
            sequences = command_result.data["sequences"]
            numbering_scheme = command_result.data["numbering_scheme"]
            persist_to_database = command_result.data["persist_to_database"]
            organism = command_result.data["organism"]

            # Process each sequence
            results = []
            for sequence_name, sequence_data in sequences.items():
                try:
                    # Create domain entity from sequence data
                    from backend.domain.entities import BiologicEntity, BiologicChain, BiologicSequence
                    from backend.domain.models import ChainType, BiologicType

                    # Convert sequence data to domain entities
                    chains = []
                    for chain_name, chain_sequence in sequence_data.items():
                        # Create sequence
                        biologic_sequence = BiologicSequence(
                            sequence_type="PROTEIN",
                            sequence_data=chain_sequence,
                            description=f"{chain_name} sequence for {sequence_name}",
                        )

                        # Determine chain type
                        chain_type = ChainType.HEAVY if "heavy" in chain_name.lower() else ChainType.LIGHT

                        # Create chain
                        biologic_chain = BiologicChain(
                            name=chain_name,
                            chain_type=chain_type,
                            sequences=[biologic_sequence],
                        )

                        chains.append(biologic_chain)

                    # Create domain entity
                    sequence = BiologicEntity(
                        name=sequence_name,
                        biologic_type=BiologicType.ANTIBODY,
                        description=f"Antibody sequence: {sequence_name}",
                        chains=chains,
                        metadata={},
                    )

                    # Perform annotation
                    annotation_result = (
                        self.annotation_service.annotate_sequence(
                            sequence, numbering_scheme
                        )
                    )

                    if annotation_result.success:
                        results.append(
                            {
                                "name": sequence_name,
                                "result": annotation_result.data,
                                "success": True,
                            }
                        )

                        # Persist to database if requested
                        if persist_to_database:
                            await self.biologic_service.process_and_persist_biologic_entity(
                                annotation_result.data, organism
                            )
                    else:
                        results.append(
                            {
                                "name": sequence_name,
                                "error": annotation_result.error,
                                "success": False,
                            }
                        )

                except Exception as e:
                    logger.error(
                        f"Error processing sequence {sequence_name}: {e}"
                    )
                    results.append(
                        {
                            "name": sequence_name,
                            "error": str(e),
                            "success": False,
                        }
                    )

            # Format the response
            formatted_response = (
                self.response_service.format_workflow_response(results)
            )

            return self._create_success_response(formatted_response)

        except Exception as e:
            logger.error(f"Error handling workflow command: {e}")
            return self._create_error_response(
                f"Workflow handler error: {str(e)}"
            )

"""
Handler for complete annotation workflow commands.
"""

from pprint import pprint
from typing import Dict, Any, List

from annotation.anarci_result_processor import (
    AnarciResultProcessor,
    AnarciResultObject,
)
from backend.domain.entities import (
    BiologicEntity,
    BiologicChain,
    BiologicSequence,
)
from backend.domain.models import BiologicType
from backend.domain.models import NumberingScheme
from backend.logger import logger
from domain import BiologicDomain, DomainType, BiologicFeature
from .base_handler import BaseHandler
from ..commands.base_command import BaseCommand
from ..services.annotation_service import AnnotationService
from ..services.biologic_service import BiologicService
from ..services.response_service import ResponseService
from ..services.validation_service import ValidationService


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
            numbering_scheme_str = command_result.data["numbering_scheme"]
            persist_to_database = command_result.data["persist_to_database"]
            organism = command_result.data["organism"]

            # Convert numbering scheme string to enum
            numbering_scheme_map = {
                "imgt": NumberingScheme.IMGT,
                "kabat": NumberingScheme.KABAT,
                "chothia": NumberingScheme.CHOTHIA,
                "martin": NumberingScheme.MARTIN,
                "aho": NumberingScheme.AHO,
                "cgg": NumberingScheme.CGG,
            }
            numbering_scheme = numbering_scheme_map.get(
                numbering_scheme_str, NumberingScheme.IMGT
            )

            # Process each sequence
            answer = []
            processor = AnarciResultProcessor(
                input_dict=sequences, numbering_scheme=numbering_scheme
            )

            anarci_results: List[AnarciResultObject] = processor.results
            for anarci_result in anarci_results:
                try:
                    answer.append(
                        {
                            "name": anarci_result.biologic_name,
                            "result": anarci_result,
                            "success": True,
                        }
                    )

                    # if persist_to_database:
                    #     await self.biologic_service.process_and_persist_biologic_entity(
                    #         results.data, organism
                    #     )

                except Exception as e:
                    logger.error(
                        f"Error processing sequence {anarci_result.biologic_name}: {e}"
                    )
                    answer.append(
                        {
                            "name": anarci_result.biologic_name,
                            "error": str(e),
                            "success": False,
                        }
                    )

            # Format the response
            formatted_response = (
                self.response_service.format_workflow_response(answer)
            )

            return self._create_success_response(formatted_response)

        except Exception as e:
            logger.error(f"Error handling workflow command: {e}")
            return self._create_error_response(
                f"Workflow handler error: {str(e)}"
            )

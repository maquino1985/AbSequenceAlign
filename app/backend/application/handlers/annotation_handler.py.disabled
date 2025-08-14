"""
Handler for annotation commands.
"""

from typing import Dict, Any

from .base_handler import BaseHandler
from ..commands.base_command import BaseCommand
from ..services.annotation_service import AnnotationService
from ..services.validation_service import ValidationService
from ..services.response_service import ResponseService
from backend.logger import logger


class AnnotationHandler(BaseHandler):
    """Handler for annotation commands"""

    def __init__(
        self,
        annotation_service: AnnotationService,
        validation_service: ValidationService,
        response_service: ResponseService,
    ):
        """
        Initialize the annotation handler.

        Args:
            annotation_service: Service for sequence annotation
            validation_service: Service for data validation
            response_service: Service for response formatting
        """
        super().__init__()
        self.annotation_service = annotation_service
        self.validation_service = validation_service
        self.response_service = response_service

    async def handle(self, command: BaseCommand) -> Dict[str, Any]:
        """
        Handle an annotation command.

        Args:
            command: The annotation command to handle

        Returns:
            Dictionary containing the annotation result
        """
        try:
            logger.info(f"Handling annotation command: {command}")

            # Execute the command to validate and prepare data
            command_result = command.execute()
            if not command_result.success:
                return self._create_error_response(command_result.error)

            # Extract data from command result
            sequence = command_result.data["sequence"]
            numbering_scheme = command_result.data["numbering_scheme"]

            # Validate the sequence
            if not self.validation_service.validate_sequence(sequence):
                return self._create_error_response("Invalid sequence data")

            # Perform annotation
            annotation_result = self.annotation_service.annotate_sequence(
                sequence, numbering_scheme
            )

            if not annotation_result.success:
                return self._create_error_response(
                    f"Annotation failed: {annotation_result.error}"
                )

            # Format the response
            formatted_response = (
                self.response_service.format_annotation_response(
                    annotation_result
                )
            )

            return self._create_success_response(formatted_response)

        except Exception as e:
            logger.error(f"Error handling annotation command: {e}")
            return self._create_error_response(
                f"Annotation handler error: {str(e)}"
            )

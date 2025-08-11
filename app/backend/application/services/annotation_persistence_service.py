"""
Service for handling annotation persistence integration.
Manages the integration between annotation services and biologic persistence.
"""

from typing import Dict, Any, Optional

from backend.annotation.anarci_result_processor import AnarciResultProcessor
from backend.application.factories.biologic_factory import create_biologic_service


class AnnotationPersistenceService:
    """Service for handling annotation persistence integration"""

    def __init__(self):
        self._biologic_service = None

    async def annotate_and_persist_sequence(
        self,
        db_session,
        input_dict: Dict[str, Any],
        numbering_scheme: str = "imgt",
        organism: Optional[str] = None,
    ):
        """
        Annotate a sequence and persist it as a biologic entity.

        This method demonstrates the integration pattern:
        1. Use domain entities for annotation (business logic)
        2. Convert to ORM models for persistence
        3. Return Pydantic models for API responses
        """
        # Initialize biologic service if not already done
        if self._biologic_service is None:
            self._biologic_service = create_biologic_service(
                "default", session=db_session
            )

        # Step 1: Process with AnarciResultProcessor
        processor = AnarciResultProcessor(
            input_dict, numbering_scheme=numbering_scheme
        )

        # Step 2: Convert processor results to domain entities
        # This would be done by AnnotationProcessorService
        from backend.application.services.annotation_processor_service import AnnotationProcessorService
        processor_service = AnnotationProcessorService()
        biologic_entity = processor_service.create_biologic_entity_from_processor(
            processor
        )

        # Step 3: Use biologic service to persist as ORM models
        biologic_response = (
            await self._biologic_service.process_and_persist_biologic_entity(
                db_session, biologic_entity, organism
            )
        )

        # Step 4: Return both the biologic response and the original annotation result
        # This would be done by AnnotationResponseService
        from backend.application.services.annotation_response_service import AnnotationResponseService
        response_service = AnnotationResponseService()
        annotation_result = response_service.create_api_response_from_processor(
            processor, numbering_scheme
        )

        return {"biologic": biologic_response, "annotation": annotation_result}

    def get_biologic_service(self):
        """Get the biologic service instance"""
        return self._biologic_service

    def set_biologic_service(self, biologic_service):
        """Set the biologic service instance"""
        self._biologic_service = biologic_service

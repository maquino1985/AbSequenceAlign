"""
Database persistence step for the annotation pipeline.
Persists annotated antibody sequences to the database.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from ...core.base_classes import AbstractPipelineStep
from ...core.interfaces import PipelineContext, ProcessingResult
from ...domain.entities import AntibodySequence
from ...services.antibody_database_service import AntibodyDatabaseService
from backend.logger import logger


class DatabasePersistenceStep(AbstractPipelineStep):
    """Pipeline step for persisting annotated antibody sequences to the database."""

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.database_service = AntibodyDatabaseService(session)

    async def process(
        self, context: PipelineContext, **kwargs
    ) -> ProcessingResult:
        """Process the pipeline step by persisting the annotated sequence to the database."""
        try:
            logger.info("Starting database persistence step")

            # Get the annotated sequence from context
            annotated_sequence = context.get_data("annotated_sequence")
            if not annotated_sequence:
                logger.warning(
                    "No annotated sequence found in context for database persistence"
                )
                return ProcessingResult(
                    success=False,
                    error="No annotated sequence found in context",
                )

            if not isinstance(annotated_sequence, AntibodySequence):
                logger.error(
                    f"Invalid annotated sequence type: {type(annotated_sequence)}"
                )
                return ProcessingResult(
                    success=False, error="Invalid annotated sequence type"
                )

            # Persist the sequence to the database
            persistence_result = (
                await self.database_service.save_antibody_sequence(
                    annotated_sequence, persist_metadata=True
                )
            )

            if not persistence_result.success:
                logger.error(
                    f"Database persistence failed: {persistence_result.error}"
                )
                return ProcessingResult(
                    success=False,
                    error=f"Database persistence failed: {persistence_result.error}",
                )

            # Add the saved sequence to the context
            saved_sequence = persistence_result.data.get("saved_sequence")
            context.add_data("saved_sequence", saved_sequence)
            context.add_data(
                "persistence_metadata", persistence_result.metadata
            )

            logger.info(
                f"Successfully persisted antibody sequence: {saved_sequence.name}"
            )

            return ProcessingResult(
                success=True,
                data={
                    "saved_sequence": saved_sequence,
                    "persistence_metadata": persistence_result.metadata,
                },
                metadata={
                    "step": "database_persistence",
                    "sequence_name": saved_sequence.name,
                    "chains_count": len(saved_sequence.chains),
                    "total_domains": sum(
                        len(chain.domains) for chain in saved_sequence.chains
                    ),
                    "total_regions": sum(
                        len(domain.regions)
                        for chain in saved_sequence.chains
                        for domain in chain.domains
                    ),
                },
            )

        except Exception as e:
            error_msg = f"Database persistence step failed: {str(e)}"
            logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def can_handle(self, context: PipelineContext) -> bool:
        """Check if this step can handle the current context."""
        # This step can handle any context that has an annotated sequence
        return context.has_data("annotated_sequence")

    def get_step_name(self) -> str:
        """Get the name of this pipeline step."""
        return "database_persistence"

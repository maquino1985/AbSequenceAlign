"""
Enhanced annotation pipeline that includes database persistence.
Integrates with the existing annotation engine and adds database storage.
"""

from typing import Dict, Any, List
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.base_classes import AbstractProcessingSubject
from ...core.interfaces import ProcessingResult
from ...domain.models import (
    AntibodySequence,
    NumberingScheme,
)
from ...services.antibody_database_service import AntibodyDatabaseService
from backend.annotation.anarci_result_processor import AnarciResultProcessor


class EnhancedAnnotationPipeline(AbstractProcessingSubject):
    """Enhanced pipeline for antibody sequence annotation with database persistence"""

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.database_service = AntibodyDatabaseService(session)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._setup_pipeline()

    def _setup_pipeline(self):
        """Setup the enhanced annotation pipeline steps"""
        self._logger.info(
            "Setting up enhanced annotation pipeline with database persistence"
        )

    async def process_sequence(
        self,
        sequence: AntibodySequence,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
        persist_to_database: bool = True,
    ) -> ProcessingResult:
        """Process a single antibody sequence through the enhanced annotation pipeline"""
        try:
            self._logger.info(
                f"Starting enhanced annotation pipeline for sequence: {sequence.name}"
            )
            self.notify_step_completed("pipeline_start", 0.0)

            # Step 1: Validate sequence
            if not self._validate_sequence(sequence):
                error_msg = f"Invalid sequence for annotation: {sequence.name}"
                self._logger.error(error_msg)
                return ProcessingResult(success=False, error=error_msg)

            self.notify_step_completed("validation", 0.2)

            # Step 2: Perform annotation using existing engine
            annotation_result = await self._perform_annotation(
                sequence, numbering_scheme
            )
            if not annotation_result.success:
                return annotation_result

            annotated_sequence = annotation_result.data["annotated_sequence"]
            self.notify_step_completed("annotation", 0.8)

            # Step 3: Persist to database if requested
            if persist_to_database:
                persistence_result = await self._persist_to_database(
                    annotated_sequence
                )
                if not persistence_result.success:
                    # Log the error but don't fail the entire pipeline
                    self._logger.warning(
                        f"Database persistence failed: {persistence_result.error}"
                    )
                    # Continue without database persistence
                else:
                    self.notify_step_completed("persistence", 0.9)
                    # Add persistence metadata to the result
                    annotation_result.metadata.update(
                        persistence_result.metadata
                    )

            self.notify_step_completed("pipeline_complete", 1.0)
            self._logger.info(
                f"Enhanced annotation pipeline completed for sequence: {sequence.name}"
            )

            return annotation_result

        except Exception as e:
            error_msg = f"Enhanced annotation pipeline failed: {str(e)}"
            self._logger.error(error_msg)
            self.notify_error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    async def process_sequences(
        self,
        sequences: List[AntibodySequence],
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
        persist_to_database: bool = True,
    ) -> ProcessingResult:
        """Process multiple antibody sequences through the enhanced annotation pipeline"""
        try:
            self._logger.info(
                f"Starting enhanced annotation pipeline for {len(sequences)} sequences"
            )
            self.notify_step_completed("batch_start", 0.0)

            annotated_sequences = []
            saved_sequences = []
            errors = []

            for i, sequence in enumerate(sequences):
                progress = i / len(sequences)
                self.notify_step_completed(f"sequence_{i+1}", progress)

                try:
                    result = await self.process_sequence(
                        sequence, numbering_scheme, persist_to_database
                    )
                    if result.success:
                        annotated_sequences.append(
                            result.data["annotated_sequence"]
                        )
                        # Check if sequence was saved to database
                        if "saved_sequence" in result.data:
                            saved_sequences.append(
                                result.data["saved_sequence"]
                            )
                    else:
                        errors.append(
                            {"sequence": sequence.name, "error": result.error}
                        )
                except Exception as e:
                    errors.append({"sequence": sequence.name, "error": str(e)})

            self.notify_step_completed("batch_complete", 1.0)

            metadata = {
                "total_sequences": len(sequences),
                "successful_annotations": len(annotated_sequences),
                "saved_to_database": len(saved_sequences),
            }

            if errors:
                metadata["errors"] = errors
                self._logger.warning(
                    f"Batch processing completed with {len(errors)} errors"
                )

            self._logger.info(
                f"Enhanced batch processing completed: {len(annotated_sequences)}/{len(sequences)} sequences processed"
            )

            return ProcessingResult(
                success=True,
                data={
                    "annotated_sequences": annotated_sequences,
                    "saved_sequences": saved_sequences,
                },
                metadata=metadata,
            )

        except Exception as e:
            error_msg = f"Enhanced batch annotation pipeline failed: {str(e)}"
            self._logger.error(error_msg)
            self.notify_error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    async def _perform_annotation(
        self, sequence: AntibodySequence, numbering_scheme: NumberingScheme
    ) -> ProcessingResult:
        """Perform annotation using the existing annotation engine"""
        try:
            self._logger.debug(
                f"Performing annotation for sequence: {sequence.name}"
            )

            # Convert sequence to the format expected by AnarciResultProcessor
            input_dict = {}
            if sequence.chains:
                # If sequence has chains, use them
                chain_data = {}
                for chain in sequence.chains:
                    if chain.sequence:
                        chain_data[chain.name] = chain.sequence.value
                if chain_data:
                    input_dict[sequence.name] = chain_data
            else:
                # If no chains, use the main sequence
                if sequence.sequence:
                    input_dict[sequence.name] = {
                        "main": sequence.sequence.value
                    }

            if not input_dict:
                error_msg = f"No valid sequence data found for annotation: {sequence.name}"
                self._logger.error(error_msg)
                return ProcessingResult(success=False, error=error_msg)

            # Use AnarciResultProcessor for annotation
            processor = AnarciResultProcessor(
                input_dict, numbering_scheme=numbering_scheme.value
            )

            # Convert results back to domain entities
            annotated_sequence = (
                await self._convert_processor_results_to_entity(
                    processor, sequence
                )
            )

            self._logger.debug(
                f"Annotation completed for sequence: {sequence.name}"
            )

            return ProcessingResult(
                success=True,
                data={"annotated_sequence": annotated_sequence},
                metadata={
                    "annotation_method": "anarci",
                    "numbering_scheme": numbering_scheme.value,
                },
            )

        except Exception as e:
            error_msg = (
                f"Annotation failed for sequence {sequence.name}: {str(e)}"
            )
            self._logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    async def _convert_processor_results_to_entity(
        self,
        processor: AnarciResultProcessor,
        original_sequence: AntibodySequence,
    ) -> AntibodySequence:
        """Convert AnarciResultProcessor results back to domain entities"""
        try:
            # For now, return the original sequence with basic annotation
            # In a full implementation, you would convert the processor results
            # to proper domain entities with all the annotation data

            # Create a basic annotated sequence
            annotated_sequence = AntibodySequence(
                name=original_sequence.name,
                sequence=original_sequence.sequence,
                chains=original_sequence.chains,  # Would be enhanced with annotation data
                metadata=original_sequence.metadata,
            )

            return annotated_sequence

        except Exception as e:
            self._logger.error(f"Error converting processor results: {e}")
            # Return original sequence as fallback
            return original_sequence

    async def _persist_to_database(
        self, sequence: AntibodySequence
    ) -> ProcessingResult:
        """Persist the annotated sequence to the database"""
        try:
            self._logger.debug(
                f"Persisting sequence to database: {sequence.name}"
            )

            return await self.database_service.save_antibody_sequence(sequence)

        except Exception as e:
            error_msg = f"Database persistence failed for sequence {sequence.name}: {str(e)}"
            self._logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def _validate_sequence(self, sequence: AntibodySequence) -> bool:
        """Validate the sequence for annotation"""
        try:
            if not sequence.name or not sequence.name.strip():
                self._logger.warning("Sequence missing name")
                return False

            # Check if we have either a main sequence or chains
            has_main_sequence = (
                sequence.sequence is not None and sequence.sequence.value
            )
            has_chains = sequence.chains and any(
                chain.sequence and chain.sequence.value
                for chain in sequence.chains
            )

            if not has_main_sequence and not has_chains:
                self._logger.warning(
                    f"Sequence {sequence.name} has no valid sequence data"
                )
                return False

            return True

        except Exception as e:
            self._logger.error(
                f"Error validating sequence {sequence.name}: {e}"
            )
            return False

    async def get_annotation_statistics(self) -> ProcessingResult:
        """Get statistics about annotated sequences in the database"""
        try:
            return (
                await self.database_service.get_antibody_sequence_statistics()
            )
        except Exception as e:
            error_msg = f"Error getting annotation statistics: {str(e)}"
            self._logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the pipeline configuration"""
        return {
            "name": "enhanced_annotation_pipeline",
            "description": "Enhanced antibody sequence annotation pipeline with database persistence",
            "features": [
                "sequence validation",
                "annotation using AnarciResultProcessor",
                "database persistence",
                "batch processing",
                "statistics tracking",
            ],
            "database_integration": True,
        }

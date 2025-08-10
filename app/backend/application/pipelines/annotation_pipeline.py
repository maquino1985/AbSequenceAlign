"""
Annotation pipeline implementing the Chain of Responsibility pattern.
Orchestrates the annotation workflow through a series of processing steps.
"""

from typing import Dict, Any, List, Optional
import logging

from ...core.base_classes import AbstractProcessingSubject
from ...core.interfaces import PipelineContext, ProcessingResult
from ...core.exceptions import PipelineError
from ...domain.models import (
    AntibodySequence,
    NumberingScheme,
)
from .steps.validation_step import (
    SequenceValidationStep,
)


class AnnotationPipeline(AbstractProcessingSubject):
    """Pipeline for antibody sequence annotation using Chain of Responsibility"""

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._steps = []
        self._setup_pipeline()

    def _setup_pipeline(self):
        """Setup the annotation pipeline steps"""
        # Step 1: Sequence validation
        validation_step = SequenceValidationStep()
        self._steps.append(validation_step)

        # Step 2: Chain validation
        chain_validation_step = ChainValidationStep()
        self._steps.append(chain_validation_step)

        # Step 3: Numbering
        numbering_step = NumberingStep()
        self._steps.append(numbering_step)

        # Step 4: Region annotation
        region_annotation_step = RegionAnnotationStep()
        self._steps.append(region_annotation_step)

        # Step 5: Isotype detection
        isotype_detection_step = IsotypeDetectionStep()
        self._steps.append(isotype_detection_step)

        # Chain the steps together
        for i in range(len(self._steps) - 1):
            self._steps[i].set_next(self._steps[i + 1])

        self._logger.info(f"Annotation pipeline setup with {len(self._steps)} steps")

    def process_sequence(
        self,
        sequence: AntibodySequence,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ) -> ProcessingResult:
        """Process a single antibody sequence through the annotation pipeline"""
        try:
            self._logger.info(
                f"Starting annotation pipeline for sequence: {sequence.name}"
            )
            self.notify_step_completed("pipeline_start", 0.0)

            # Create pipeline context
            context = PipelineContext(
                sequence=sequence,
                total_steps=len(self._steps),
                metadata={
                    "numbering_scheme": numbering_scheme.value,
                    "pipeline_type": "annotation",
                },
            )

            # Execute pipeline starting with the first step
            if self._steps:
                final_context = self._steps[0].execute(context)
            else:
                raise PipelineError(
                    "No pipeline steps configured", pipeline_name="annotation"
                )

            # Check for errors
            if final_context.errors:
                error_msg = f"Pipeline failed with {len(final_context.errors)} errors"
                self._logger.error(error_msg)
                self.notify_error(error_msg)
                return ProcessingResult(
                    success=False,
                    error=error_msg,
                    metadata={"errors": final_context.errors},
                )

            # Extract annotated sequence from context
            annotated_sequence = self._extract_annotated_sequence(final_context)

            self.notify_step_completed("pipeline_complete", 1.0)
            self._logger.info(
                f"Annotation pipeline completed for sequence: {sequence.name}"
            )

            return ProcessingResult(
                success=True,
                data={"annotated_sequence": annotated_sequence},
                metadata={
                    "steps_completed": final_context.completed_steps,
                    "total_steps": final_context.total_steps,
                    "step_results": final_context.step_results,
                },
            )

        except Exception as e:
            error_msg = f"Annotation pipeline failed: {str(e)}"
            self._logger.error(error_msg)
            self.notify_error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def process_sequences(
        self,
        sequences: List[AntibodySequence],
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ) -> ProcessingResult:
        """Process multiple antibody sequences through the annotation pipeline"""
        try:
            self._logger.info(
                f"Starting annotation pipeline for {len(sequences)} sequences"
            )
            self.notify_step_completed("batch_start", 0.0)

            annotated_sequences = []
            errors = []

            for i, sequence in enumerate(sequences):
                progress = i / len(sequences)
                self.notify_step_completed(f"sequence_{i+1}", progress)

                try:
                    result = self.process_sequence(sequence, numbering_scheme)
                    if result.success:
                        annotated_sequences.append(result.data["annotated_sequence"])
                    else:
                        errors.append(
                            {"sequence": sequence.name, "error": result.error}
                        )
                except Exception as e:
                    errors.append({"sequence": sequence.name, "error": str(e)})

            self.notify_step_completed("batch_complete", 1.0)

            if errors:
                self._logger.warning(
                    f"Batch processing completed with {len(errors)} errors"
                )
                return ProcessingResult(
                    success=True,  # Partial success
                    data={"annotated_sequences": annotated_sequences},
                    metadata={
                        "total_sequences": len(sequences),
                        "successful_annotations": len(annotated_sequences),
                        "errors": errors,
                    },
                )
            else:
                self._logger.info(
                    f"Batch processing completed successfully for {len(sequences)} sequences"
                )
                return ProcessingResult(
                    success=True,
                    data={"annotated_sequences": annotated_sequences},
                    metadata={
                        "total_sequences": len(sequences),
                        "successful_annotations": len(annotated_sequences),
                    },
                )

        except Exception as e:
            error_msg = f"Batch annotation pipeline failed: {str(e)}"
            self._logger.error(error_msg)
            self.notify_error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def _extract_annotated_sequence(self, context: PipelineContext) -> AntibodySequence:
        """Extract the annotated sequence from the pipeline context"""
        # The annotated sequence should be in the context after processing
        # For now, return the original sequence (this would be enhanced in real implementation)
        return context.sequence

    def add_step(self, step, position: Optional[int] = None):
        """Add a step to the pipeline"""
        if position is None:
            position = len(self._steps)

        if position < 0 or position > len(self._steps):
            raise PipelineError(
                f"Invalid step position: {position}",
                pipeline_name="annotation",
            )

        self._steps.insert(position, step)
        self._logger.info(f"Added step at position {position}: {step.name}")

        # Rechain the steps
        self._rechain_steps()

    def remove_step(self, step_name: str):
        """Remove a step from the pipeline"""
        for i, step in enumerate(self._steps):
            if step.name == step_name:
                del self._steps[i]
                self._logger.info(f"Removed step: {step_name}")
                self._rechain_steps()
                return

        raise PipelineError(f"Step not found: {step_name}", pipeline_name="annotation")

    def _rechain_steps(self):
        """Rechain the pipeline steps"""
        for i in range(len(self._steps) - 1):
            self._steps[i].set_next(self._steps[i + 1])

        # Clear the next step of the last step
        if self._steps:
            self._steps[-1].set_next(None)

    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the pipeline configuration"""
        return {
            "name": "annotation_pipeline",
            "steps": [step.name for step in self._steps],
            "total_steps": len(self._steps),
            "description": "Antibody sequence annotation pipeline using Chain of Responsibility pattern",
        }

    def validate_pipeline(self) -> bool:
        """Validate the pipeline configuration"""
        if not self._steps:
            self._logger.error("Pipeline has no steps")
            return False

        # Check that all steps are properly configured
        for step in self._steps:
            if not hasattr(step, "name") or not step.name:
                self._logger.error(f"Step missing name: {step}")
                return False

        self._logger.info("Pipeline validation passed")
        return True


# Placeholder classes for pipeline steps that will be implemented later
class ChainValidationStep:
    """Pipeline step for validating antibody chains"""

    def __init__(self):
        self.name = "chain_validation"
        self.next_step = None

    def set_next(self, step):
        self.next_step = step
        return step

    def execute(self, context):
        # Placeholder implementation
        context.completed_steps += 1
        return context


class NumberingStep:
    """Pipeline step for sequence numbering"""

    def __init__(self):
        self.name = "numbering"
        self.next_step = None

    def set_next(self, step):
        self.next_step = step
        return step

    def execute(self, context):
        # Placeholder implementation
        context.completed_steps += 1
        return context


class RegionAnnotationStep:
    """Pipeline step for region annotation"""

    def __init__(self):
        self.name = "region_annotation"
        self.next_step = None

    def set_next(self, step):
        self.next_step = step
        return step

    def execute(self, context):
        # Placeholder implementation
        context.completed_steps += 1
        return context


class IsotypeDetectionStep:
    """Pipeline step for isotype detection"""

    def __init__(self):
        self.name = "isotype_detection"
        self.next_step = None

    def set_next(self, step):
        self.next_step = step
        return step

    def execute(self, context):
        # Placeholder implementation
        context.completed_steps += 1
        return context

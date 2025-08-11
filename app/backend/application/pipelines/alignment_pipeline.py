"""
Alignment pipeline implementing the Chain of Responsibility pattern.
Orchestrates the alignment workflow through a series of processing steps.
"""

from typing import Dict, Any, List, Optional
import logging

from ...core.base_classes import AbstractProcessingSubject
from ...core.interfaces import PipelineContext, ProcessingResult
from ...core.exceptions import PipelineError
from ...domain.models import (
    AntibodySequence,
    RegionType,
)
from .steps.validation_step import SequenceValidationStep


class AlignmentPipeline(AbstractProcessingSubject):
    """Pipeline for sequence alignment using Chain of Responsibility"""

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._steps = []
        self._setup_pipeline()

    def _setup_pipeline(self) -> None:
        """Setup the alignment pipeline steps"""
        # Step 1: Sequence validation
        validation_step = SequenceValidationStep()
        self._steps.append(validation_step)

        # Step 2: Sequence preparation
        preparation_step = SequencePreparationStep()
        self._steps.append(preparation_step)

        # Step 3: Alignment strategy selection
        strategy_step = AlignmentStrategyStep()
        self._steps.append(strategy_step)

        # Step 4: Alignment execution
        alignment_step = AlignmentExecutionStep()
        self._steps.append(alignment_step)

        # Step 5: Result processing
        processing_step = ResultProcessingStep()
        self._steps.append(processing_step)

        # Chain the steps together
        for i in range(len(self._steps) - 1):
            self._steps[i].set_next(self._steps[i + 1])

        self._logger.info(
            f"Alignment pipeline setup with {len(self._steps)} steps"
        )

    def align_sequences(
        self,
        sequences: List[AntibodySequence],
        strategy: str = "multiple",
        **kwargs,
    ) -> ProcessingResult:
        """Align sequences through the alignment pipeline"""
        try:
            self._logger.info(
                f"Starting alignment pipeline for {len(sequences)} sequences"
            )
            self.notify_step_completed("pipeline_start", 0.0)

            # Create pipeline context
            context = PipelineContext(
                sequence=sequences[0] if sequences else None,
                total_steps=len(self._steps),
                metadata={
                    "strategy": strategy,
                    "sequences_count": len(sequences),
                    "pipeline_type": "alignment",
                    **kwargs,
                },
            )

            # Add sequences to context
            context.metadata["sequences"] = sequences

            # Execute pipeline starting with the first step
            if self._steps:
                final_context = self._steps[0].execute(context)
            else:
                raise PipelineError(
                    "No pipeline steps configured", pipeline_name="alignment"
                )

            # Check for errors
            if final_context.errors:
                error_msg = (
                    f"Pipeline failed with {len(final_context.errors)} errors"
                )
                self._logger.error(error_msg)
                self.notify_error(error_msg)
                return ProcessingResult(
                    success=False,
                    error=error_msg,
                    metadata={"errors": final_context.errors},
                )

            # Extract alignment result from context
            alignment_result = self._extract_alignment_result(final_context)

            self.notify_step_completed("pipeline_complete", 1.0)
            self._logger.info(
                f"Alignment pipeline completed for {len(sequences)} sequences"
            )

            return ProcessingResult(
                success=True,
                data={"alignment_result": alignment_result},
                metadata={
                    "steps_completed": final_context.completed_steps,
                    "total_steps": final_context.total_steps,
                    "step_results": final_context.step_results,
                    "strategy": strategy,
                },
            )

        except Exception as e:
            error_msg = f"Alignment pipeline failed: {str(e)}"
            self._logger.error(error_msg)
            self.notify_error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def align_regions(
        self,
        sequences: List[AntibodySequence],
        region_type: RegionType,
        **kwargs,
    ) -> ProcessingResult:
        """Align specific regions through the alignment pipeline"""
        try:
            self._logger.info(
                f"Starting region alignment pipeline for {region_type.value}"
            )
            self.notify_step_completed("region_pipeline_start", 0.0)

            # Create pipeline context for region alignment
            context = PipelineContext(
                sequence=sequences[0] if sequences else None,
                total_steps=len(self._steps),
                metadata={
                    "strategy": "region_specific",
                    "region_type": region_type.value,
                    "sequences_count": len(sequences),
                    "pipeline_type": "region_alignment",
                    **kwargs,
                },
            )

            # Add sequences to context
            context.metadata["sequences"] = sequences

            # Execute pipeline starting with the first step
            if self._steps:
                final_context = self._steps[0].execute(context)
            else:
                raise PipelineError(
                    "No pipeline steps configured", pipeline_name="alignment"
                )

            # Check for errors
            if final_context.errors:
                error_msg = f"Region alignment pipeline failed with {len(final_context.errors)} errors"
                self._logger.error(error_msg)
                self.notify_error(error_msg)
                return ProcessingResult(
                    success=False,
                    error=error_msg,
                    metadata={"errors": final_context.errors},
                )

            # Extract region alignment result from context
            alignment_result = self._extract_alignment_result(final_context)

            self.notify_step_completed("region_pipeline_complete", 1.0)
            self._logger.info(
                f"Region alignment pipeline completed for {region_type.value}"
            )

            return ProcessingResult(
                success=True,
                data={"alignment_result": alignment_result},
                metadata={
                    "steps_completed": final_context.completed_steps,
                    "total_steps": final_context.total_steps,
                    "step_results": final_context.step_results,
                    "region_type": region_type.value,
                },
            )

        except Exception as e:
            error_msg = f"Region alignment pipeline failed: {str(e)}"
            self._logger.error(error_msg)
            self.notify_error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def _extract_alignment_result(
        self, context: PipelineContext
    ) -> Dict[str, Any]:
        """Extract the alignment result from the pipeline context"""
        # The alignment result should be in the context after processing
        # For now, return a placeholder (this would be enhanced in real implementation)
        return {
            "type": "alignment",
            "sequences": context.metadata.get("sequences_count", 0),
            "strategy": context.metadata.get("strategy", "unknown"),
            "step_results": context.step_results,
        }

    def add_step(self, step, position: Optional[int] = None):
        """Add a step to the pipeline"""
        if position is None:
            position = len(self._steps)

        if position < 0 or position > len(self._steps):
            raise PipelineError(
                f"Invalid step position: {position}", pipeline_name="alignment"
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

        raise PipelineError(
            f"Step not found: {step_name}", pipeline_name="alignment"
        )

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
            "name": "alignment_pipeline",
            "steps": [step.name for step in self._steps],
            "total_steps": len(self._steps),
            "description": "Sequence alignment pipeline using Chain of Responsibility pattern",
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
class SequencePreparationStep:
    """Pipeline step for preparing sequences for alignment"""

    def __init__(self):
        self.name = "sequence_preparation"
        self.next_step = None

    def set_next(self, step):
        self.next_step = step
        return step

    def execute(self, context):
        # Placeholder implementation
        context.completed_steps += 1
        return context


class AlignmentStrategyStep:
    """Pipeline step for selecting alignment strategy"""

    def __init__(self):
        self.name = "alignment_strategy"
        self.next_step = None

    def set_next(self, step):
        self.next_step = step
        return step

    def execute(self, context):
        # Placeholder implementation
        context.completed_steps += 1
        return context


class AlignmentExecutionStep:
    """Pipeline step for executing alignment"""

    def __init__(self):
        self.name = "alignment_execution"
        self.next_step = None

    def set_next(self, step):
        self.next_step = step
        return step

    def execute(self, context):
        # Placeholder implementation
        context.completed_steps += 1
        return context


class ResultProcessingStep:
    """Pipeline step for processing alignment results"""

    def __init__(self):
        self.name = "result_processing"
        self.next_step = None

    def set_next(self, step):
        self.next_step = step
        return step

    def execute(self, context):
        # Placeholder implementation
        context.completed_steps += 1
        return context

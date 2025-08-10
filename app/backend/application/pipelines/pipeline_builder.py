"""
Pipeline builder implementing the Builder pattern for constructing processing pipelines.
Allows dynamic creation and configuration of processing pipelines.
"""

from typing import Dict, Any, List, Optional, Type

from backend.core.base_classes import AbstractBuilder, AbstractPipelineStep
from backend.core.interfaces import ProcessingContext, ProcessingResult
from backend.core.exceptions import ProcessingError
from backend.domain.models import NumberingScheme
from backend.logger import logger


class PipelineBuilder(AbstractBuilder):
    """Builder for constructing processing pipelines"""

    def __init__(self):
        self._steps: List[AbstractPipelineStep] = []
        self._config: Dict[str, Any] = {}
        # Don't call super().__init__() to avoid the reset() call

    def reset(self) -> None:
        """Reset the builder state"""
        self._steps = []
        self._config = {}
        logger.debug("Pipeline builder reset")

    def add_step(
        self, step: AbstractPipelineStep, position: Optional[int] = None
    ) -> "PipelineBuilder":
        """Add a step to the pipeline"""
        if position is None:
            self._steps.append(step)
        else:
            self._steps.insert(position, step)

        logger.debug(f"Added step '{step.name}' to pipeline")
        return self

    def add_step_by_type(
        self,
        step_class: Type[AbstractPipelineStep],
        name: str,
        position: Optional[int] = None,
        **kwargs,
    ) -> "PipelineBuilder":
        """Add a step by class type"""
        step = step_class(name, **kwargs)
        return self.add_step(step, position)

    def remove_step(self, step_name: str) -> "PipelineBuilder":
        """Remove a step from the pipeline"""
        self._steps = [step for step in self._steps if step.name != step_name]
        logger.debug(f"Removed step '{step_name}' from pipeline")
        return self

    def configure(self, key: str, value: Any) -> "PipelineBuilder":
        """Configure the pipeline"""
        self._config[key] = value
        logger.debug(f"Configured pipeline with {key}={value}")
        return self

    def configure_numbering_scheme(self, scheme: NumberingScheme) -> "PipelineBuilder":
        """Configure the numbering scheme for the pipeline"""
        return self.configure("numbering_scheme", scheme)

    def configure_validation_level(self, level: str) -> "PipelineBuilder":
        """Configure the validation level"""
        return self.configure("validation_level", level)

    def configure_parallel_processing(self, enabled: bool) -> "PipelineBuilder":
        """Configure parallel processing"""
        return self.configure("parallel_processing", enabled)

    def build(self) -> "ProcessingPipeline":
        """Build and return the final pipeline"""
        if not self._steps:
            raise ProcessingError("Cannot build pipeline: no steps configured")

        pipeline = ProcessingPipeline(self._steps, self._config)
        logger.info(f"Built pipeline with {len(self._steps)} steps")
        return pipeline

    def get_step_names(self) -> List[str]:
        """Get the names of all steps in the pipeline"""
        return [step.name for step in self._steps]

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return self._config.copy()


class ProcessingPipeline:
    """A processing pipeline that executes steps in sequence"""

    def __init__(self, steps: List[AbstractPipelineStep], config: Dict[str, Any]):
        self.steps = steps
        self.config = config

    def execute(self, context: ProcessingContext) -> ProcessingResult:
        """Execute the pipeline with the given context"""
        try:
            logger.info(f"Executing pipeline with {len(self.steps)} steps")

            # Execute each step in sequence
            for i, step in enumerate(self.steps):
                step_progress = i / len(self.steps)
                logger.debug(f"Executing step {i+1}/{len(self.steps)}: {step.name}")

                # Execute the step
                context = step.execute(context)

                # Check for errors
                if context.errors:
                    error_msg = (
                        f"Pipeline failed at step '{step.name}': {context.errors[-1]}"
                    )
                    logger.error(error_msg)
                    return ProcessingResult(
                        success=False,
                        error=error_msg,
                        metadata={
                            "failed_step": step.name,
                            "step_index": i,
                            "total_steps": len(self.steps),
                        },
                    )

            logger.info("Pipeline execution completed successfully")
            return ProcessingResult(
                success=True,
                data={"context": context},
                metadata={
                    "total_steps": len(self.steps),
                    "completed_steps": len(self.steps),
                },
            )

        except Exception as e:
            error_msg = f"Pipeline execution failed: {str(e)}"
            logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def get_step_info(self) -> List[Dict[str, Any]]:
        """Get information about all steps in the pipeline"""
        return [
            {
                "name": step.name,
                "index": i,
                "can_execute": step.can_execute(ProcessingContext(sequence=None)),
            }
            for i, step in enumerate(self.steps)
        ]

    def validate(self) -> bool:
        """Validate the pipeline configuration"""
        if not self.steps:
            logger.error("Pipeline validation failed: no steps configured")
            return False

        # Check that all steps have unique names
        step_names = [step.name for step in self.steps]
        if len(step_names) != len(set(step_names)):
            logger.error("Pipeline validation failed: duplicate step names")
            return False

        logger.debug("Pipeline validation passed")
        return True


# =============================================================================
# PREDEFINED PIPELINE BUILDER METHODS
# =============================================================================


def create_annotation_pipeline(
    numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
) -> ProcessingPipeline:
    """Create a standard annotation pipeline"""
    builder = PipelineBuilder()

    builder.add_step_by_type(SequenceValidationStep, "sequence_validation")
    builder.add_step_by_type(ChainValidationStep, "chain_validation")
    builder.add_step_by_type(
        NumberingStep, "numbering", numbering_scheme=numbering_scheme
    )
    builder.add_step_by_type(RegionAnnotationStep, "region_annotation")
    builder.add_step_by_type(IsotypeDetectionStep, "isotype_detection")

    builder.configure_numbering_scheme(numbering_scheme)
    builder.configure_validation_level("strict")

    return builder.build()


def create_alignment_pipeline() -> ProcessingPipeline:
    """Create a standard alignment pipeline"""
    builder = PipelineBuilder()

    builder.add_step_by_type(SequenceValidationStep, "sequence_validation")
    builder.add_step_by_type(AlignmentPreparationStep, "alignment_preparation")
    builder.add_step_by_type(MSAStep, "msa_alignment")
    builder.add_step_by_type(AlignmentPostProcessingStep, "alignment_post_processing")

    builder.configure_parallel_processing(True)

    return builder.build()


def create_custom_pipeline(
    steps: List[str], config: Dict[str, Any] = None
) -> ProcessingPipeline:
    """Create a custom pipeline with specified steps"""
    builder = PipelineBuilder()

    # Step registry mapping step names to step classes
    step_registry = {
        "sequence_validation": SequenceValidationStep,
        "chain_validation": ChainValidationStep,
        "numbering": NumberingStep,
        "region_annotation": RegionAnnotationStep,
        "isotype_detection": IsotypeDetectionStep,
        "alignment_preparation": AlignmentPreparationStep,
        "msa_alignment": MSAStep,
        "alignment_post_processing": AlignmentPostProcessingStep,
    }

    for step_name in steps:
        if step_name in step_registry:
            builder.add_step_by_type(step_registry[step_name], step_name)
        else:
            raise ProcessingError(f"Unknown step type: {step_name}")

    if config:
        for key, value in config.items():
            builder.configure(key, value)

    return builder.build()


# =============================================================================
# PLACEHOLDER STEP CLASSES (to be implemented)
# =============================================================================


class SequenceValidationStep(AbstractPipelineStep):
    """Step for validating input sequences"""

    def _execute_step(self, context: ProcessingContext) -> Any:
        # Placeholder implementation
        return {"validated": True}


class ChainValidationStep(AbstractPipelineStep):
    """Step for validating antibody chains"""

    def _execute_step(self, context: ProcessingContext) -> Any:
        # Placeholder implementation
        return {"chains_validated": True}


class NumberingStep(AbstractPipelineStep):
    """Step for numbering sequences"""

    def __init__(
        self,
        name: str,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ):
        super().__init__(name)
        self.numbering_scheme = numbering_scheme

    def _execute_step(self, context: ProcessingContext) -> Any:
        # Placeholder implementation
        return {"numbered": True, "scheme": self.numbering_scheme}


class RegionAnnotationStep(AbstractPipelineStep):
    """Step for annotating regions"""

    def _execute_step(self, context: ProcessingContext) -> Any:
        # Placeholder implementation
        return {"regions_annotated": True}


class IsotypeDetectionStep(AbstractPipelineStep):
    """Step for detecting isotypes"""

    def _execute_step(self, context: ProcessingContext) -> Any:
        # Placeholder implementation
        return {"isotype_detected": True}


class AlignmentPreparationStep(AbstractPipelineStep):
    """Step for preparing sequences for alignment"""

    def _execute_step(self, context: ProcessingContext) -> Any:
        # Placeholder implementation
        return {"prepared": True}


class MSAStep(AbstractPipelineStep):
    """Step for performing multiple sequence alignment"""

    def _execute_step(self, context: ProcessingContext) -> Any:
        # Placeholder implementation
        return {"aligned": True}


class AlignmentPostProcessingStep(AbstractPipelineStep):
    """Step for post-processing alignment results"""

    def _execute_step(self, context: ProcessingContext) -> Any:
        # Placeholder implementation
        return {"post_processed": True}

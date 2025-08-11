"""
Processing service for orchestrating different types of sequence processing.
Implements the Strategy pattern and Observer pattern for flexible processing workflows.
"""

from typing import Dict, Any, List, Type
from datetime import datetime

from backend.core.base_classes import AbstractProcessingSubject
from backend.core.interfaces import (
    ProcessingContext,
    ProcessingResult,
    ProcessingObserver,
)
from backend.core.exceptions import ProcessingError, ValidationError
from backend.domain.entities import BiologicEntity
from backend.application.pipelines.pipeline_builder import (
    ProcessingPipeline,
    create_annotation_pipeline,
    create_alignment_pipeline,
    create_custom_pipeline,
)
from .annotation_service import AnnotationService
from .alignment_service import AlignmentService
from backend.logger import logger


class ProcessingService(AbstractProcessingSubject):
    """Service for orchestrating different types of sequence processing"""

    def __init__(self):
        super().__init__()
        self._annotation_service = AnnotationService()
        self._alignment_service = AlignmentService()
        self._pipeline_registry: Dict[str, Type[ProcessingPipeline]] = {}
        self._processing_strategies: Dict[str, Any] = {}
        self._setup_services()

    def _setup_services(self):
        """Setup processing services and register strategies"""
        # Register pipeline types
        self._pipeline_registry = {
            "annotation": create_annotation_pipeline,
            "alignment": create_alignment_pipeline,
            "custom": create_custom_pipeline,
        }

        # Register processing strategies
        self._processing_strategies = {
            "annotation": self._annotation_service,
            "alignment": self._alignment_service,
            "pipeline": self._execute_pipeline,
        }

        logger.info(
            "Processing service initialized with pipeline and strategy support"
        )

    def process_sequence(
        self,
        sequence: BiologicEntity,
        processing_type: str = "annotation",
        **kwargs,
    ) -> ProcessingResult:
        """Process a sequence using the specified processing type"""
        try:
            logger.info(
                f"Starting {processing_type} processing for sequence: {sequence.name}"
            )
            self.notify_step_completed("processing_start", 0.0)

            # Validate input
            if not self._validate_sequence(sequence):
                raise ValidationError(
                    "Invalid sequence for processing", field="sequence"
                )

            # Get processing strategy
            strategy = self._processing_strategies.get(processing_type)
            if not strategy:
                error_msg = f"Unknown processing type: {processing_type}"
                logger.error(error_msg)
                raise ProcessingError(error_msg)

            # Execute processing
            if processing_type == "pipeline":
                result = strategy(sequence, **kwargs)
            else:
                result = strategy.process_sequence(sequence, **kwargs)

            # Add processing metadata
            if result.success:
                result.metadata = result.metadata or {}
                result.metadata.update(
                    {
                        "processing_type": processing_type,
                        "processing_timestamp": datetime.now().isoformat(),
                        "sequence_name": sequence.name,
                    }
                )

            self.notify_step_completed("processing_complete", 1.0)
            logger.info(
                f"{processing_type} processing completed for sequence: {sequence.name}"
            )

            return result

        except Exception as e:
            error_msg = f"{processing_type} processing failed for sequence {sequence.name}: {str(e)}"
            logger.error(error_msg)
            self.notify_processing_failed(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def process_sequences_batch(
        self,
        sequences: List[BiologicEntity],
        processing_type: str = "annotation",
        parallel: bool = False,
        **kwargs,
    ) -> ProcessingResult:
        """Process multiple sequences in batch"""
        try:
            logger.info(
                f"Starting batch {processing_type} processing for {len(sequences)} sequences"
            )
            self.notify_step_completed("batch_start", 0.0)

            results = []
            total_sequences = len(sequences)

            for i, sequence in enumerate(sequences):
                progress = (
                    i / total_sequences
                ) * 0.9  # 90% for processing, 10% for completion
                self.notify_step_completed(f"sequence_{i+1}", progress)

                result = self.process_sequence(
                    sequence, processing_type, **kwargs
                )
                results.append(result)

                if not result.success:
                    logger.warning(
                        f"Sequence {sequence.name} processing failed: {result.error}"
                    )

            # Aggregate results
            successful_results = [r for r in results if r.success]
            failed_results = [r for r in results if not r.success]

            success_rate = (
                len(successful_results) / total_sequences
                if total_sequences > 0
                else 0
            )

            self.notify_step_completed("batch_complete", 1.0)
            logger.info(
                f"Batch processing completed. Success rate: {success_rate:.1%}"
            )

            return ProcessingResult(
                success=success_rate > 0,
                data={
                    "results": results,
                    "successful_count": len(successful_results),
                    "failed_count": len(failed_results),
                    "success_rate": success_rate,
                },
                metadata={
                    "processing_type": processing_type,
                    "total_sequences": total_sequences,
                    "parallel_processing": parallel,
                },
            )

        except Exception as e:
            error_msg = f"Batch processing failed: {str(e)}"
            logger.error(error_msg)
            self.notify_processing_failed(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def create_pipeline(
        self, pipeline_type: str, **config
    ) -> ProcessingPipeline:
        """Create a processing pipeline of the specified type"""
        try:
            if pipeline_type not in self._pipeline_registry:
                raise ProcessingError(
                    f"Unknown pipeline type: {pipeline_type}"
                )

            pipeline_creator = self._pipeline_registry[pipeline_type]
            pipeline = pipeline_creator(**config)

            logger.info(
                f"Created {pipeline_type} pipeline with {len(pipeline.steps)} steps"
            )
            return pipeline

        except Exception as e:
            error_msg = f"Failed to create {pipeline_type} pipeline: {str(e)}"
            logger.error(error_msg)
            raise ProcessingError(error_msg)

    def _execute_pipeline(
        self,
        sequence: BiologicEntity,
        pipeline: ProcessingPipeline,
        **kwargs,
    ) -> ProcessingResult:
        """Execute a custom pipeline on a sequence"""
        try:
            logger.info(
                f"Executing custom pipeline for sequence: {sequence.name}"
            )

            # Create processing context
            context = ProcessingContext(sequence=sequence, metadata=kwargs)

            # Execute pipeline
            result = pipeline.execute(context)

            if result.success:
                logger.info(
                    f"Pipeline execution completed successfully for sequence: {sequence.name}"
                )
            else:
                logger.error(
                    f"Pipeline execution failed for sequence: {sequence.name}: {result.error}"
                )

            return result

        except Exception as e:
            error_msg = f"Pipeline execution failed for sequence {sequence.name}: {str(e)}"
            logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def register_pipeline_type(self, name: str, pipeline_creator) -> None:
        """Register a new pipeline type"""
        self._pipeline_registry[name] = pipeline_creator
        logger.info(f"Registered new pipeline type: {name}")

    def register_processing_strategy(self, name: str, strategy: Any) -> None:
        """Register a new processing strategy"""
        self._processing_strategies[name] = strategy
        logger.info(f"Registered new processing strategy: {name}")

    def get_available_pipeline_types(self) -> List[str]:
        """Get list of available pipeline types"""
        return list(self._pipeline_registry.keys())

    def get_available_processing_types(self) -> List[str]:
        """Get list of available processing types"""
        return list(self._processing_strategies.keys())

    def _validate_sequence(self, sequence: BiologicEntity) -> bool:
        """Validate sequence for processing"""
        if not sequence or not sequence.name:
            return False

        if not sequence.chains:
            return False

        return True


class ProgressTrackingObserver(ProcessingObserver):
    """Observer for tracking processing progress"""

    def __init__(self):
        self.progress_history: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.completed = False
        self.final_result = None

    def on_step_completed(self, step_name: str, progress: float) -> None:
        """Called when a processing step is completed"""
        self.progress_history.append(
            {
                "step": step_name,
                "progress": progress,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def on_error(self, error: str) -> None:
        """Called when an error occurs during processing"""
        self.errors.append(
            {"error": error, "timestamp": datetime.now().isoformat()}
        )

    def on_processing_failed(self, error: str) -> None:
        """Called when processing fails"""
        self.errors.append(
            {"error": error, "timestamp": datetime.now().isoformat()}
        )

    def on_processing_completed(self, result: Any) -> None:
        """Called when processing is completely finished"""
        self.completed = True
        self.final_result = result

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of the processing progress"""
        return {
            "completed": self.completed,
            "total_steps": len(self.progress_history),
            "current_progress": (
                self.progress_history[-1]["progress"]
                if self.progress_history
                else 0.0
            ),
            "error_count": len(self.errors),
            "has_errors": len(self.errors) > 0,
        }

    def get_latest_progress(self) -> float:
        """Get the latest progress value"""
        if self.progress_history:
            return self.progress_history[-1]["progress"]
        return 0.0


class ProcessingServiceFactory:
    """Factory for creating processing services with different configurations"""

    @staticmethod
    def create_standard_service() -> ProcessingService:
        """Create a standard processing service"""
        return ProcessingService()

    @staticmethod
    def create_service_with_observers(
        observers: List[ProcessingObserver],
    ) -> ProcessingService:
        """Create a processing service with attached observers"""
        service = ProcessingService()
        for observer in observers:
            service.attach(observer)
        return service

    @staticmethod
    def create_service_with_custom_pipelines(
        custom_pipelines: Dict[str, Type[ProcessingPipeline]],
    ) -> ProcessingService:
        """Create a processing service with custom pipeline types"""
        service = ProcessingService()
        for name, pipeline_creator in custom_pipelines.items():
            service.register_pipeline_type(name, pipeline_creator)
        return service

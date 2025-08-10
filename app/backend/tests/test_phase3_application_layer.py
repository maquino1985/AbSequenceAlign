"""
Tests for Phase 3: Application Layer implementation.
Verifies pipeline pattern, application services, and observer pattern functionality.
"""

import pytest
from datetime import datetime

from backend.application.pipelines.pipeline_builder import (
    PipelineBuilder,
    ProcessingPipeline,
    create_annotation_pipeline,
    create_alignment_pipeline,
    create_custom_pipeline,
)
from backend.application.services.processing_service import (
    ProcessingService,
    ProgressTrackingObserver,
    ProcessingServiceFactory,
)
from backend.core.interfaces import (
    ProcessingContext,
    ProcessingResult,
    ProcessingObserver,
)
from backend.domain.entities import (
    AntibodySequence,
    AntibodyChain,
    AntibodyDomain,
)
from backend.domain.value_objects import AminoAcidSequence
from backend.domain.models import ChainType, DomainType, NumberingScheme
from backend.core.exceptions import ProcessingError, ValidationError


class TestPipelineBuilder:
    """Test pipeline builder functionality"""

    def test_pipeline_builder_creation(self):
        """Test creating a pipeline builder"""
        builder = PipelineBuilder()
        assert builder is not None
        assert len(builder.get_step_names()) == 0

    def test_pipeline_builder_add_step(self):
        """Test adding steps to pipeline builder"""
        builder = PipelineBuilder()

        # Add steps
        builder.add_step_by_type(SequenceValidationStep, "validation")
        builder.add_step_by_type(
            NumberingStep, "numbering", numbering_scheme=NumberingScheme.IMGT
        )

        step_names = builder.get_step_names()
        assert len(step_names) == 2
        assert "validation" in step_names
        assert "numbering" in step_names

    def test_pipeline_builder_configure(self):
        """Test configuring pipeline builder"""
        builder = PipelineBuilder()

        builder.configure("numbering_scheme", NumberingScheme.IMGT)
        builder.configure("validation_level", "strict")

        config = builder.get_config()
        assert config["numbering_scheme"] == NumberingScheme.IMGT
        assert config["validation_level"] == "strict"

    def test_pipeline_builder_build(self):
        """Test building a pipeline"""
        builder = PipelineBuilder()

        builder.add_step_by_type(SequenceValidationStep, "validation")
        builder.add_step_by_type(NumberingStep, "numbering")
        builder.configure("test_config", "test_value")

        pipeline = builder.build()
        assert pipeline is not None
        assert len(pipeline.steps) == 2
        assert pipeline.config["test_config"] == "test_value"

    def test_pipeline_builder_build_empty(self):
        """Test building pipeline with no steps should fail"""
        builder = PipelineBuilder()

        with pytest.raises(ProcessingError):
            builder.build()

    def test_pipeline_builder_remove_step(self):
        """Test removing steps from pipeline builder"""
        builder = PipelineBuilder()

        builder.add_step_by_type(SequenceValidationStep, "validation")
        builder.add_step_by_type(NumberingStep, "numbering")

        assert len(builder.get_step_names()) == 2

        builder.remove_step("validation")
        assert len(builder.get_step_names()) == 1
        assert "numbering" in builder.get_step_names()


class TestProcessingPipeline:
    """Test processing pipeline functionality"""

    def test_pipeline_creation(self):
        """Test creating a processing pipeline"""
        steps = [
            SequenceValidationStep("validation"),
            NumberingStep("numbering"),
        ]
        config = {"test": "value"}

        pipeline = ProcessingPipeline(steps, config)
        assert pipeline is not None
        assert len(pipeline.steps) == 2
        assert pipeline.config["test"] == "value"

    def test_pipeline_execution(self):
        """Test pipeline execution"""
        steps = [
            SequenceValidationStep("validation"),
            NumberingStep("numbering"),
        ]
        config = {}

        pipeline = ProcessingPipeline(steps, config)

        # Create test sequence
        sequence = self._create_test_sequence()
        context = ProcessingContext(sequence=sequence)

        result = pipeline.execute(context)
        assert result.success
        assert result.metadata["total_steps"] == 2
        assert result.metadata["completed_steps"] == 2

    def test_pipeline_execution_with_error(self):
        """Test pipeline execution with step error"""
        steps = [
            SequenceValidationStep("validation"),
            ErrorStep("error_step"),  # This step will cause an error
        ]
        config = {}

        pipeline = ProcessingPipeline(steps, config)

        sequence = self._create_test_sequence()
        context = ProcessingContext(sequence=sequence)

        result = pipeline.execute(context)
        assert not result.success
        assert "error_step" in result.error

    def test_pipeline_validation(self):
        """Test pipeline validation"""
        # Valid pipeline
        steps = [SequenceValidationStep("validation")]
        config = {}
        pipeline = ProcessingPipeline(steps, config)
        assert pipeline.validate()

        # Invalid pipeline - empty steps
        empty_pipeline = ProcessingPipeline([], config)
        assert not empty_pipeline.validate()

        # Invalid pipeline - duplicate step names
        duplicate_steps = [
            SequenceValidationStep("validation"),
            SequenceValidationStep("validation"),
        ]
        duplicate_pipeline = ProcessingPipeline(duplicate_steps, config)
        assert not duplicate_pipeline.validate()

    def test_pipeline_get_step_info(self):
        """Test getting pipeline step information"""
        steps = [
            SequenceValidationStep("validation"),
            NumberingStep("numbering"),
        ]
        config = {}

        pipeline = ProcessingPipeline(steps, config)
        step_info = pipeline.get_step_info()

        assert len(step_info) == 2
        assert step_info[0]["name"] == "validation"
        assert step_info[0]["index"] == 0
        assert step_info[1]["name"] == "numbering"
        assert step_info[1]["index"] == 1

    def _create_test_sequence(self) -> AntibodySequence:
        """Create a test antibody sequence"""
        sequence = AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY")
        domain = AntibodyDomain(
            domain_type=DomainType.VARIABLE,
            sequence=sequence,
            numbering_scheme=NumberingScheme.IMGT,
        )
        chain = AntibodyChain(
            name="TestChain", chain_type=ChainType.HEAVY, sequence=sequence
        )
        chain.add_domain(domain)

        antibody_sequence = AntibodySequence(name="TestAntibody")
        antibody_sequence.add_chain(chain)

        return antibody_sequence


class TestPredefinedPipelines:
    """Test predefined pipeline creation functions"""

    def test_create_annotation_pipeline(self):
        """Test creating annotation pipeline"""
        pipeline = create_annotation_pipeline(NumberingScheme.IMGT)

        assert pipeline is not None
        assert len(pipeline.steps) == 5
        assert pipeline.config["numbering_scheme"] == NumberingScheme.IMGT
        assert pipeline.config["validation_level"] == "strict"

    def test_create_alignment_pipeline(self):
        """Test creating alignment pipeline"""
        pipeline = create_alignment_pipeline()

        assert pipeline is not None
        assert len(pipeline.steps) == 4
        assert pipeline.config["parallel_processing"] is True

    def test_create_custom_pipeline(self):
        """Test creating custom pipeline"""
        steps = ["sequence_validation", "numbering"]
        config = {"custom_config": "value"}

        pipeline = create_custom_pipeline(steps, config)

        assert pipeline is not None
        assert len(pipeline.steps) == 2
        assert pipeline.config["custom_config"] == "value"

    def test_create_custom_pipeline_invalid_step(self):
        """Test creating custom pipeline with invalid step"""
        steps = ["invalid_step"]

        with pytest.raises(ProcessingError):
            create_custom_pipeline(steps)


class TestProcessingService:
    """Test processing service functionality"""

    def test_processing_service_creation(self):
        """Test creating processing service"""
        service = ProcessingService()
        assert service is not None

        # Check available types
        pipeline_types = service.get_available_pipeline_types()
        processing_types = service.get_available_processing_types()

        assert "annotation" in pipeline_types
        assert "alignment" in pipeline_types
        assert "annotation" in processing_types
        assert "alignment" in processing_types

    def test_processing_service_process_sequence(self):
        """Test processing a single sequence"""
        service = ProcessingService()
        sequence = self._create_test_sequence()

        result = service.process_sequence(sequence, "annotation")

        assert result.success
        assert result.metadata["processing_type"] == "annotation"
        assert result.metadata["sequence_name"] == sequence.name

    def test_processing_service_process_sequence_invalid_type(self):
        """Test processing with invalid processing type"""
        service = ProcessingService()
        sequence = self._create_test_sequence()

        with pytest.raises(ProcessingError):
            service.process_sequence(sequence, "invalid_type")

    def test_processing_service_batch_processing(self):
        """Test batch processing of sequences"""
        service = ProcessingService()
        sequences = [
            self._create_test_sequence(),
            self._create_test_sequence(),
        ]

        result = service.process_sequences_batch(sequences, "annotation")

        assert result.success
        assert result.data["total_sequences"] == 2
        assert result.data["successful_count"] == 2
        assert result.data["success_rate"] == 1.0

    def test_processing_service_create_pipeline(self):
        """Test creating pipeline through service"""
        service = ProcessingService()

        pipeline = service.create_pipeline(
            "annotation", numbering_scheme=NumberingScheme.IMGT
        )

        assert pipeline is not None
        assert len(pipeline.steps) == 5

    def test_processing_service_register_pipeline_type(self):
        """Test registering new pipeline type"""
        service = ProcessingService()

        def custom_pipeline_creator(**kwargs):
            return create_custom_pipeline(["sequence_validation"], kwargs)

        service.register_pipeline_type("custom_type", custom_pipeline_creator)

        pipeline_types = service.get_available_pipeline_types()
        assert "custom_type" in pipeline_types

    def _create_test_sequence(self) -> AntibodySequence:
        """Create a test antibody sequence"""
        sequence = AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY")
        domain = AntibodyDomain(
            domain_type=DomainType.VARIABLE,
            sequence=sequence,
            numbering_scheme=NumberingScheme.IMGT,
        )
        chain = AntibodyChain(
            name="TestChain", chain_type=ChainType.HEAVY, sequence=sequence
        )
        chain.add_domain(domain)

        antibody_sequence = AntibodySequence(name="TestAntibody")
        antibody_sequence.add_chain(chain)

        return antibody_sequence


class TestProgressTrackingObserver:
    """Test progress tracking observer functionality"""

    def test_observer_creation(self):
        """Test creating progress tracking observer"""
        observer = ProgressTrackingObserver()
        assert observer is not None
        assert len(observer.progress_history) == 0
        assert len(observer.errors) == 0
        assert not observer.completed

    def test_observer_step_completed(self):
        """Test observer step completion tracking"""
        observer = ProgressTrackingObserver()

        observer.on_step_completed("test_step", 0.5)

        assert len(observer.progress_history) == 1
        assert observer.progress_history[0]["step"] == "test_step"
        assert observer.progress_history[0]["progress"] == 0.5

    def test_observer_error_tracking(self):
        """Test observer error tracking"""
        observer = ProgressTrackingObserver()

        observer.on_error("test error")

        assert len(observer.errors) == 1
        assert observer.errors[0]["error"] == "test error"

    def test_observer_processing_complete(self):
        """Test observer processing completion"""
        observer = ProgressTrackingObserver()

        result = ProcessingResult(success=True, data={"test": "data"})
        observer.on_processing_complete(result)

        assert observer.completed
        assert observer.final_result == result

    def test_observer_progress_summary(self):
        """Test observer progress summary"""
        observer = ProgressTrackingObserver()

        observer.on_step_completed("step1", 0.3)
        observer.on_step_completed("step2", 0.7)
        observer.on_error("test error")

        summary = observer.get_progress_summary()

        assert summary["completed"] is False
        assert summary["total_steps"] == 2
        assert summary["current_progress"] == 0.7
        assert summary["error_count"] == 1
        assert summary["has_errors"] is True

    def test_observer_latest_progress(self):
        """Test observer latest progress retrieval"""
        observer = ProgressTrackingObserver()

        assert observer.get_latest_progress() == 0.0

        observer.on_step_completed("step1", 0.5)
        assert observer.get_latest_progress() == 0.5

        observer.on_step_completed("step2", 0.8)
        assert observer.get_latest_progress() == 0.8


class TestProcessingServiceFactory:
    """Test processing service factory functionality"""

    def test_create_standard_service(self):
        """Test creating standard service"""
        service = ProcessingServiceFactory.create_standard_service()
        assert service is not None
        assert isinstance(service, ProcessingService)

    def test_create_service_with_observers(self):
        """Test creating service with observers"""
        observer = ProgressTrackingObserver()
        service = ProcessingServiceFactory.create_service_with_observers(
            [observer]
        )

        assert service is not None
        # Note: We can't easily test observer attachment without exposing internal state

    def test_create_service_with_custom_pipelines(self):
        """Test creating service with custom pipelines"""

        def custom_pipeline(**kwargs):
            return create_custom_pipeline(["sequence_validation"], kwargs)

        custom_pipelines = {"custom": custom_pipeline}
        service = (
            ProcessingServiceFactory.create_service_with_custom_pipelines(
                custom_pipelines
            )
        )

        assert service is not None
        pipeline_types = service.get_available_pipeline_types()
        assert "custom" in pipeline_types


# =============================================================================
# PLACEHOLDER STEP CLASSES FOR TESTING
# =============================================================================


class SequenceValidationStep:
    """Placeholder sequence validation step for testing"""

    def __init__(self, name: str):
        self.name = name

    def execute(self, context: ProcessingContext) -> ProcessingContext:
        return context

    def can_execute(self, context: ProcessingContext) -> bool:
        return True


class NumberingStep:
    """Placeholder numbering step for testing"""

    def __init__(
        self,
        name: str,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ):
        self.name = name
        self.numbering_scheme = numbering_scheme

    def execute(self, context: ProcessingContext) -> ProcessingContext:
        return context

    def can_execute(self, context: ProcessingContext) -> bool:
        return True


class ErrorStep:
    """Step that always causes an error for testing"""

    def __init__(self, name: str):
        self.name = name

    def execute(self, context: ProcessingContext) -> ProcessingContext:
        context.errors.append(f"Error in step {self.name}")
        return context

    def can_execute(self, context: ProcessingContext) -> bool:
        return True


if __name__ == "__main__":
    pytest.main([__file__])

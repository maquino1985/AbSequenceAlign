"""
Abstract base classes providing common functionality and enforcing contracts.
These classes implement the Template Method pattern and provide shared behavior.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generic, TypeVar, Optional
from dataclasses import dataclass, field
import logging

from .interfaces import (
    ProcessingObserver,
    ProcessingSubject,
    ProcessingContext,
    ProcessingResult,
    ProcessingStatus,
    ExternalToolAdapter,
)

# Type variables
T = TypeVar("T")
U = TypeVar("U")

# =============================================================================
# ABSTRACT PROCESSING CLASSES
# =============================================================================


class AbstractProcessingSubject(ProcessingSubject):
    """Abstract implementation of ProcessingSubject with common functionality"""

    def __init__(self):
        self._observers: List[ProcessingObserver] = []
        self._logger = logging.getLogger(self.__class__.__name__)

    def attach(self, observer: ProcessingObserver) -> None:
        """Attach an observer to this subject"""
        if observer not in self._observers:
            self._observers.append(observer)
            self._logger.debug(
                f"Attached observer: {observer.__class__.__name__}"
            )

    def detach(self, observer: ProcessingObserver) -> None:
        """Detach an observer from this subject"""
        if observer in self._observers:
            self._observers.remove(observer)
            self._logger.debug(
                f"Detached observer: {observer.__class__.__name__}"
            )

    def notify_step_completed(self, step: str, progress: float) -> None:
        """Notify all observers of step completion"""
        for observer in self._observers:
            observer.on_step_completed(step, progress)

    def notify_processing_completed(self, result: ProcessingResult) -> None:
        """Notify all observers of processing completion"""
        for observer in self._observers:
            observer.on_processing_completed(result)

    def notify_processing_failed(self, error: str) -> None:
        """Notify all observers of processing failure"""
        for observer in self._observers:
            observer.on_processing_failed(error)


class AbstractProcessor(ABC, Generic[T]):
    """Abstract base class for processors with common functionality"""

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._processing_status = ProcessingStatus.PENDING

    @property
    def status(self) -> ProcessingStatus:
        """Get the current processing status"""
        return self._processing_status

    def _set_status(self, status: ProcessingStatus) -> None:
        """Set the processing status"""
        self._processing_status = status
        self._logger.debug(f"Status changed to: {status}")

    def _validate_input(self, input_data: T) -> bool:
        """Validate input data - can be overridden by subclasses"""
        return input_data is not None

    def _pre_process(self, input_data: T) -> T:
        """Pre-processing hook - can be overridden by subclasses"""
        return input_data

    def _post_process(self, result: Any) -> Any:
        """Post-processing hook - can be overridden by subclasses"""
        return result

    def _handle_error(self, error: Exception) -> ProcessingResult:
        """Handle processing errors"""
        self._set_status(ProcessingStatus.FAILED)
        error_msg = f"Processing failed: {str(error)}"
        self._logger.error(error_msg)
        return ProcessingResult(success=False, error=error_msg)

    def process(self, input_data: T) -> ProcessingResult:
        """Template method for processing with error handling"""
        try:
            self._set_status(ProcessingStatus.RUNNING)

            # Validate input
            if not self._validate_input(input_data):
                raise ValueError("Invalid input data")

            # Pre-process
            processed_input = self._pre_process(input_data)

            # Process (implemented by subclasses)
            result = self._process(processed_input)

            # Post-process
            final_result = self._post_process(result)

            self._set_status(ProcessingStatus.COMPLETED)
            return ProcessingResult(success=True, data=final_result)

        except Exception as e:
            return self._handle_error(e)

    @abstractmethod
    def _process(self, input_data: T) -> Any:
        """Process the input data - must be implemented by subclasses"""
        pass


# =============================================================================
# TEMPLATE METHOD PATTERN CLASSES
# =============================================================================


class AbstractAnnotationProcessor(AbstractProcessor):
    """Template method for annotation processing"""

    def process_sequence(self, sequence):
        """Template method defining the annotation processing flow"""
        try:
            self._set_status(ProcessingStatus.RUNNING)

            # Template method steps
            validated_sequence = self._validate_sequence(sequence)
            numbered_sequence = self._number_sequence(validated_sequence)
            annotated_sequence = self._annotate_regions(numbered_sequence)
            domain = self._create_domain(annotated_sequence)

            self._set_status(ProcessingStatus.COMPLETED)
            return domain

        except Exception as e:
            return self._handle_error(e)

    @abstractmethod
    def _validate_sequence(self, sequence):
        """Validate the input sequence"""
        pass

    @abstractmethod
    def _number_sequence(self, sequence):
        """Number the sequence according to the appropriate scheme"""
        pass

    @abstractmethod
    def _annotate_regions(self, sequence):
        """Annotate functional regions in the sequence"""
        pass

    @abstractmethod
    def _create_domain(self, sequence):
        """Create a domain object from the processed sequence"""
        pass


class AbstractAlignmentProcessor(AbstractProcessor):
    """Template method for alignment processing"""

    def align_sequences(self, sequences: List):
        """Template method defining the alignment processing flow"""
        try:
            self._set_status(ProcessingStatus.RUNNING)

            # Template method steps
            validated_sequences = self._validate_sequences(sequences)
            prepared_sequences = self._prepare_sequences(validated_sequences)
            alignment_result = self._perform_alignment(prepared_sequences)
            processed_result = self._process_alignment_result(alignment_result)

            self._set_status(ProcessingStatus.COMPLETED)
            return processed_result

        except Exception as e:
            return self._handle_error(e)

    @abstractmethod
    def _validate_sequences(self, sequences: List) -> List:
        """Validate the input sequences"""
        pass

    @abstractmethod
    def _prepare_sequences(self, sequences: List) -> List:
        """Prepare sequences for alignment"""
        pass

    @abstractmethod
    def _perform_alignment(self, sequences: List) -> Dict[str, Any]:
        """Perform the actual alignment"""
        pass

    @abstractmethod
    def _process_alignment_result(self, result: Dict[str, Any]):
        """Process and format the alignment result"""
        pass


# =============================================================================
# BIOLOGIC PROCESSING ABSTRACT CLASSES
# =============================================================================


class AbstractBiologicProcessor(AbstractProcessor[T]):
    """Template method for biologic processing"""

    async def process_biologic(self, biologic_data: T) -> ProcessingResult:
        """Template method defining biologic processing flow"""
        try:
            self._set_status(ProcessingStatus.RUNNING)

            # Template method steps
            validated_data = self._validate_biologic_data(biologic_data)
            processed_biologic = self._process_biologic_entity(validated_data)
            persisted_biologic = await self._persist_biologic(
                processed_biologic
            )

            self._set_status(ProcessingStatus.COMPLETED)
            return ProcessingResult(success=True, data=persisted_biologic)

        except Exception as e:
            return self._handle_error(e)

    @abstractmethod
    def _validate_biologic_data(self, data: T) -> T:
        """Validate the biologic data"""
        pass

    @abstractmethod
    def _process_biologic_entity(self, data: T) -> Any:
        """Process the biologic entity"""
        pass

    @abstractmethod
    async def _persist_biologic(self, biologic: Any) -> Any:
        """Persist the biologic entity"""
        pass

    def _process(self, input_data: T) -> Any:
        """Process implementation for AbstractProcessor"""
        return self.process_biologic(input_data)


class AbstractBiologicConverter(ABC, Generic[T, U]):
    """Abstract converter for biologic entities"""

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def convert_to_orm(self, domain_entity: T) -> U:
        """Convert domain entity to ORM model"""
        pass

    @abstractmethod
    def convert_to_domain(self, orm_model: U) -> T:
        """Convert ORM model to domain entity"""
        pass

    def convert_list_to_orm(self, domain_entities: List[T]) -> List[U]:
        """Convert a list of domain entities to ORM models"""
        return [self.convert_to_orm(entity) for entity in domain_entities]

    def convert_list_to_domain(self, orm_models: List[U]) -> List[T]:
        """Convert a list of ORM models to domain entities"""
        return [self.convert_to_domain(model) for model in orm_models]


# =============================================================================
# BUILDER PATTERN BASE CLASSES
# =============================================================================


class AbstractBuilder(ABC, Generic[T]):
    """Abstract base class for builders"""

    def __init__(self):
        self.reset()

    @abstractmethod
    def reset(self) -> None:
        """Reset the builder state"""
        pass

    @abstractmethod
    def build(self) -> T:
        """Build and return the final object"""
        pass


# =============================================================================
# FACTORY PATTERN BASE CLASSES
# =============================================================================


class AbstractFactory(ABC, Generic[T]):
    """Abstract base class for factories"""

    def __init__(self):
        self._registry: Dict[str, type] = {}
        self._logger = logging.getLogger(self.__class__.__name__)

    def register(self, key: str, cls: type) -> None:
        """Register a class with a key"""
        self._registry[key] = cls
        self._logger.debug(f"Registered {cls.__name__} with key '{key}'")

    def create(self, key: str, **kwargs) -> T:
        """Create an instance using the registered class"""
        if key not in self._registry:
            raise ValueError(f"No class registered for key '{key}'")

        cls = self._registry[key]
        try:
            instance = cls(**kwargs)
            self._logger.debug(f"Created instance of {cls.__name__}")
            return instance
        except Exception as e:
            self._logger.error(
                f"Failed to create instance of {cls.__name__}: {e}"
            )
            raise

    def get_available_types(self) -> List[str]:
        """Get list of available registered types"""
        return list(self._registry.keys())


class AbstractServiceFactory(AbstractFactory[T]):
    """Abstract factory for creating services"""

    def __init__(self):
        super().__init__()
        self._register_default_services()

    @abstractmethod
    def _register_default_services(self) -> None:
        """Register default service types - must be implemented by subclasses"""
        pass


# =============================================================================
# PIPELINE PATTERN BASE CLASSES
# =============================================================================


@dataclass
class PipelineContext:
    """Context for pipeline execution"""

    input_data: Any = None
    current_step: str = ""
    step_results: Dict[str, Any] = field(default_factory=dict)
    step_errors: Dict[str, str] = field(default_factory=dict)
    completed_steps: int = 0
    total_steps: int = 0
    errors: List[str] = field(default_factory=list)


class AbstractPipelineStep(ABC):
    """Abstract base class for pipeline steps"""

    def __init__(self, name: str):
        self.name = name
        self._logger = logging.getLogger(f"PipelineStep.{name}")

    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute this pipeline step"""
        try:
            self._logger.debug(f"Executing step: {self.name}")
            context.current_step = self.name

            # Execute the step
            result = self._execute_step(context)

            # Update context
            context.step_results[self.name] = result
            context.completed_steps += 1

            self._logger.debug(f"Completed step: {self.name}")
            return context

        except Exception as e:
            error_msg = f"Step '{self.name}' failed: {str(e)}"
            self._logger.error(error_msg)
            context.step_errors[self.name] = error_msg
            context.errors.append(error_msg)
            return context

    @abstractmethod
    def _execute_step(self, context: PipelineContext) -> Any:
        """Execute the actual step logic - must be implemented by subclasses"""
        pass

    def can_execute(self, context: PipelineContext) -> bool:
        """Check if this step can execute given the current context"""
        return True


# =============================================================================
# ADAPTER PATTERN BASE CLASSES
# =============================================================================


class AbstractBiologicAdapter(ABC):
    """Abstract adapter for biologic data sources"""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self._logger = logging.getLogger(
            f"{self.__class__.__name__}.{source_name}"
        )

    @abstractmethod
    async def fetch_biologic_data(self, identifier: str) -> Dict[str, Any]:
        """Fetch biologic data from the source"""
        pass

    @abstractmethod
    async def validate_biologic_data(self, data: Dict[str, Any]) -> bool:
        """Validate biologic data from the source"""
        pass

    @abstractmethod
    async def transform_biologic_data(
        self, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform biologic data to internal format"""
        pass

    async def process_biologic_data(self, identifier: str) -> Dict[str, Any]:
        """Process biologic data through the adapter pipeline"""
        try:
            # Fetch data
            raw_data = await self.fetch_biologic_data(identifier)

            # Validate data
            if not await self.validate_biologic_data(raw_data):
                raise ValueError(
                    f"Invalid biologic data from {self.source_name}"
                )

            # Transform data
            transformed_data = await self.transform_biologic_data(raw_data)

            return transformed_data

        except Exception as e:
            self._logger.error(f"Error processing biologic data: {e}")
            raise

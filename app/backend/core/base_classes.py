"""
Abstract base classes providing common functionality and enforcing contracts.
These classes implement the Template Method pattern and provide shared behavior.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generic, TypeVar
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

    def notify_step_completed(self, step_name: str, progress: float) -> None:
        """Notify all observers of a step completion"""
        self._logger.debug(f"Step completed: {step_name} ({progress:.1%})")
        for observer in self._observers:
            try:
                observer.on_step_completed(step_name, progress)
            except Exception as e:
                self._logger.error(f"Error notifying observer {observer}: {e}")

    def notify_error(self, error: str) -> None:
        """Notify all observers of an error"""
        self._logger.error(f"Processing error: {error}")
        for observer in self._observers:
            try:
                observer.on_error(error)
            except Exception as e:
                self._logger.error(f"Error notifying observer {observer}: {e}")


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


class AbstractExternalToolAdapter(ExternalToolAdapter):
    """Abstract base class for external tool adapters"""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self._logger = logging.getLogger(
            f"{self.__class__.__name__}.{tool_name}"
        )
        self._available = None  # Cache for availability check

    def is_available(self) -> bool:
        """Check if the external tool is available on the system"""
        if self._available is None:
            self._available = self._check_availability()
        return self._available

    @abstractmethod
    def _check_availability(self) -> bool:
        """Check if the tool is available - must be implemented by subclasses"""
        pass

    def _validate_input(self, input_data: str) -> bool:
        """Validate input data"""
        if not input_data or not input_data.strip():
            self._logger.error("Empty or invalid input data")
            return False
        return True

    def _create_result(
        self, success: bool, data: Dict[str, Any] = None, error: str = None
    ) -> Dict[str, Any]:
        """Create a standardized result dictionary"""
        return {
            "success": success,
            "data": data or {},
            "error": error,
            "tool": self.tool_name,
        }


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


# =============================================================================
# PIPELINE BASE CLASSES
# =============================================================================


@dataclass
class PipelineContext(ProcessingContext):
    """Extended context for pipeline processing"""

    step_results: Dict[str, Any] = field(default_factory=dict)
    step_errors: Dict[str, str] = field(default_factory=dict)
    current_step: str = ""
    total_steps: int = 0
    completed_steps: int = 0


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
# UTILITY BASE CLASSES
# =============================================================================


class Validatable(ABC):
    """Base class for objects that can validate themselves"""

    @abstractmethod
    def validate(self) -> bool:
        """Validate this object"""
        pass

    @abstractmethod
    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors"""
        pass


class Configurable(ABC):
    """Base class for objects that can be configured"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self.config[key] = value

    def has_config(self, key: str) -> bool:
        """Check if a configuration key exists"""
        return key in self.config

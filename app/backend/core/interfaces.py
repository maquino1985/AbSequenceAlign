"""
Core interfaces and protocols for the antibody sequence analysis system.
Defines the contracts that all components must follow.
"""

from abc import ABC, abstractmethod
from typing import Protocol, Generic, TypeVar, Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Type variables for generic components
T = TypeVar("T")
InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")

# =============================================================================
# CORE DOMAIN INTERFACES
# =============================================================================


class Sequence(Protocol):
    """Core sequence interface - represents any biological sequence"""

    @property
    def sequence(self) -> str:
        """The raw sequence string"""
        ...

    @property
    def name(self) -> str:
        """The sequence identifier/name"""
        ...

    @property
    def type(self) -> str:
        """The type of sequence (e.g., 'antibody', 'protein', 'dna')"""
        ...


class Domain(Protocol):
    """Core domain interface - represents a functional domain within a sequence"""

    @property
    def sequence(self) -> str:
        """The domain sequence"""
        ...

    @property
    def type(self) -> str:
        """The domain type (e.g., 'V', 'C', 'LINKER')"""
        ...

    @property
    def regions(self) -> Dict[str, Any]:
        """The annotated regions within this domain"""
        ...


class Region(Protocol):
    """Core region interface - represents a functional region within a domain"""

    @property
    def name(self) -> str:
        """The region name (e.g., 'CDR1', 'FR1')"""
        ...

    @property
    def start(self) -> int:
        """The start position in the sequence"""
        ...

    @property
    def stop(self) -> int:
        """The stop position in the sequence"""
        ...

    @property
    def sequence(self) -> str:
        """The region sequence"""
        ...


# =============================================================================
# PROCESSING INTERFACES
# =============================================================================


class Processor(Generic[InputT, OutputT], ABC):
    """Generic processor interface for transforming input to output"""

    @abstractmethod
    def process(self, input_data: InputT) -> OutputT:
        """Process the input data and return the result"""
        pass


class ProcessingStrategy(ABC):
    """Strategy interface for different processing approaches"""

    @abstractmethod
    def execute(self, sequence: Sequence) -> Domain:
        """Execute the processing strategy on a sequence"""
        pass

    @abstractmethod
    def can_process(self, sequence: Sequence) -> bool:
        """Check if this strategy can process the given sequence"""
        pass


class PipelineStep(ABC):
    """Base class for pipeline steps in the Chain of Responsibility pattern"""

    def __init__(self, next_step: Optional["PipelineStep"] = None):
        self.next_step = next_step

    @abstractmethod
    def process(self, context: "ProcessingContext") -> "ProcessingContext":
        """Process the context and optionally pass to next step"""
        pass

    def set_next(self, step: "PipelineStep") -> "PipelineStep":
        """Set the next step in the chain"""
        self.next_step = step
        return step

    def _process_next(self, context: "ProcessingContext") -> "ProcessingContext":
        """Helper method to process the next step if it exists"""
        if self.next_step:
            return self.next_step.process(context)
        return context


# =============================================================================
# EXTERNAL TOOL INTERFACES
# =============================================================================


class ExternalToolAdapter(ABC):
    """Adapter interface for external bioinformatics tools"""

    @abstractmethod
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute the external tool with the given input"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the external tool is available on the system"""
        pass


class AbstractExternalToolAdapter(ABC):
    """Abstract base class for external tool adapters"""

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the external tool"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the external tool is available"""
        pass

    @abstractmethod
    def get_version(self) -> Optional[str]:
        """Get the version of the external tool"""
        pass


class ToolResult(Protocol):
    """Protocol for tool execution results"""

    @property
    def success(self) -> bool:
        """Whether the tool execution was successful"""
        ...

    @property
    def data(self) -> Dict[str, Any]:
        """The result data from the tool"""
        ...

    @property
    def error(self) -> Optional[str]:
        """Error message if execution failed"""
        ...


# =============================================================================
# OBSERVER PATTERN INTERFACES
# =============================================================================


class ProcessingObserver(ABC):
    """Observer interface for processing events"""

    @abstractmethod
    def on_step_completed(self, step_name: str, progress: float) -> None:
        """Called when a processing step is completed"""
        pass

    @abstractmethod
    def on_error(self, error: str) -> None:
        """Called when an error occurs during processing"""
        pass

    @abstractmethod
    def on_processing_complete(self, result: Any) -> None:
        """Called when processing is completely finished"""
        pass


class ProcessingSubject(ABC):
    """Subject interface for the Observer pattern"""

    @abstractmethod
    def attach(self, observer: ProcessingObserver) -> None:
        """Attach an observer to this subject"""
        pass

    @abstractmethod
    def detach(self, observer: ProcessingObserver) -> None:
        """Detach an observer from this subject"""
        pass

    @abstractmethod
    def notify_step_completed(self, step_name: str, progress: float) -> None:
        """Notify all observers of a step completion"""
        pass

    @abstractmethod
    def notify_error(self, error: str) -> None:
        """Notify all observers of an error"""
        pass


# =============================================================================
# REPOSITORY INTERFACES
# =============================================================================


class Repository(Generic[T], ABC):
    """Generic repository interface for data access"""

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save an entity"""
        pass

    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find an entity by its ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[T]:
        """Find all entities"""
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity by its ID"""
        pass


# =============================================================================
# FACTORY INTERFACES
# =============================================================================


class Factory(Generic[T], ABC):
    """Generic factory interface"""

    @abstractmethod
    def create(self, **kwargs) -> T:
        """Create a new instance of T"""
        pass


# =============================================================================
# ENUMERATIONS
# =============================================================================


class ProcessingStatus(str, Enum):
    """Status of processing operations"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DomainType(str, Enum):
    """Types of antibody domains"""

    VARIABLE = "V"
    CONSTANT = "C"
    LINKER = "LINKER"


class RegionType(str, Enum):
    """Types of antibody regions"""

    CDR1 = "CDR1"
    CDR2 = "CDR2"
    CDR3 = "CDR3"
    FR1 = "FR1"
    FR2 = "FR2"
    FR3 = "FR3"
    FR4 = "FR4"
    CONSTANT = "CONSTANT"
    LINKER = "LINKER"


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class ProcessingContext:
    """Context object passed through processing pipelines"""

    sequence: Sequence
    domains: List[Domain] = None
    annotations: Dict[str, Any] = None
    errors: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.domains is None:
            self.domains = []
        if self.annotations is None:
            self.annotations = {}
        if self.errors is None:
            self.errors = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ProcessingResult:
    """Result of a processing operation"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

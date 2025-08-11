"""
Core interfaces defining contracts for the application.
These interfaces establish the contracts that implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Generic, TypeVar, Protocol
from dataclasses import dataclass
from datetime import datetime
import logging

# Type variables
T = TypeVar("T")
U = TypeVar("U")

# =============================================================================
# PROCESSING INTERFACES
# =============================================================================


class ProcessingObserver(ABC):
    """Observer interface for processing events"""

    @abstractmethod
    def on_step_completed(self, step: str, progress: float) -> None:
        """Called when a processing step is completed"""
        pass

    @abstractmethod
    def on_processing_completed(self, result: "ProcessingResult") -> None:
        """Called when processing is completed"""
        pass

    @abstractmethod
    def on_processing_failed(self, error: str) -> None:
        """Called when processing fails"""
        pass


class ProcessingSubject(ABC):
    """Subject interface for the Observer pattern"""

    @abstractmethod
    def attach(self, observer: ProcessingObserver) -> None:
        """Attach an observer"""
        pass

    @abstractmethod
    def detach(self, observer: ProcessingObserver) -> None:
        """Detach an observer"""
        pass

    @abstractmethod
    def notify_step_completed(self, step: str, progress: float) -> None:
        """Notify observers of step completion"""
        pass

    @abstractmethod
    def notify_processing_completed(self, result: "ProcessingResult") -> None:
        """Notify observers of processing completion"""
        pass

    @abstractmethod
    def notify_processing_failed(self, error: str) -> None:
        """Notify observers of processing failure"""
        pass


@dataclass
class ProcessingResult:
    """Result of a processing operation"""

    success: bool
    data: Any = None
    error: str = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class ProcessingStatus:
    """Processing status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingContext(ABC):
    """Context for processing operations"""

    @abstractmethod
    def get_input_data(self) -> Any:
        """Get the input data for processing"""
        pass

    @abstractmethod
    def set_result(self, result: ProcessingResult) -> None:
        """Set the processing result"""
        pass

    @abstractmethod
    def get_result(self) -> Optional[ProcessingResult]:
        """Get the processing result"""
        pass


class AbstractExternalToolAdapter(ABC):
    """Abstract base class for external tool adapters"""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the external tool is available"""
        pass

    @abstractmethod
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute the external tool with input data"""
        pass

    @abstractmethod
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the tool output"""
        pass

    def _validate_input(self, input_data: str) -> bool:
        """Validate input data"""
        return input_data is not None and len(input_data.strip()) > 0

    def _create_result(
        self, success: bool, data: Any = None, error: str = None
    ) -> Dict[str, Any]:
        """Create a standardized result dictionary"""
        return {
            "success": success,
            "data": data,
            "error": error,
            "tool_name": self.tool_name,
        }


class ExternalToolAdapter(AbstractExternalToolAdapter):
    """Interface for external tool adapters"""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the external tool is available"""
        pass

    @abstractmethod
    def execute(self, input_data: str) -> Dict[str, Any]:
        """Execute the external tool with input data"""
        pass

    @abstractmethod
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the tool output"""
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

    @abstractmethod
    def count(self) -> int:
        """Count total entities"""
        pass


class AsyncRepository(Generic[T], ABC):
    """Generic async repository interface for data access"""

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save an entity"""
        pass

    @abstractmethod
    async def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find an entity by its ID"""
        pass

    @abstractmethod
    async def find_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[T]:
        """Find all entities with optional pagination"""
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity by its ID"""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Count total entities"""
        pass

    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """Check if an entity exists"""
        pass


# =============================================================================
# BIOLOGIC INTERFACES
# =============================================================================


class BiologicRepository(AsyncRepository[T], ABC):
    """Repository interface for biologic entities"""

    @abstractmethod
    async def find_by_organism(
        self, organism: str, limit: Optional[int] = None
    ) -> List[T]:
        """Find biologics by organism"""
        pass

    @abstractmethod
    async def find_by_type(
        self, biologic_type: str, limit: Optional[int] = None
    ) -> List[T]:
        """Find biologics by type"""
        pass

    @abstractmethod
    async def find_by_name_pattern(
        self, name_pattern: str, limit: Optional[int] = None
    ) -> List[T]:
        """Find biologics by name pattern"""
        pass

    @abstractmethod
    async def find_with_chains(self, entity_id: str) -> Optional[T]:
        """Find biologic with all its chains loaded"""
        pass

    @abstractmethod
    async def find_with_full_hierarchy(self, entity_id: str) -> Optional[T]:
        """Find biologic with full hierarchy (chains, sequences, domains, features)"""
        pass


class BiologicService(ProcessingSubject, ABC):
    """Service interface for biologic entity management"""

    @abstractmethod
    async def create_biologic(
        self, biologic_data: "BiologicCreate"
    ) -> "BiologicResponse":
        """Create a new biologic entity"""
        pass

    @abstractmethod
    async def get_biologic(self, biologic_id: str) -> "BiologicResponse":
        """Get a biologic entity by ID"""
        pass

    @abstractmethod
    async def list_biologics(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List["BiologicResponse"]:
        """List all biologic entities"""
        pass

    @abstractmethod
    async def update_biologic(
        self, biologic_id: str, update_data: "BiologicUpdate"
    ) -> "BiologicResponse":
        """Update a biologic entity"""
        pass

    @abstractmethod
    async def delete_biologic(self, biologic_id: str) -> bool:
        """Delete a biologic entity"""
        pass

    @abstractmethod
    async def process_and_persist_biologic(
        self, biologic_data: "BiologicCreate"
    ) -> "ProcessingResult":
        """Process and persist a biologic entity"""
        pass

    @abstractmethod
    async def search_biologics(
        self, search_criteria: Dict[str, Any]
    ) -> List["BiologicResponse"]:
        """Search biologics by criteria"""
        pass


class BiologicProcessor(ABC):
    """Processor interface for biologic entities"""

    @abstractmethod
    def validate_biologic_data(self, data: "BiologicCreate") -> bool:
        """Validate biologic data"""
        pass

    @abstractmethod
    def process_biologic_entity(
        self, data: "BiologicCreate"
    ) -> "BiologicResponse":
        """Process biologic entity"""
        pass

    @abstractmethod
    def convert_domain_to_orm(self, domain_entity: T) -> U:
        """Convert domain entity to ORM model"""
        pass

    @abstractmethod
    def convert_orm_to_domain(self, orm_model: U) -> T:
        """Convert ORM model to domain entity"""
        pass


class BiologicConverter(Generic[T, U], ABC):
    """Converter interface for biologic entities"""

    @abstractmethod
    def convert_to_orm(self, domain_entity: T) -> U:
        """Convert domain entity to ORM model"""
        pass

    @abstractmethod
    def convert_to_domain(self, orm_model: U) -> T:
        """Convert ORM model to domain entity"""
        pass

    @abstractmethod
    def convert_to_pydantic(self, domain_entity: T) -> "BiologicResponse":
        """Convert domain entity to Pydantic response model"""
        pass

    @abstractmethod
    def convert_from_pydantic(self, pydantic_model: "BiologicCreate") -> T:
        """Convert Pydantic model to domain entity"""
        pass


# =============================================================================
# STRATEGY INTERFACES
# =============================================================================


class BiologicProcessingStrategy(ABC):
    """Strategy interface for processing different biologic types"""

    @abstractmethod
    def can_process(self, biologic_type: str) -> bool:
        """Check if this strategy can process the given biologic type"""
        pass

    @abstractmethod
    def process(self, biologic_data: "BiologicCreate") -> "BiologicResponse":
        """Process biologic data according to this strategy"""
        pass

    @abstractmethod
    def validate(self, biologic_data: "BiologicCreate") -> bool:
        """Validate biologic data according to this strategy"""
        pass


class BiologicValidationStrategy(ABC):
    """Strategy interface for validating different biologic types"""

    @abstractmethod
    def can_validate(self, biologic_type: str) -> bool:
        """Check if this strategy can validate the given biologic type"""
        pass

    @abstractmethod
    def validate(self, biologic_data: "BiologicCreate") -> List[str]:
        """Validate biologic data and return list of errors"""
        pass


# =============================================================================
# ADAPTER INTERFACES
# =============================================================================


class BiologicDataAdapter(ABC):
    """Adapter interface for biologic data sources"""

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
    ) -> "BiologicCreate":
        """Transform biologic data to internal format"""
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this data source"""
        pass


# =============================================================================
# FACTORY INTERFACES
# =============================================================================


class BiologicServiceFactory(ABC):
    """Factory interface for creating biologic services"""

    @abstractmethod
    def create_service(self, service_type: str, **kwargs) -> BiologicService:
        """Create a biologic service of the specified type"""
        pass

    @abstractmethod
    def create_processor(
        self, processor_type: str, **kwargs
    ) -> BiologicProcessor:
        """Create a biologic processor of the specified type"""
        pass

    @abstractmethod
    def create_converter(
        self, converter_type: str, **kwargs
    ) -> BiologicConverter:
        """Create a biologic converter of the specified type"""
        pass

    @abstractmethod
    def create_strategy(
        self, strategy_type: str, **kwargs
    ) -> BiologicProcessingStrategy:
        """Create a biologic processing strategy of the specified type"""
        pass

    @abstractmethod
    def get_available_service_types(self) -> List[str]:
        """Get list of available service types"""
        pass

    @abstractmethod
    def get_available_processor_types(self) -> List[str]:
        """Get list of available processor types"""
        pass

    @abstractmethod
    def get_available_converter_types(self) -> List[str]:
        """Get list of available converter types"""
        pass

    @abstractmethod
    def get_available_strategy_types(self) -> List[str]:
        """Get list of available strategy types"""
        pass


# =============================================================================
# PYDANTIC MODEL PROTOCOLS (for type hints)
# =============================================================================


class BiologicCreate(Protocol):
    """Protocol for biologic creation data"""

    name: str
    description: Optional[str]
    organism: Optional[str]
    biologic_type: str
    metadata: Optional[Dict[str, Any]]


class BiologicUpdate(Protocol):
    """Protocol for biologic update data"""

    name: Optional[str]
    description: Optional[str]
    organism: Optional[str]
    biologic_type: Optional[str]
    metadata: Optional[Dict[str, Any]]


class BiologicResponse(Protocol):
    """Protocol for biologic response data"""

    id: str
    name: str
    description: Optional[str]
    organism: Optional[str]
    biologic_type: str
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

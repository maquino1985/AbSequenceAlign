"""
Processing interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass
from datetime import datetime


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


class ProcessingObserver(ABC):
    """Observer interface for processing events"""

    @abstractmethod
    def on_step_completed(self, step: str, progress: float) -> None:
        """Called when a processing step is completed"""
        pass

    @abstractmethod
    def on_processing_completed(self, result: ProcessingResult) -> None:
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
    def notify_processing_completed(self, result: ProcessingResult) -> None:
        """Notify observers of processing completion"""
        pass

    @abstractmethod
    def notify_processing_failed(self, error: str) -> None:
        """Notify observers of processing failure"""
        pass


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
    def get_result(self) -> ProcessingResult:
        """Get the processing result"""
        pass


class ProcessingStatus:
    """Processing status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


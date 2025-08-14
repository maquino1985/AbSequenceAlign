"""
Interfaces module exports.
"""

from .processing import (
    ProcessingResult,
    ProcessingObserver,
    ProcessingSubject,
    ProcessingContext,
    ProcessingStatus,
)
from .processors import (
    Processor,
    SequenceProcessor,
    AnnotationProcessor,
    BiologicProcessor,
)
from .adapters import (
    AbstractExternalToolAdapter,
    ExternalToolAdapter,
)
from .repositories import Repository, BiologicRepository
from .factories import SimpleServiceFactory
from .models import (
    BiologicCreate,
    BiologicUpdate,
    BiologicResponse,
)
from .services import (
    AnnotationService,
    BiologicService,
)
from .utils import RegionExtractionInterface

__all__ = [
    # Processing
    "ProcessingResult",
    "ProcessingObserver", 
    "ProcessingSubject",
    "ProcessingContext",
    "ProcessingStatus",
    # Processors
    "Processor",
    "SequenceProcessor",
    "AnnotationProcessor",
    "BiologicProcessor",
    # Adapters
    "AbstractExternalToolAdapter",
    "ExternalToolAdapter",
    # Repositories
    "Repository",
    "BiologicRepository",
    # Factories
    "SimpleServiceFactory",
    # Models
    "BiologicCreate",
    "BiologicUpdate",
    "BiologicResponse",
    # Services
    "AnnotationService",
    "BiologicService",
    # Utils
    "RegionExtractionInterface",
]

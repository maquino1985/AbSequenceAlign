"""
Model protocols for type hints.
"""

from typing import Dict, Any, Optional, Protocol
from datetime import datetime


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


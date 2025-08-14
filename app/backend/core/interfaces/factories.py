"""
Factory interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Any


class SimpleServiceFactory(ABC):
    """Simple factory interface for creating services"""

    @abstractmethod
    def create_service(self, service_type: str, **kwargs) -> Any:
        """Create a service of the specified type"""
        pass

    @abstractmethod
    def get_available_service_types(self) -> List[str]:
        """Get list of available service types"""
        pass


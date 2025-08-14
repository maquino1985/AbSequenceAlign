"""
Repository interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar, Dict, Any

# Type variables
T = TypeVar("T")


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


class BiologicRepository(Repository[T], ABC):
    """Repository interface for biologic entities"""

    @abstractmethod
    def find_by_type(self, biologic_type: str) -> List[T]:
        """Find biologics by type"""
        pass

    @abstractmethod
    def find_by_organism(self, organism: str) -> List[T]:
        """Find biologics by organism"""
        pass

    @abstractmethod
    def find_by_filters(self, filters: Dict[str, Any]) -> List[T]:
        """Find biologics by filters"""
        pass

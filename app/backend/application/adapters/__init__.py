"""
Adapters for converting between domain entities and Pydantic/SQLAlchemy models.

This module provides the conversion layer between:
- Domain entities (business logic layer)
- Pydantic models (API layer) 
- SQLAlchemy models (database layer)

The adapters ensure that data can flow between these layers while maintaining
type safety and business rules.
"""

# from .domain_to_pydantic_adapter import DomainToPydanticAdapter
# from .pydantic_to_domain_adapter import PydanticToDomainAdapter
# from .domain_to_orm_adapter import DomainToORMAdapter
# from .orm_to_domain_adapter import ORMToDomainAdapter

__all__ = [
    # "DomainToPydanticAdapter",
    # "PydanticToDomainAdapter", 
    # "DomainToORMAdapter",
    # "ORMToDomainAdapter",
]

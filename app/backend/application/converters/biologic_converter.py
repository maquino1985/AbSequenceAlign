"""
Converter for biologic entities between domain, ORM, and Pydantic models.
Implements the Converter pattern for type transformations.
"""

from uuid import uuid4
from typing import Dict, Any

from backend.core.base_classes import AbstractBiologicConverter
from backend.database.models import Biologic
from backend.domain.entities import BiologicEntity
from backend.models.biologic_models import BiologicResponse, BiologicCreate
from backend.logger import logger


class BiologicConverterImpl(
    AbstractBiologicConverter[BiologicEntity, Biologic]
):
    """Concrete converter implementation for biologic entities."""

    def __init__(self):
        super().__init__()
        self._logger = logger

    def convert_to_orm(self, domain_entity: BiologicEntity) -> Biologic:
        """Convert domain entity to ORM model."""
        try:
            self._logger.debug(
                f"Converting domain entity to ORM: {domain_entity.name}"
            )

            # Create biologic ORM model
            biologic = Biologic(
                name=domain_entity.name,
                description=domain_entity.description
                or f"Biologic: {domain_entity.name}",
                organism=domain_entity.organism,
                biologic_type=domain_entity.biologic_type,
                metadata_json={
                    "domain_entity_id": domain_entity.id,
                    "chain_count": len(domain_entity.chains),
                    "total_length": domain_entity.total_length,
                    **domain_entity.metadata,
                },
            )

            self._logger.debug(
                f"Successfully converted domain entity to ORM: {domain_entity.name}"
            )
            return biologic

        except Exception as e:
            self._logger.error(f"Error converting domain entity to ORM: {e}")
            raise

    def convert_to_domain(self, orm_model: Biologic) -> BiologicEntity:
        """Convert ORM model to domain entity."""
        try:
            self._logger.debug(
                f"Converting ORM model to domain entity: {orm_model.name}"
            )

            # Create domain entity
            domain_entity = BiologicEntity(
                name=orm_model.name,
                biologic_type=orm_model.biologic_type,
                description=orm_model.description,
                organism=orm_model.organism,
                chains=[],  # Would be populated from ORM chains
                metadata=orm_model.metadata_json or {},
            )

            self._logger.debug(
                f"Successfully converted ORM model to domain entity: {orm_model.name}"
            )
            return domain_entity

        except Exception as e:
            self._logger.error(
                f"Error converting ORM model to domain entity: {e}"
            )
            raise

    def convert_to_pydantic(
        self, domain_entity: BiologicEntity
    ) -> BiologicResponse:
        """Convert domain entity to Pydantic response model."""
        try:
            self._logger.debug(
                f"Converting domain entity to Pydantic: {domain_entity.name}"
            )

            # Create Pydantic response
            biologic_response = BiologicResponse(
                id=str(uuid4()),  # Generate new ID for response
                name=domain_entity.name,
                description=f"Biologic: {domain_entity.name}",
                biologic_type=domain_entity.biologic_type,
                organism=domain_entity.organism,
                metadata=domain_entity.metadata,
                chains=[],  # Would be populated from domain chains
                created_at=None,
                updated_at=None,
            )

            self._logger.debug(
                f"Successfully converted domain entity to Pydantic: {domain_entity.name}"
            )
            return biologic_response

        except Exception as e:
            self._logger.error(
                f"Error converting domain entity to Pydantic: {e}"
            )
            raise

    def convert_from_pydantic(
        self, pydantic_model: BiologicCreate
    ) -> BiologicEntity:
        """Convert Pydantic create model to domain entity."""
        try:
            self._logger.debug(
                f"Converting Pydantic model to domain entity: {pydantic_model.name}"
            )

            # For now, we'll create a simple domain entity
            # In a full implementation, you'd convert chains, sequences, etc.
            domain_entity = BiologicEntity(
                name=pydantic_model.name,
                biologic_type=pydantic_model.biologic_type,
                description=pydantic_model.description,
                organism=pydantic_model.organism,
                chains=[],  # Would be populated from pydantic_model.chains
                metadata=pydantic_model.metadata or {},
            )

            self._logger.debug(
                f"Successfully converted Pydantic model to domain entity: {pydantic_model.name}"
            )
            return domain_entity

        except Exception as e:
            self._logger.error(
                f"Error converting Pydantic model to domain entity: {e}"
            )
            raise



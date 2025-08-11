"""
Processor for biologic entities following the Template Method pattern.
Implements biologic processing with validation, conversion, and persistence.
"""

from typing import Dict, Any, Optional, List
from backend.core.exceptions import ValidationError
from backend.domain.entities import BiologicEntity
from backend.core.base_classes import AbstractBiologicProcessor
from backend.database.models import Biologic
from backend.models.biologic_models import BiologicCreate, BiologicResponse
from backend.application.converters.biologic_converter import (
    BiologicConverterImpl,
)
from backend.infrastructure.repositories.biologic_repository import (
    BiologicRepositoryImpl,
)
from backend.logger import logger


class BiologicProcessorImpl(AbstractBiologicProcessor[BiologicCreate]):
    """Concrete processor implementation for biologic entities."""

    def __init__(
        self,
        repository: BiologicRepositoryImpl = None,
        converter: BiologicConverterImpl = None,
    ):
        super().__init__()
        self._repository = repository
        self._converter = converter or BiologicConverterImpl()
        self._logger = logger

    def _validate_biologic_data(self, data: BiologicCreate) -> BiologicCreate:
        """Validate biologic data according to business rules."""
        try:
            self._logger.debug(f"Validating biologic data: {data.name}")

            # Basic validation
            if not data.name or not data.name.strip():
                raise ValidationError(
                    "Biologic name is required", field="name"
                )

            if len(data.name) > 255:
                raise ValidationError(
                    "Biologic name must be less than 255 characters",
                    field="name",
                )

            if data.description and len(data.description) > 1000:
                raise ValidationError(
                    "Biologic description must be less than 1000 characters",
                    field="description",
                )

            # Validate biologic type
            valid_types = ["antibody", "protein", "dna", "rna"]
            if data.biologic_type not in valid_types:
                raise ValidationError(
                    f"Biologic type must be one of: {valid_types}",
                    field="biologic_type",
                )

            # Validate organism (optional but if provided, must be valid)
            if data.organism and len(data.organism) > 100:
                raise ValidationError(
                    "Organism name must be less than 100 characters",
                    field="organism",
                )

            # Validate metadata (optional)
            if data.metadata:
                if not isinstance(data.metadata, dict):
                    raise ValidationError(
                        "Metadata must be a dictionary", field="metadata"
                    )

                # Check for any invalid keys in metadata
                invalid_keys = [
                    k for k in data.metadata.keys() if not isinstance(k, str)
                ]
                if invalid_keys:
                    raise ValidationError(
                        "Metadata keys must be strings", field="metadata"
                    )

            self._logger.debug(
                f"Successfully validated biologic data: {data.name}"
            )
            return data

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error validating biologic data: {e}")
            raise ValidationError(f"Validation failed: {str(e)}")

    def _process_biologic_entity(
        self, data: BiologicCreate
    ) -> BiologicResponse:
        """Process biologic entity according to business logic."""
        try:
            self._logger.debug(f"Processing biologic entity: {data.name}")

            # Convert Pydantic model to domain entity
            domain_entity = self._converter.convert_from_pydantic(data)

            # Apply business logic based on biologic type
            if data.biologic_type == "antibody":
                domain_entity = self._process_antibody_biologic(
                    domain_entity, data
                )
            elif data.biologic_type == "protein":
                domain_entity = self._process_protein_biologic(
                    domain_entity, data
                )
            elif data.biologic_type == "dna":
                domain_entity = self._process_dna_biologic(domain_entity, data)
            elif data.biologic_type == "rna":
                domain_entity = self._process_rna_biologic(domain_entity, data)

            # Convert domain entity to Pydantic response
            biologic_response = self._converter.convert_to_pydantic(
                domain_entity
            )

            self._logger.debug(
                f"Successfully processed biologic entity: {data.name}"
            )
            return biologic_response

        except Exception as e:
            self._logger.error(f"Error processing biologic entity: {e}")
            raise

    async def _persist_biologic(
        self, biologic: BiologicResponse
    ) -> BiologicResponse:
        """Persist biologic entity to database."""
        try:
            self._logger.debug(f"Persisting biologic entity: {biologic.name}")

            if not self._repository:
                self._logger.warning(
                    "No repository provided, skipping persistence"
                )
                return biologic

            # Convert Pydantic response back to domain entity for persistence
            # This is a simplified approach - in a real implementation, you'd have
            # the original domain entity from the processing step
            domain_entity = BiologicEntity(
                name=biologic.name,
                description=biologic.description,
                organism=biologic.organism,
                biologic_type=biologic.biologic_type,
                chains=[],  # Would be populated from biologic.chains
                metadata=biologic.metadata or {},
            )

            # Convert domain entity to ORM model
            orm_model = self._converter.convert_to_orm(domain_entity)

            # Set organism if provided
            if biologic.organism:
                orm_model.organism = biologic.organism

            # Persist to database
            if self._repository:
                persisted_orm = await self._repository.save(orm_model)
            else:
                persisted_orm = orm_model

            # Convert back to response
            persisted_domain = self._converter.convert_to_domain(persisted_orm)
            persisted_response = self._converter.convert_to_pydantic(
                persisted_domain
            )

            # Update with actual database ID and timestamps
            persisted_response.id = str(persisted_orm.id)
            persisted_response.created_at = persisted_orm.created_at
            persisted_response.updated_at = persisted_orm.updated_at

            self._logger.debug(
                f"Successfully persisted biologic entity: {biologic.name}"
            )
            return persisted_response

        except Exception as e:
            self._logger.error(f"Error persisting biologic entity: {e}")
            raise

    def _process_antibody_biologic(
        self, domain_entity: BiologicEntity, data: BiologicCreate
    ) -> BiologicEntity:
        """Process antibody biologic with specific business logic."""
        try:
            self._logger.debug(f"Processing antibody biologic: {data.name}")

            # Add antibody-specific metadata
            domain_entity.metadata.update(
                {
                    "biologic_type": "antibody",
                    "processing_stage": "annotated",
                    "source": (
                        data.metadata.get("source", "manual_input")
                        if data.metadata
                        else "manual_input"
                    ),
                }
            )

            # Apply antibody-specific validation
            if not domain_entity.chains:
                self._logger.warning(
                    f"No chains found for antibody biologic: {data.name}"
                )

            # Add antibody-specific features
            for chain in domain_entity.chains:
                if chain.chain_type.value.upper() in ["HEAVY", "LIGHT"]:
                    chain.metadata["is_standard_antibody"] = True
                else:
                    chain.metadata["is_standard_antibody"] = False

            return domain_entity

        except Exception as e:
            self._logger.error(f"Error processing antibody biologic: {e}")
            raise

    def _process_protein_biologic(
        self, domain_entity: BiologicEntity, data: BiologicCreate
    ) -> BiologicEntity:
        """Process protein biologic with specific business logic."""
        try:
            self._logger.debug(f"Processing protein biologic: {data.name}")

            # Add protein-specific metadata
            domain_entity.metadata.update(
                {
                    "biologic_type": "protein",
                    "processing_stage": "validated",
                    "source": (
                        data.metadata.get("source", "manual_input")
                        if data.metadata
                        else "manual_input"
                    ),
                }
            )

            # Apply protein-specific validation
            # (In a real implementation, you'd validate protein sequences)

            return domain_entity

        except Exception as e:
            self._logger.error(f"Error processing protein biologic: {e}")
            raise

    def _process_dna_biologic(
        self, domain_entity: BiologicEntity, data: BiologicCreate
    ) -> BiologicEntity:
        """Process DNA biologic with specific business logic."""
        try:
            self._logger.debug(f"Processing DNA biologic: {data.name}")

            # Add DNA-specific metadata
            domain_entity.metadata.update(
                {
                    "biologic_type": "dna",
                    "processing_stage": "validated",
                    "source": (
                        data.metadata.get("source", "manual_input")
                        if data.metadata
                        else "manual_input"
                    ),
                }
            )

            # Apply DNA-specific validation
            # (In a real implementation, you'd validate DNA sequences)

            return domain_entity

        except Exception as e:
            self._logger.error(f"Error processing DNA biologic: {e}")
            raise

    def _process_rna_biologic(
        self, domain_entity: BiologicEntity, data: BiologicCreate
    ) -> BiologicEntity:
        """Process RNA biologic with specific business logic."""
        try:
            self._logger.debug(f"Processing RNA biologic: {data.name}")

            # Add RNA-specific metadata
            domain_entity.metadata.update(
                {
                    "biologic_type": "rna",
                    "processing_stage": "validated",
                    "source": (
                        data.metadata.get("source", "manual_input")
                        if data.metadata
                        else "manual_input"
                    ),
                }
            )

            # Apply RNA-specific validation
            # (In a real implementation, you'd validate RNA sequences)

            return domain_entity

        except Exception as e:
            self._logger.error(f"Error processing RNA biologic: {e}")
            raise

    def validate_biologic_data(self, data: BiologicCreate) -> bool:
        """Validate biologic data - interface method."""
        try:
            self._validate_biologic_data(data)
            return True
        except ValidationError:
            return False

    def process_biologic_entity(
        self, data: BiologicCreate
    ) -> BiologicResponse:
        """Process biologic entity - interface method."""
        return self._process_biologic_entity(data)

    def convert_domain_to_orm(self, domain_entity: BiologicEntity) -> Biologic:
        """Convert domain entity to ORM model - interface method."""
        return self._converter.convert_to_orm(domain_entity)

    def convert_orm_to_domain(self, orm_model: Biologic) -> BiologicEntity:
        """Convert ORM model to domain entity - interface method."""
        return self._converter.convert_to_domain(orm_model)

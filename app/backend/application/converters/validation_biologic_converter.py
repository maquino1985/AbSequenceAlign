"""
Validation biologic converter with enhanced validation capabilities.
Implements the Decorator pattern for adding validation to converters.
"""


from typing import Dict, Any, List
from backend.core.base_classes import AbstractBiologicConverter
from backend.core.interfaces import (
    BiologicConverter,
    BiologicValidationStrategy,
)
from backend.core.exceptions import ValidationError
from backend.domain.entities import BiologicEntity
from backend.database.models import Biologic
from backend.models.biologic_models import BiologicCreate, BiologicResponse
from backend.logger import logger


class ValidationBiologicConverterImpl(
    AbstractBiologicConverter[BiologicEntity, Biologic]
):
    """Validation-enhanced converter implementation for biologic entities."""

    def __init__(
        self,
        base_converter: BiologicConverter,
        validation_strategies: Dict[str, BiologicValidationStrategy] = None,
    ):
        super().__init__()
        self._base_converter = base_converter
        self._validation_strategies = validation_strategies or {}
        self._logger = logger

    def convert_to_orm(self, domain_entity: BiologicEntity) -> Biologic:
        """Convert domain entity to ORM model with validation."""
        try:
            self._logger.debug(
                f"Converting domain entity to ORM with validation: {domain_entity.name}"
            )

            # Validate domain entity before conversion
            self._validate_domain_entity(domain_entity)

            # Use base converter
            orm_model = self._base_converter.convert_to_orm(domain_entity)

            # Validate ORM model after conversion
            self._validate_orm_model(orm_model)

            self._logger.debug(
                f"Successfully converted domain entity to ORM with validation: {domain_entity.name}"
            )
            return orm_model

        except Exception as e:
            self._logger.error(
                f"Error converting domain entity to ORM with validation: {e}"
            )
            raise

    def convert_to_domain(self, orm_model: Biologic) -> BiologicEntity:
        """Convert ORM model to domain entity with validation."""
        try:
            self._logger.debug(
                f"Converting ORM model to domain entity with validation: {orm_model.name}"
            )

            # Validate ORM model before conversion
            self._validate_orm_model(orm_model)

            # Use base converter
            domain_entity = self._base_converter.convert_to_domain(orm_model)

            # Validate domain entity after conversion
            self._validate_domain_entity(domain_entity)

            self._logger.debug(
                f"Successfully converted ORM model to domain entity with validation: {orm_model.name}"
            )
            return domain_entity

        except Exception as e:
            self._logger.error(
                f"Error converting ORM model to domain entity with validation: {e}"
            )
            raise

    def convert_to_pydantic(
        self, domain_entity: BiologicEntity
    ) -> BiologicResponse:
        """Convert domain entity to Pydantic response model with validation."""
        try:
            self._logger.debug(
                f"Converting domain entity to Pydantic with validation: {domain_entity.name}"
            )

            # Validate domain entity before conversion
            self._validate_domain_entity(domain_entity)

            # Use base converter
            pydantic_model = self._base_converter.convert_to_pydantic(
                domain_entity
            )

            # Validate Pydantic model after conversion
            self._validate_pydantic_model(pydantic_model)

            self._logger.debug(
                f"Successfully converted domain entity to Pydantic with validation: {domain_entity.name}"
            )
            return pydantic_model

        except Exception as e:
            self._logger.error(
                f"Error converting domain entity to Pydantic with validation: {e}"
            )
            raise

    def convert_from_pydantic(
        self, pydantic_model: BiologicCreate
    ) -> BiologicEntity:
        """Convert Pydantic model to domain entity with validation."""
        try:
            self._logger.debug(
                f"Converting Pydantic model to domain entity with validation: {pydantic_model.name}"
            )

            # Validate Pydantic model before conversion
            self._validate_pydantic_create_model(pydantic_model)

            # Use base converter
            domain_entity = self._base_converter.convert_from_pydantic(
                pydantic_model
            )

            # Validate domain entity after conversion
            self._validate_domain_entity(domain_entity)

            self._logger.debug(
                f"Successfully converted Pydantic model to domain entity with validation: {pydantic_model.name}"
            )
            return domain_entity

        except Exception as e:
            self._logger.error(
                f"Error converting Pydantic model to domain entity with validation: {e}"
            )
            raise

    def _validate_domain_entity(self, domain_entity: BiologicEntity) -> None:
        """Validate domain entity."""
        try:
            # Basic validation
            if not domain_entity.name or not domain_entity.name.strip():
                raise ValidationError("Domain entity name is required")

            if not domain_entity.chains:
                self._logger.warning(
                    f"Domain entity {domain_entity.name} has no chains"
                )

            # Validate each chain
            for chain in domain_entity.chains:
                self._validate_antibody_chain(chain)

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error validating domain entity: {e}")
            raise ValidationError(f"Domain entity validation failed: {str(e)}")

    def _validate_orm_model(self, orm_model: Biologic) -> None:
        """Validate ORM model."""
        try:
            # Basic validation
            if not orm_model.name or not orm_model.name.strip():
                raise ValidationError("ORM model name is required")

            if not orm_model.biologic_type:
                raise ValidationError("ORM model biologic type is required")

            # Validate biologic type
            valid_types = ["antibody", "protein", "dna", "rna"]
            if orm_model.biologic_type not in valid_types:
                raise ValidationError(
                    f"Invalid biologic type: {orm_model.biologic_type}"
                )

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error validating ORM model: {e}")
            raise ValidationError(f"ORM model validation failed: {str(e)}")

    def _validate_pydantic_model(
        self, pydantic_model: BiologicResponse
    ) -> None:
        """Validate Pydantic response model."""
        try:
            # Basic validation
            if not pydantic_model.name or not pydantic_model.name.strip():
                raise ValidationError("Pydantic model name is required")

            if not pydantic_model.biologic_type:
                raise ValidationError(
                    "Pydantic model biologic type is required"
                )

            # Validate biologic type
            valid_types = ["antibody", "protein", "dna", "rna"]
            if pydantic_model.biologic_type not in valid_types:
                raise ValidationError(
                    f"Invalid biologic type: {pydantic_model.biologic_type}"
                )

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error validating Pydantic model: {e}")
            raise ValidationError(
                f"Pydantic model validation failed: {str(e)}"
            )

    def _validate_pydantic_create_model(
        self, pydantic_model: BiologicCreate
    ) -> None:
        """Validate Pydantic create model."""
        try:
            # Basic validation
            if not pydantic_model.name or not pydantic_model.name.strip():
                raise ValidationError("Pydantic create model name is required")

            if not pydantic_model.biologic_type:
                raise ValidationError(
                    "Pydantic create model biologic type is required"
                )

            # Validate biologic type
            valid_types = ["antibody", "protein", "dna", "rna"]
            if pydantic_model.biologic_type not in valid_types:
                raise ValidationError(
                    f"Invalid biologic type: {pydantic_model.biologic_type}"
                )

            # Use validation strategy if available
            strategy = self._validation_strategies.get(
                pydantic_model.biologic_type.lower()
            )
            if strategy and strategy.can_validate(
                pydantic_model.biologic_type
            ):
                errors = strategy.validate(pydantic_model)
                if errors:
                    raise ValidationError(
                        f"Validation errors: {', '.join(errors)}"
                    )

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error validating Pydantic create model: {e}")
            raise ValidationError(
                f"Pydantic create model validation failed: {str(e)}"
            )

    def _validate_biologic_chain(self, chain) -> None:
        """Validate antibody chain."""
        try:
            # Basic validation
            if not chain.name or not chain.name.strip():
                raise ValidationError("Chain name is required")

            if not chain.sequence:
                raise ValidationError("Chain sequence is required")

            # Validate chain type
            valid_chain_types = ["HEAVY", "LIGHT", "KAPPA", "LAMBDA"]
            if (
                chain.chain_type
                and chain.chain_type.value not in valid_chain_types
            ):
                raise ValidationError(
                    f"Invalid chain type: {chain.chain_type.value}"
                )

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error validating antibody chain: {e}")
            raise ValidationError(
                f"Antibody chain validation failed: {str(e)}"
            )

    def add_validation_strategy(
        self, biologic_type: str, strategy: BiologicValidationStrategy
    ) -> None:
        """Add a validation strategy for a specific biologic type."""
        self._validation_strategies[biologic_type.lower()] = strategy
        self._logger.debug(
            f"Added validation strategy for biologic type: {biologic_type}"
        )

    def remove_validation_strategy(self, biologic_type: str) -> None:
        """Remove a validation strategy for a specific biologic type."""
        if biologic_type.lower() in self._validation_strategies:
            del self._validation_strategies[biologic_type.lower()]
            self._logger.debug(
                f"Removed validation strategy for biologic type: {biologic_type}"
            )

    def get_available_validation_strategies(self) -> List[str]:
        """Get list of available validation strategy types."""
        return list(self._validation_strategies.keys())

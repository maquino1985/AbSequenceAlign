"""
Strategy-based biologic processor that uses different strategies for different biologic types.
Implements the Strategy pattern for flexible biologic processing.
"""


from backend.core.base_classes import AbstractBiologicProcessor
from backend.domain.entities import BiologicEntity
from backend.database.models import Biologic
from backend.models.biologic_models import BiologicCreate, BiologicResponse
from backend.application.converters.biologic_converter import (
    BiologicConverterImpl,
)
from backend.application.strategies.biologic_strategies import (
    BiologicProcessingStrategy,
)
from backend.logger import logger


class StrategyBiologicProcessorImpl(AbstractBiologicProcessor[BiologicCreate]):
    """Strategy-based processor implementation for biologic entities."""

    def __init__(
        self,
        repository=None,
        converter: BiologicConverterImpl = None,
        strategies: Dict[str, BiologicProcessingStrategy] = None,
    ):
        super().__init__()
        self._repository = repository
        self._converter = converter or BiologicConverterImpl()
        self._strategies = strategies or {}
        self._logger = logger

    def _validate_biologic_data(self, data: BiologicCreate) -> BiologicCreate:
        """Validate biologic data using appropriate strategy."""
        try:
            self._logger.debug(
                f"Validating biologic data with strategy: {data.biologic_type}"
            )

            # Find appropriate strategy
            strategy = self._get_strategy_for_type(data.biologic_type)
            if not strategy:
                raise ValidationError(
                    f"No strategy available for biologic type: {data.biologic_type}"
                )

            # Validate using strategy
            if not strategy.validate(data):
                raise ValidationError(
                    f"Validation failed for biologic type: {data.biologic_type}"
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
        """Process biologic entity using appropriate strategy."""
        try:
            self._logger.debug(
                f"Processing biologic entity with strategy: {data.biologic_type}"
            )

            # Find appropriate strategy
            strategy = self._get_strategy_for_type(data.biologic_type)
            if not strategy:
                raise ValidationError(
                    f"No strategy available for biologic type: {data.biologic_type}"
                )

            # Process using strategy
            biologic_response = strategy.process(data)

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
            persisted_orm = await self._repository.save(orm_model)

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

    def _get_strategy_for_type(
        self, biologic_type: str
    ) -> Optional[BiologicProcessingStrategy]:
        """Get the appropriate strategy for the given biologic type."""
        strategy = self._strategies.get(biologic_type.lower())
        if strategy and strategy.can_process(biologic_type):
            return strategy
        return None

    def add_strategy(
        self, biologic_type: str, strategy: BiologicProcessingStrategy
    ) -> None:
        """Add a strategy for a specific biologic type."""
        self._strategies[biologic_type.lower()] = strategy
        self._logger.debug(
            f"Added strategy for biologic type: {biologic_type}"
        )

    def remove_strategy(self, biologic_type: str) -> None:
        """Remove a strategy for a specific biologic type."""
        if biologic_type.lower() in self._strategies:
            del self._strategies[biologic_type.lower()]
            self._logger.debug(
                f"Removed strategy for biologic type: {biologic_type}"
            )

    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy types."""
        return list(self._strategies.keys())

    # Interface method implementations
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

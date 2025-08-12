"""
Biologic service for managing biologic entities with ORM integration.
Implements the Service pattern with Observer pattern for processing notifications.
"""

from typing import Dict, Any, List, Optional


from backend.core.base_classes import AbstractProcessingSubject
from backend.core.interfaces import (
    BiologicService as IBiologicService,
    BiologicRepository,
    BiologicProcessor,
    ProcessingResult,
)
from backend.core.exceptions import ValidationError, EntityNotFoundError
from backend.database.models import (
    Chain,
    Sequence,
    ChainSequence,
    SequenceDomain,
    DomainFeature,
)
from backend.domain.entities import (
    BiologicEntity,
    BiologicChain,
    BiologicSequence,
    BiologicDomain,
    BiologicFeature,
)
from backend.domain.value_objects import (
    ConfidenceScore,
)
from backend.models.biologic_models import (
    ChainResponse,
    ChainCreate,
    SequenceResponse,
    SequenceCreate,
    BiologicCreate,
    BiologicResponse,
    BiologicUpdate,
)
from backend.database.models import Biologic
from backend.infrastructure.repositories.biologic_repository import (
    BiologicRepositoryImpl,
)
from backend.application.processors.biologic_processor import (
    BiologicProcessorImpl,
)
from backend.application.converters.biologic_converter import (
    BiologicConverterImpl,
)
from backend.logger import logger


class BiologicServiceImpl(AbstractProcessingSubject, IBiologicService):
    """Concrete service implementation for biologic entity management."""

    def __init__(
        self,
        repository: BiologicRepository = None,
        processor: BiologicProcessor = None,
    ):
        super().__init__()
        self._repository = repository
        self._processor = processor
        self._converter = BiologicConverterImpl()
        self._logger = logger

    async def create_biologic(
        self, biologic_data: BiologicCreate
    ) -> BiologicResponse:
        """Create a new biologic entity."""
        try:
            self._logger.info(
                f"Creating biologic entity: {biologic_data.name}"
            )
            self.notify_step_completed("start", 0.0)

            # Validate input data
            if not biologic_data.name or not biologic_data.name.strip():
                raise ValidationError(
                    "Biologic name is required", field="name"
                )

            # Create ORM model
            biologic = Biologic(
                name=biologic_data.name,
                description=biologic_data.description,
                organism=biologic_data.organism,
                biologic_type=biologic_data.biologic_type,
                metadata_json=biologic_data.metadata or {},
            )

            # Persist to database
            if self._repository:
                biologic = await self._repository.save(biologic)
                self._logger.info(
                    f"Successfully created biologic entity: {biologic.name} (ID: {biologic.id})"
                )
            else:
                self._logger.warning(
                    "No repository provided, skipping persistence"
                )

            # Convert to response
            biologic_response = BiologicResponse(
                id=str(biologic.id),
                name=biologic.name,
                description=biologic.description,
                organism=biologic.organism,
                biologic_type=biologic.biologic_type,
                metadata=biologic.metadata_json,
                chains=[],  # Would be populated from biologic.chains
                created_at=biologic.created_at,
                updated_at=biologic.updated_at,
            )

            self.notify_step_completed("complete", 1.0)
            return biologic_response

        except Exception as e:
            self.notify_processing_failed(str(e))
            self._logger.error(f"Error creating biologic entity: {e}")
            raise

    async def get_biologic(self, biologic_id: str) -> BiologicResponse:
        """Get a biologic entity by ID."""
        try:
            self._logger.info(f"Retrieving biologic entity: {biologic_id}")

            if not self._repository:
                raise EntityNotFoundError("Repository not available")

            biologic = await self._repository.find_by_id(biologic_id)
            if not biologic:
                raise EntityNotFoundError(
                    f"Biologic with ID {biologic_id} not found"
                )

            # Convert to response
            biologic_response = BiologicResponse(
                id=str(biologic.id),
                name=biologic.name,
                description=biologic.description,
                organism=biologic.organism,
                biologic_type=biologic.biologic_type,
                metadata=biologic.metadata_json,
                chains=[],  # Would be populated from biologic.chains
                created_at=biologic.created_at,
                updated_at=biologic.updated_at,
            )

            self._logger.info(
                f"Successfully retrieved biologic entity: {biologic.name}"
            )
            return biologic_response

        except EntityNotFoundError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error retrieving biologic entity {biologic_id}: {e}"
            )
            raise

    async def list_biologics(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[BiologicResponse]:
        """List all biologic entities."""
        try:
            self._logger.info("Listing biologic entities")

            if not self._repository:
                return []

            biologics = await self._repository.find_all(
                limit=limit, offset=offset
            )

            # Convert to responses
            biologic_responses = []
            for biologic in biologics:
                biologic_response = BiologicResponse(
                    id=str(biologic.id),
                    name=biologic.name,
                    description=biologic.description,
                    organism=biologic.organism,
                    biologic_type=biologic.biologic_type,
                    metadata=biologic.metadata_json,
                    chains=[],  # Would be populated from biologic.chains
                    created_at=biologic.created_at,
                    updated_at=biologic.updated_at,
                )
                biologic_responses.append(biologic_response)

            self._logger.info(
                f"Successfully listed {len(biologic_responses)} biologic entities"
            )
            return biologic_responses

        except Exception as e:
            self._logger.error(f"Error listing biologic entities: {e}")
            raise

    async def update_biologic(
        self, biologic_id: str, update_data: BiologicUpdate
    ) -> BiologicResponse:
        """Update a biologic entity."""
        try:
            self._logger.info(f"Updating biologic entity: {biologic_id}")

            if not self._repository:
                raise EntityNotFoundError("Repository not available")

            # Get existing biologic
            biologic = await self._repository.find_by_id(biologic_id)
            if not biologic:
                raise EntityNotFoundError(
                    f"Biologic with ID {biologic_id} not found"
                )

            # Update fields
            if update_data.name is not None:
                biologic.name = update_data.name
            if update_data.description is not None:
                biologic.description = update_data.description
            if update_data.organism is not None:
                biologic.organism = update_data.organism
            if update_data.biologic_type is not None:
                biologic.biologic_type = update_data.biologic_type
            if update_data.metadata is not None:
                biologic.metadata_json = update_data.metadata

            # Persist changes
            biologic = await self._repository.save(biologic)

            # Convert to response
            biologic_response = BiologicResponse(
                id=str(biologic.id),
                name=biologic.name,
                description=biologic.description,
                organism=biologic.organism,
                biologic_type=biologic.biologic_type,
                metadata=biologic.metadata_json,
                chains=[],  # Would be populated from biologic.chains
                created_at=biologic.created_at,
                updated_at=biologic.updated_at,
            )

            self._logger.info(
                f"Successfully updated biologic entity: {biologic.name}"
            )
            return biologic_response

        except EntityNotFoundError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error updating biologic entity {biologic_id}: {e}"
            )
            raise

    async def delete_biologic(self, biologic_id: str) -> bool:
        """Delete a biologic entity."""
        try:
            self._logger.info(f"Deleting biologic entity: {biologic_id}")

            if not self._repository:
                return False

            success = await self._repository.delete(biologic_id)
            if success:
                self._logger.info(
                    f"Successfully deleted biologic entity: {biologic_id}"
                )
            else:
                self._logger.warning(
                    f"Failed to delete biologic entity: {biologic_id}"
                )

            return success

        except Exception as e:
            self._logger.error(
                f"Error deleting biologic entity {biologic_id}: {e}"
            )
            raise

    async def process_and_persist_biologic(
        self, biologic_data: BiologicCreate
    ) -> ProcessingResult:
        """Process and persist a biologic entity."""
        try:
            self._logger.info(
                f"Processing and persisting biologic entity: {biologic_data.name}"
            )
            self.notify_step_completed("start", 0.0)

            if not self._processor:
                raise ValidationError("Processor not available")

            # Process biologic using the processor
            result = self._processor.process_biologic(biologic_data)

            if result.success:
                self.notify_step_completed("complete", 1.0)
                self._logger.info(
                    f"Successfully processed and persisted biologic entity: {biologic_data.name}"
                )
            else:
                self.notify_processing_failed(result.error)
                self._logger.error(
                    f"Failed to process biologic entity: {result.error}"
                )

            return result

        except Exception as e:
            self.notify_processing_failed(str(e))
            self._logger.error(f"Error processing biologic entity: {e}")
            return ProcessingResult(success=False, error=str(e))

    async def search_biologics(
        self, search_criteria: Dict[str, Any]
    ) -> List[BiologicResponse]:
        """Search biologics by criteria."""
        try:
            self._logger.info(
                f"Searching biologic entities with criteria: {search_criteria}"
            )

            if not self._repository:
                return []

            biologics = await self._repository.search_biologics(
                search_criteria
            )

            # Convert to responses
            biologic_responses = []
            for biologic in biologics:
                biologic_response = BiologicResponse(
                    id=str(biologic.id),
                    name=biologic.name,
                    description=biologic.description,
                    organism=biologic.organism,
                    biologic_type=biologic.biologic_type,
                    metadata=biologic.metadata_json,
                    chains=[],  # Would be populated from biologic.chains
                    created_at=biologic.created_at,
                    updated_at=biologic.updated_at,
                )
                biologic_responses.append(biologic_response)

            self._logger.info(
                f"Successfully found {len(biologic_responses)} biologic entities"
            )
            return biologic_responses

        except Exception as e:
            self._logger.error(f"Error searching biologic entities: {e}")
            raise

    # Legacy methods for backward compatibility
    def create_biologic_from_biologic_entity(
        self, biologic_entity: BiologicEntity, organism: Optional[str] = None
    ) -> Biologic:
        """Create a Biologic ORM model from an AntibodySequence domain entity."""
        try:
            self._logger.debug(
                f"Creating biologic from biologic entity: {biologic_entity.name}"
            )

            # Create the biologic entity
            biologic = Biologic(
                name=biologic_entity.name,
                description=f"Biologic: {biologic_entity.name}",
                organism=organism,
                biologic_type=biologic_entity.biologic_type,
                metadata_json={
                    "domain_entity_id": biologic_entity.id,
                    "chain_count": len(biologic_entity.chains),
                    "total_length": biologic_entity.total_length,
                },
            )

            # Create chains for each biologic chain
            for biologic_chain in biologic_entity.chains:
                chain = self._create_chain_from_biologic_chain(
                    biologic, biologic_chain
                )
                biologic.chains.append(chain)

            self._logger.debug(
                f"Successfully created biologic from biologic entity: {biologic_entity.name}"
            )
            return biologic

        except Exception as e:
            self._logger.error(
                f"Error creating biologic from biologic entity: {e}"
            )
            raise

    def create_biologic_entity_from_biologic(
        self, biologic: Biologic
    ) -> BiologicEntity:
        """Create an AntibodySequence domain entity from a Biologic ORM model."""
        try:
            self._logger.debug(
                f"Creating antibody sequence from biologic: {biologic.name}"
            )

            # Convert chains to antibody chains
            chains = []
            for chain in biologic.chains:
                antibody_chain = self._create_antibody_chain_from_chain(chain)
                chains.append(antibody_chain)

            # Create domain entity
            biologic_entity = BiologicEntity(
                name=biologic.name,
                biologic_type=biologic.biologic_type,
                description=biologic.description,
                organism=biologic.organism,
                chains=chains,
                metadata=biologic.metadata_json or {},
            )

            self._logger.debug(
                f"Successfully created antibody sequence from biologic: {biologic.name}"
            )
            return biologic_entity

        except Exception as e:
            self._logger.error(
                f"Error creating antibody sequence from biologic: {e}"
            )
            raise

    async def process_and_persist_biologic_entity(
        self,
        biologic_entity: BiologicEntity,
        organism: Optional[str] = None,
    ) -> BiologicResponse:
        """Process and persist an antibody sequence as a biologic entity."""
        try:
            self._logger.info(
                f"Processing and persisting biologic entity: {biologic_entity.name}"
            )

            # Create biologic from biologic entity
            biologic = self.create_biologic_from_biologic_entity(
                biologic_entity, organism
            )

            # Persist to database
            if self._repository:
                biologic = await self._repository.save(biologic)
                self._logger.info(
                    f"Successfully persisted biologic entity: {biologic_entity.name}"
                )
            else:
                self._logger.warning(
                    "No repository provided, skipping persistence"
                )

            # Convert to response
            from datetime import datetime
            from backend.database import UUIDv7

            biologic_response = BiologicResponse(
                id=str(biologic.id) if biologic.id else UUIDv7()(),
                name=biologic.name,
                description=biologic.description,
                organism=biologic.organism,
                biologic_type=biologic.biologic_type,
                metadata=biologic.metadata_json,
                chains=[],  # Would be populated from biologic.chains
                created_at=biologic.created_at or datetime.now(),
                updated_at=biologic.updated_at or datetime.now(),
            )

            return biologic_response

        except Exception as e:
            self._logger.error(
                f"Error processing and persisting antibody sequence: {e}"
            )
            raise

    # Helper methods for chain conversion
    def _create_chain_from_biologic_chain(
        self, biologic: Biologic, biologic_chain: BiologicChain
    ) -> Chain:
        """Create a Chain ORM model from an AntibodyChain domain entity."""
        try:
            # Create chain ORM model
            chain = Chain(
                biologic_id=biologic.id,
                name=biologic_chain.name,
                chain_type=biologic_chain.chain_type,
                metadata_json={
                    "domain_entity_id": biologic_chain.id,
                    "sequence_count": len(biologic_chain.sequences),
                },
            )

            # Create sequences for each sequence in the chain
            chain_sequences = []
            for sequence in biologic_chain.sequences:
                orm_sequence = self._create_sequence_from_sequence(
                    chain=chain, biologic_sequence=sequence
                )
                # The sequence is returned with its chain_sequences already set
                # We need to extract the chain_sequence and add it to the chain
                if orm_sequence.chain_sequences:
                    chain_sequences.extend(orm_sequence.chain_sequences)

            # Set the chain_sequences on the chain
            chain.sequences = chain_sequences

            return chain

        except Exception as e:
            self._logger.error(
                f"Error creating chain from antibody chain: {e}"
            )
            raise

    def _create_biologic_chain_from_chain(self, chain: Chain) -> BiologicChain:
        """Create an AntibodyChain domain entity from a Chain ORM model."""
        try:
            # Convert sequences to biologic sequences
            biologic_sequences = []
            for chain_sequence in chain.sequences:
                # Get the actual sequence from the chain_sequence
                sequence = chain_sequence.sequence
                biologic_sequence = (
                    self._create_biologic_sequence_from_orm_sequence(
                        sequence=sequence
                    )
                )
                biologic_sequences.append(biologic_sequence)

            # Create domain entity
            biologic_chain = BiologicChain(
                name=chain.name,
                chain_type=chain.chain_type,  # Would need enum conversion
                sequences=biologic_sequences,
                metadata=chain.metadata_json or {},
            )

            return biologic_chain

        except Exception as e:
            self._logger.error(
                f"Error creating antibody chain from chain: {e}"
            )
            raise

    def _create_biologic_sequence_from_orm_sequence(
        self, sequence: Sequence
    ) -> BiologicSequence:
        """Create a BiologicSequence domain entity from a Sequence ORM model."""
        try:
            # Convert domains to biologic domains
            biologic_domains = []
            for chain_sequence in sequence.chain_sequences:
                for domain in chain_sequence.domains:
                    biologic_domain = (
                        self._create_biologic_domain_from_sequence_domain(
                            domain
                        )
                    )
                    biologic_domains.append(biologic_domain)

            # Create domain entity
            biologic_sequence = BiologicSequence(
                sequence_type=sequence.sequence_type,
                sequence_data=sequence.sequence_data,
                description=sequence.description,
                domains=biologic_domains,
                metadata=sequence.metadata_json or {},
            )

            return biologic_sequence

        except Exception as e:
            self._logger.error(
                f"Error creating biologic sequence from ORM sequence: {e}"
            )
            raise

    def _create_biologic_domain_from_sequence_domain(
        self, sequence_domain: SequenceDomain
    ) -> BiologicDomain:
        """Create a BiologicDomain domain entity from a SequenceDomain ORM model."""
        try:
            # Convert features to biologic features
            biologic_features = []
            for feature in sequence_domain.features:
                biologic_feature = (
                    self._create_biologic_feature_from_sequence_domain(
                        sequence_domain=sequence_domain
                    )
                )
                biologic_features.append(biologic_feature)

            # Create domain entity
            biologic_domain = BiologicDomain(
                domain_type=sequence_domain.domain_type,  # Would need enum conversion
                start_position=sequence_domain.start_position,
                end_position=sequence_domain.end_position,
                confidence_score=sequence_domain.confidence_score,
                features=biologic_features,
                metadata=sequence_domain.metadata_json or {},
            )

            return biologic_domain

        except Exception as e:
            self._logger.error(
                f"Error creating biologic domain from sequence domain: {e}"
            )
            raise

    def _create_sequence_from_sequence(
        self, chain: Chain, biologic_sequence: BiologicSequence
    ) -> Sequence:
        """Create a Sequence ORM model from a BiologicSequence domain entity."""
        try:
            # Create sequence ORM model
            metadata_json = {
                "sequence_entity_id": biologic_sequence.id,
                "sequence_type": biologic_sequence.sequence_type,
                "domain_count": len(biologic_sequence.domains),
            }

            sequence = Sequence(
                sequence_type=biologic_sequence.sequence_type,
                sequence_data=biologic_sequence.sequence_data,
                length=len(biologic_sequence.sequence_data),
                description=biologic_sequence.description
                or f"{biologic_sequence.sequence_type} sequence",
                metadata_json=metadata_json,
            )

            # Create ChainSequence to link the sequence to the chain
            chain_sequence = ChainSequence(
                chain_id=chain.id,
                sequence_id=sequence.id,  # This will be set after sequence is saved
                start_position=0,
                end_position=len(biologic_sequence.sequence_data),
                metadata_json={
                    "sequence_entity_id": biologic_sequence.id,
                    "chain_entity_id": chain.id,
                },
            )

            # Create SequenceDomain objects for each domain in the sequence
            sequence_domains = []
            for domain in biologic_sequence.domains:
                sequence_domain = SequenceDomain(
                    chain_sequence_id=chain_sequence.id,  # This will be set after chain_sequence is saved
                    domain_type=domain.domain_type.value,
                    start_position=domain.start_position,
                    end_position=domain.end_position,
                    species=domain.metadata.get("species"),
                    germline=domain.metadata.get("germline"),
                    confidence_score=domain.confidence_score,
                    metadata_json={
                        "domain_entity_id": domain.id,
                        "domain_type": domain.domain_type,
                    },
                )

                # Create features for each feature in the domain
                for feature in domain.features:
                    domain_feature = self._create_domain_feature_from_feature(
                        sequence_domain=sequence_domain,
                        biologic_feature=feature,
                    )
                    sequence_domain.features.append(domain_feature)

                sequence_domains.append(sequence_domain)

            # Set the domains on the chain_sequence
            chain_sequence.domains = sequence_domains

            # Set the chain_sequence on the sequence
            sequence.chain_sequences = [chain_sequence]

            return sequence

        except Exception as e:
            self._logger.error(f"Error creating sequence from sequence: {e}")
            raise

    def _create_biologic_domain_from_sequence(
        self, sequence: Sequence
    ) -> BiologicDomain:
        """Create an AntibodyDomain domain entity from a Sequence ORM model."""
        try:
            # Convert domains to regions
            regions = {}
            for sequence_domain in sequence.domains:
                antibody_region = (
                    self._create_antibody_region_from_sequence_domain(
                        sequence_domain
                    )
                )
                regions[antibody_region.name] = antibody_region

            # Create domain entity - use the first domain's type or default to VARIABLE
            domain_type = "VARIABLE"  # Default
            if sequence.domains:
                # Get domain type from the first domain
                first_domain = sequence.domains[0]
                if hasattr(first_domain, "domain_type"):
                    domain_type = first_domain.domain_type
                elif hasattr(first_domain, "domain_name"):
                    # Try to infer from domain name
                    if "constant" in first_domain.domain_name.lower():
                        domain_type = "CONSTANT"
                    elif "linker" in first_domain.domain_name.lower():
                        domain_type = "LINKER"

            biologic_domain = BiologicDomain(
                domain_type=domain_type,
                start_position=0,
                end_position=len(sequence.sequence_data),
                confidence_score=1.0,
                metadata=sequence.metadata_json or {},
            )

            return biologic_domain

        except Exception as e:
            self._logger.error(
                f"Error creating antibody domain from sequence: {e}"
            )
            raise

    def _create_domain_feature_from_feature(
        self,
        sequence_domain: SequenceDomain,
        biologic_feature: BiologicFeature,
    ) -> DomainFeature:
        """Create a DomainFeature ORM model from a BiologicFeature domain entity."""
        try:
            # Create domain feature ORM model
            domain_feature = DomainFeature(
                sequence_domain_id=sequence_domain.id,  # This will be set after sequence_domain is saved
                feature_type=biologic_feature.feature_type.value,
                name=biologic_feature.name,
                value=biologic_feature.value,
                start_position=biologic_feature.start_position,
                end_position=biologic_feature.end_position,
                confidence_score=biologic_feature.confidence_score,
                metadata_json={
                    "feature_entity_id": biologic_feature.id,
                    "feature_type": biologic_feature.feature_type,
                },
            )

            return domain_feature

        except Exception as e:
            self._logger.error(
                f"Error creating domain feature from feature: {e}"
            )
            raise

    def _create_sequence_domain_from_feature(
        self, sequence: Sequence, biologic_feature: BiologicFeature
    ) -> SequenceDomain:
        """Create a SequenceDomain ORM model from a BiologicFeature domain entity."""
        try:
            # Create sequence domain ORM model
            sequence_domain = SequenceDomain(
                chain_sequence_id=sequence.id,  # This should be chain_sequence_id, not sequence_id
                domain_type=biologic_feature.feature_type.value,  # Use domain_type instead of domain_name
                start_position=biologic_feature.start_position,
                end_position=biologic_feature.end_position,
                metadata_json={
                    "domain_entity_id": biologic_feature.id,
                    "feature_type": biologic_feature.feature_type,
                },
            )

            return sequence_domain

        except Exception as e:
            self._logger.error(
                f"Error creating sequence domain from feature: {e}"
            )
            raise

    def _create_biologic_feature_from_sequence_domain(
        self, sequence_domain: SequenceDomain
    ) -> BiologicFeature:
        """Create a BiologicFeature domain entity from a SequenceDomain ORM model."""
        try:
            # Create feature domain entity
            biologic_feature = BiologicFeature(
                name=sequence_domain.domain_type,  # Use domain_type instead of domain_name
                feature_type=sequence_domain.metadata_json.get(
                    "feature_type", "FR1"
                ),  # Would need enum conversion
                start_position=sequence_domain.start_position,
                end_position=sequence_domain.end_position,
                confidence_score=sequence_domain.confidence_score or 1.0,
                metadata=sequence_domain.metadata_json or {},
            )

            return biologic_feature

        except Exception as e:
            self._logger.error(
                f"Error creating biologic feature from sequence domain: {e}"
            )
            raise


# Additional service implementations for different use cases
class CachedBiologicServiceImpl(BiologicServiceImpl):
    """Biologic service with caching capabilities."""

    def __init__(
        self,
        repository: BiologicRepository = None,
        processor: BiologicProcessor = None,
    ):
        super().__init__(repository, processor)
        self._cache: Dict[str, BiologicResponse] = {}

    async def get_biologic(self, biologic_id: str) -> BiologicResponse:
        """Get a biologic entity by ID with caching."""
        # Check cache first
        if biologic_id in self._cache:
            self._logger.debug(f"Cache hit for biologic: {biologic_id}")
            return self._cache[biologic_id]

        # Get from repository
        biologic_response = await super().get_biologic(biologic_id)

        # Cache the result
        self._cache[biologic_id] = biologic_response
        self._logger.debug(f"Cached biologic: {biologic_id}")

        return biologic_response


class ValidationBiologicServiceImpl(BiologicServiceImpl):
    """Biologic service with enhanced validation."""

    def __init__(
        self,
        repository: BiologicRepository = None,
        processor: BiologicProcessor = None,
    ):
        super().__init__(repository, processor)

    async def create_biologic(
        self, biologic_data: BiologicCreate
    ) -> BiologicResponse:
        """Create a new biologic entity with enhanced validation."""
        # Perform additional validation
        self._validate_biologic_data_enhanced(biologic_data)

        # Call parent implementation
        return await super().create_biologic(biologic_data)

    def _validate_biologic_data_enhanced(
        self, biologic_data: BiologicCreate
    ) -> None:
        """Perform enhanced validation on biologic data."""
        # Additional validation rules
        if biologic_data.biologic_type == "antibody":
            if (
                not biologic_data.metadata
                or "chains" not in biologic_data.metadata
            ):
                raise ValidationError(
                    "Antibody biologics must have chains in metadata",
                    field="metadata",
                )

        # Add more validation rules as needed


# Alias for backward compatibility
BiologicService = BiologicServiceImpl

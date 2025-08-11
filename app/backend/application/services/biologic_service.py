"""
Biologic service for managing biologic entities with ORM integration.

This service bridges domain entities with ORM models, ensuring that:
- Domain entities are used for business logic
- ORM models are used for persistence
- Conversion happens at appropriate boundaries
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database.models import (
    Biologic,
    BiologicAlias,
    Chain,
    Sequence,
    ChainSequence,
    SequenceDomain,
    DomainFeature,
)
from backend.domain.entities import (
    AntibodySequence,
    AntibodyChain,
    AntibodyDomain,
    AntibodyRegion,
)
from backend.domain.value_objects import (
    AminoAcidSequence,
    RegionBoundary,
    ConfidenceScore,
)
from backend.models.biologic_models import (
    BiologicResponse,
    BiologicCreate,
    BiologicUpdate,
    ChainResponse,
    ChainCreate,
    SequenceResponse,
    SequenceCreate,
)
from backend.core.exceptions import ValidationError, EntityNotFoundError
from backend.logger import logger


class BiologicService:
    """Service for managing biologic entities with ORM integration"""

    def __init__(self):
        pass

    # =============================================================================
    # Domain Entity to ORM Model Conversion
    # =============================================================================

    def create_biologic_from_antibody_sequence(
        self, antibody_sequence: AntibodySequence, organism: Optional[str] = None
    ) -> Biologic:
        """
        Create a Biologic ORM model from an AntibodySequence domain entity.
        
        This is the key integration point where domain entities are converted
        to ORM models for persistence.
        """
        # Create the biologic entity
        biologic = Biologic(
            name=antibody_sequence.name,
            description=f"Antibody sequence: {antibody_sequence.name}",
            organism=organism,
            biologic_type="antibody",
            metadata_json={
                "domain_entity_id": antibody_sequence.id,
                "chain_count": len(antibody_sequence.chains),
                "total_length": antibody_sequence.total_length,
                "is_complete_antibody": antibody_sequence.is_complete_antibody(),
                "is_scfv": antibody_sequence.is_scfv(),
            }
        )

        # Create chains for each antibody chain
        for antibody_chain in antibody_sequence.chains:
            chain = self._create_chain_from_antibody_chain(biologic, antibody_chain)
            biologic.chains.append(chain)

        return biologic

    def _create_chain_from_antibody_chain(
        self, biologic: Biologic, antibody_chain: AntibodyChain
    ) -> Chain:
        """Create a Chain ORM model from an AntibodyChain domain entity."""
        chain = Chain(
            biologic_id=biologic.id,
            name=antibody_chain.name,
            chain_type=antibody_chain.chain_type.value,
            metadata_json={
                "domain_entity_id": antibody_chain.id,
                "chain_type": antibody_chain.chain_type.value,
                "length": len(antibody_chain.sequence),
                "domain_count": len(antibody_chain.domains),
            }
        )

        # Create sequences for each domain
        for domain in antibody_chain.domains:
            sequence = self._create_sequence_from_domain(domain)
            chain_sequence = ChainSequence(
                chain_id=chain.id,
                sequence_id=sequence.id,
                metadata_json={
                    "domain_type": domain.domain_type.value,
                    "domain_length": len(domain.sequence),
                }
            )
            chain.sequences.append(chain_sequence)

        return chain

    def _create_sequence_from_domain(self, domain: AntibodyDomain) -> Sequence:
        """Create a Sequence ORM model from an AntibodyDomain domain entity."""
        sequence = Sequence(
            sequence_type="PROTEIN",
            sequence_data=str(domain.sequence),
            length=len(domain.sequence),
            description=f"{domain.domain_type.value} domain sequence",
            metadata_json={
                "domain_entity_id": domain.id,
                "domain_type": domain.domain_type.value,
                "region_count": len(domain.regions),
            }
        )

        # Create sequence domains for each region
        for region_name, region in domain.regions.items():
            sequence_domain = self._create_sequence_domain_from_region(
                sequence, region, region_name
            )
            # Note: sequence_domain.chain_sequence_id will be set when chain_sequence is created
            # For now, we'll just store it in metadata
            sequence_domain.metadata_json["temp_chain_sequence_id"] = "pending"

        return sequence

    def _create_sequence_domain_from_region(
        self, sequence: Sequence, region: AntibodyRegion, region_name: str
    ) -> SequenceDomain:
        """Create a SequenceDomain ORM model from an AntibodyRegion domain entity."""
        sequence_domain = SequenceDomain(
            chain_sequence_id=sequence.id,  # This will be updated when chain_sequence is created
            domain_type=region.region_type.value,
            start_position=region.start,
            end_position=region.end,
            confidence_score=int(region.confidence_score.score * 100) if region.confidence_score else None,
            metadata_json={
                "domain_entity_id": region.id,
                "region_name": region_name,
                "region_type": region.region_type.value,
                "sequence": str(region.sequence),
            }
        )

        # Create domain features for any additional metadata
        for key, value in region.metadata.items():
            if isinstance(value, (str, int, float, bool)):
                feature = DomainFeature(
                    sequence_domain_id=sequence_domain.id,
                    feature_type="METADATA",
                    name=key,
                    value=str(value),
                    metadata_json={"source": "domain_entity_metadata"}
                )
                sequence_domain.features.append(feature)

        return sequence_domain

    # =============================================================================
    # ORM Model to Domain Entity Conversion
    # =============================================================================

    def create_antibody_sequence_from_biologic(
        self, biologic: Biologic
    ) -> AntibodySequence:
        """
        Create an AntibodySequence domain entity from a Biologic ORM model.
        
        This is the reverse conversion for when we need to work with domain entities
        in business logic.
        """
        chains = []
        for chain_orm in biologic.chains:
            antibody_chain = self._create_antibody_chain_from_chain(chain_orm)
            chains.append(antibody_chain)

        return AntibodySequence(
            name=biologic.name,
            chains=chains,
            metadata=biologic.metadata_json or {}
        )

    def _create_antibody_chain_from_chain(self, chain_orm: Chain) -> AntibodyChain:
        """Create an AntibodyChain domain entity from a Chain ORM model."""
        from backend.domain.models import ChainType

        # Create domains from sequences
        domains = []
        for chain_sequence in chain_orm.sequences:
            domain = self._create_antibody_domain_from_sequence(chain_sequence.sequence)
            domains.append(domain)

        # Create the antibody chain
        chain_type = ChainType(chain_orm.chain_type)
        sequence = AminoAcidSequence(chain_orm.sequences[0].sequence.sequence_data)

        return AntibodyChain(
            name=chain_orm.name,
            chain_type=chain_type,
            sequence=sequence,
            domains=domains,
            metadata=chain_orm.metadata_json or {}
        )

    def _create_antibody_domain_from_sequence(self, sequence_orm: Sequence) -> AntibodyDomain:
        """Create an AntibodyDomain domain entity from a Sequence ORM model."""
        from backend.domain.models import DomainType

        # Create regions from sequence domains
        regions = {}
        for chain_sequence in sequence_orm.chain_sequences:
            for sequence_domain in chain_sequence.domains:
                region = self._create_antibody_region_from_sequence_domain(sequence_domain)
                regions[sequence_domain.metadata_json.get("region_name", "unknown")] = region

        # Create the antibody domain
        domain_type = DomainType(sequence_orm.metadata_json.get("domain_type", "VARIABLE"))
        sequence = AminoAcidSequence(sequence_orm.sequence_data)

        return AntibodyDomain(
            domain_type=domain_type,
            sequence=sequence,
            numbering_scheme=None,  # This would need to be determined from context
            regions=regions,
            metadata=sequence_orm.metadata_json or {}
        )

    def _create_antibody_region_from_sequence_domain(
        self, sequence_domain: SequenceDomain
    ) -> AntibodyRegion:
        """Create an AntibodyRegion domain entity from a SequenceDomain ORM model."""
        from backend.domain.models import RegionType, NumberingScheme

        # Create boundary
        boundary = RegionBoundary(
            start=sequence_domain.start_position,
            end=sequence_domain.end_position
        )

        # Create sequence
        sequence = AminoAcidSequence(sequence_domain.metadata_json.get("sequence", ""))

        # Create confidence score
        confidence_score = None
        if sequence_domain.confidence_score is not None:
            confidence_score = ConfidenceScore(
                score=sequence_domain.confidence_score / 100.0,
                method="database"
            )

        # Create region type
        region_type = RegionType(sequence_domain.domain_type)

        return AntibodyRegion(
            name=sequence_domain.metadata_json.get("region_name", "unknown"),
            region_type=region_type,
            boundary=boundary,
            sequence=sequence,
            numbering_scheme=NumberingScheme.IMGT,  # Default, could be made configurable
            metadata=sequence_domain.metadata_json or {},
            confidence_score=confidence_score
        )

    # =============================================================================
    # Database Operations
    # =============================================================================

    async def create_biologic(
        self, db_session: AsyncSession, biologic_data: BiologicCreate
    ) -> BiologicResponse:
        """Create a new biologic entity in the database."""
        biologic = Biologic(
            name=biologic_data.name,
            description=biologic_data.description,
            organism=biologic_data.organism,
            biologic_type=biologic_data.biologic_type,
            metadata_json=biologic_data.metadata,
        )

        db_session.add(biologic)
        await db_session.commit()
        await db_session.refresh(biologic)

        return BiologicResponse.model_validate(biologic)

    async def get_biologic(
        self, db_session: AsyncSession, biologic_id: UUID
    ) -> BiologicResponse:
        """Get a biologic entity by ID."""
        stmt = (
            select(Biologic)
            .options(
                selectinload(Biologic.aliases),
                selectinload(Biologic.chains).selectinload(Chain.sequences)
            )
            .where(Biologic.id == biologic_id)
        )
        
        result = await db_session.execute(stmt)
        biologic = result.scalar_one_or_none()
        
        if not biologic:
            raise EntityNotFoundError(f"Biologic with ID {biologic_id} not found")
        
        return BiologicResponse.model_validate(biologic)

    async def list_biologics(
        self, db_session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[BiologicResponse]:
        """List biologic entities with pagination."""
        stmt = (
            select(Biologic)
            .options(
                selectinload(Biologic.aliases),
                selectinload(Biologic.chains)
            )
            .offset(skip)
            .limit(limit)
        )
        
        result = await db_session.execute(stmt)
        biologics = result.scalars().all()
        
        return [BiologicResponse.model_validate(biologic) for biologic in biologics]

    async def update_biologic(
        self, db_session: AsyncSession, biologic_id: UUID, update_data: BiologicUpdate
    ) -> BiologicResponse:
        """Update a biologic entity."""
        biologic = await self.get_biologic(db_session, biologic_id)
        
        # Update fields if provided
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

        await db_session.commit()
        await db_session.refresh(biologic)
        
        return BiologicResponse.model_validate(biologic)

    async def delete_biologic(
        self, db_session: AsyncSession, biologic_id: UUID
    ) -> None:
        """Delete a biologic entity."""
        biologic = await self.get_biologic(db_session, biologic_id)
        await db_session.delete(biologic)
        await db_session.commit()

    # =============================================================================
    # Integration with Annotation Service
    # =============================================================================

    async def process_and_persist_antibody_sequence(
        self,
        db_session: AsyncSession,
        antibody_sequence: AntibodySequence,
        organism: Optional[str] = None
    ) -> BiologicResponse:
        """
        Process an antibody sequence through annotation and persist it as a biologic.
        
        This method demonstrates the integration pattern:
        1. Use domain entities for business logic (annotation)
        2. Convert to ORM models for persistence
        3. Return Pydantic models for API responses
        """
        # Step 1: Process with domain entities (annotation would happen here)
        # For now, we'll just use the sequence as-is
        processed_sequence = antibody_sequence

        # Step 2: Convert to ORM model for persistence
        biologic = self.create_biologic_from_antibody_sequence(
            processed_sequence, organism
        )

        # Step 3: Persist to database
        db_session.add(biologic)
        await db_session.commit()
        await db_session.refresh(biologic)

        # Step 4: Return Pydantic model for API response
        return BiologicResponse.model_validate(biologic)

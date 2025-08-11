"""
Repository for managing antibody sequences and related entities in the database.
"""

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.domain.entities import (
    AntibodySequence,
    AntibodyChain,
    AntibodyDomain,
    AntibodyRegion,
    AntibodyFeature,
)
from backend.domain.value_objects import (
    AminoAcidSequence,
    ConfidenceScore,
    AnnotationMetadata,
    RegionBoundary,
)
from backend.domain.models import (
    ChainType,
    DomainType,
    NumberingScheme,
    RegionType,
    FeatureType,
)
from backend.database.models import (
    AntibodySequence as AntibodySequenceModel,
    AntibodyChain as AntibodyChainModel,
    AntibodyDomain as AntibodyDomainModel,
    AntibodyRegion as AntibodyRegionModel,
    AntibodyFeature as AntibodyFeatureModel,
    ChainType as ChainTypeModel,
    DomainType as DomainTypeModel,
    NumberingScheme as NumberingSchemeModel,
    RegionType as RegionTypeModel,
    FeatureType as FeatureTypeModel,
)
from backend.core.interfaces import Repository
from backend.logger import logger


class AntibodyRepository(Repository[AntibodySequence]):
    """Repository for antibody sequence entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, entity: AntibodySequence) -> AntibodySequence:
        """Save an antibody sequence and all its related entities."""
        try:
            # Check if sequence already exists
            existing = await self.find_by_name(entity.name)
            if existing:
                logger.info(
                    f"Updating existing antibody sequence: {entity.name}"
                )
                return await self._update_sequence(existing, entity)
            else:
                logger.info(f"Creating new antibody sequence: {entity.name}")
                return await self._create_sequence(entity)
        except Exception as e:
            logger.error(f"Error saving antibody sequence {entity.name}: {e}")
            raise

    async def find_by_id(self, entity_id: str) -> Optional[AntibodySequence]:
        """Find antibody sequence by ID."""
        try:
            stmt = (
                select(AntibodySequenceModel)
                .options(
                    selectinload(AntibodySequenceModel.chains)
                    .selectinload(AntibodyChainModel.domains)
                    .selectinload(AntibodyDomainModel.regions),
                    selectinload(AntibodySequenceModel.chains).selectinload(
                        AntibodyChainModel.features
                    ),
                )
                .where(AntibodySequenceModel.id == uuid.UUID(entity_id))
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return await self._model_to_entity(model)
            return None
        except Exception as e:
            logger.error(
                f"Error finding antibody sequence by ID {entity_id}: {e}"
            )
            raise

    async def find_by_name(self, name: str) -> Optional[AntibodySequence]:
        """Find antibody sequence by name."""
        try:
            stmt = (
                select(AntibodySequenceModel)
                .options(
                    selectinload(AntibodySequenceModel.chains)
                    .selectinload(AntibodyChainModel.domains)
                    .selectinload(AntibodyDomainModel.regions),
                    selectinload(AntibodySequenceModel.chains).selectinload(
                        AntibodyChainModel.features
                    ),
                )
                .where(AntibodySequenceModel.name == name)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return await self._model_to_entity(model)
            return None
        except Exception as e:
            logger.error(
                f"Error finding antibody sequence by name {name}: {e}"
            )
            raise

    async def find_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[AntibodySequence]:
        """Find all antibody sequences with optional pagination."""
        try:
            stmt = select(AntibodySequenceModel).options(
                selectinload(AntibodySequenceModel.chains)
                .selectinload(AntibodyChainModel.domains)
                .selectinload(AntibodyDomainModel.regions),
                selectinload(AntibodySequenceModel.chains).selectinload(
                    AntibodyChainModel.features
                ),
            )

            if offset:
                stmt = stmt.offset(offset)
            if limit:
                stmt = stmt.limit(limit)

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            entities = []
            for model in models:
                entity = await self._model_to_entity(model)
                entities.append(entity)

            return entities
        except Exception as e:
            logger.error(f"Error finding all antibody sequences: {e}")
            raise

    async def find_by_chain_type(
        self, chain_type: ChainType
    ) -> List[AntibodySequence]:
        """Find antibody sequences by chain type."""
        try:
            # Get chain type ID
            chain_type_id = await self._get_chain_type_id(chain_type.value)

            stmt = (
                select(AntibodySequenceModel)
                .join(AntibodyChainModel)
                .options(
                    selectinload(AntibodySequenceModel.chains)
                    .selectinload(AntibodyChainModel.domains)
                    .selectinload(AntibodyDomainModel.regions),
                    selectinload(AntibodySequenceModel.chains).selectinload(
                        AntibodyChainModel.features
                    ),
                )
                .where(AntibodyChainModel.chain_type_id == chain_type_id)
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            entities = []
            for model in models:
                entity = await self._model_to_entity(model)
                entities.append(entity)

            return entities
        except Exception as e:
            logger.error(
                f"Error finding antibody sequences by chain type {chain_type}: {e}"
            )
            raise

    async def delete(self, entity_id: str) -> bool:
        """Delete an antibody sequence by ID."""
        try:
            stmt = select(AntibodySequenceModel).where(
                AntibodySequenceModel.id == uuid.UUID(entity_id)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                await self.session.delete(model)
                await self.session.commit()
                logger.info(f"Deleted antibody sequence: {entity_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting antibody sequence {entity_id}: {e}")
            raise

    async def count(self) -> int:
        """Count total antibody sequences."""
        try:
            stmt = select(AntibodySequenceModel)
            result = await self.session.execute(stmt)
            return len(result.scalars().all())
        except Exception as e:
            logger.error(f"Error counting antibody sequences: {e}")
            raise

    async def _create_sequence(
        self, entity: AntibodySequence
    ) -> AntibodySequence:
        """Create a new antibody sequence in the database."""
        # Create sequence model
        sequence_model = AntibodySequenceModel(
            name=entity.name,
            sequence=entity.sequence.value if entity.sequence else None,
            sequence_type="AMINO_ACID",
            length=len(entity.sequence.value) if entity.sequence else 0,
            description=(
                entity.metadata.description if entity.metadata else None
            ),
            source=entity.metadata.source if entity.metadata else None,
            is_valid=True,
        )

        self.session.add(sequence_model)
        await self.session.flush()  # Get the ID

        # Create chains
        for chain in entity.chains:
            chain_model = await self._create_chain_model(
                chain, sequence_model.id
            )
            self.session.add(chain_model)

        await self.session.commit()

        # Return the created entity
        return await self._model_to_entity(sequence_model)

    async def _update_sequence(
        self, existing: AntibodySequence, updated: AntibodySequence
    ) -> AntibodySequence:
        """Update an existing antibody sequence."""
        # For now, we'll delete and recreate to handle complex relationships
        # In a production system, you'd want more sophisticated update logic
        existing_id = existing.id
        await self.delete(existing_id)
        return await self._create_sequence(updated)

    async def _create_chain_model(
        self, chain: AntibodyChain, sequence_id: uuid.UUID
    ) -> AntibodyChainModel:
        """Create a chain model from domain entity."""
        # Get lookup IDs
        chain_type_id = await self._get_chain_type_id(chain.chain_type.value)
        numbering_scheme_id = await self._get_numbering_scheme_id(
            chain.numbering_scheme.value
        )

        chain_model = AntibodyChainModel(
            sequence_id=sequence_id,
            chain_type_id=chain_type_id,
            numbering_scheme_id=numbering_scheme_id,
            chain_identifier=chain.name,
            sequence=chain.sequence.value if chain.sequence else None,
            length=len(chain.sequence.value) if chain.sequence else 0,
        )

        # Create domains
        for domain in chain.domains:
            domain_model = await self._create_domain_model(
                domain, chain_model.id
            )
            self.session.add(domain_model)

        # Create features
        for feature in chain.features:
            feature_model = await self._create_feature_model(
                feature, chain_model.id
            )
            self.session.add(feature_model)

        return chain_model

    async def _create_domain_model(
        self, domain: AntibodyDomain, chain_id: uuid.UUID
    ) -> AntibodyDomainModel:
        """Create a domain model from domain entity."""
        domain_type_id = await self._get_domain_type_id(
            domain.domain_type.value
        )

        domain_model = AntibodyDomainModel(
            chain_id=chain_id,
            domain_type_id=domain_type_id,
            sequence=domain.sequence.value if domain.sequence else None,
            start_position=domain.boundary.start if domain.boundary else None,
            end_position=domain.boundary.end if domain.boundary else None,
            confidence_score=(
                domain.confidence_score.value
                if domain.confidence_score
                else None
            ),
        )

        # Create regions
        for region in domain.regions:
            region_model = await self._create_region_model(
                region, domain_model.id
            )
            self.session.add(region_model)

        return domain_model

    async def _create_region_model(
        self, region: AntibodyRegion, domain_id: uuid.UUID
    ) -> AntibodyRegionModel:
        """Create a region model from domain entity."""
        region_type_id = await self._get_region_type_id(
            region.region_type.value
        )

        return AntibodyRegionModel(
            domain_id=domain_id,
            region_type_id=region_type_id,
            start_position=region.boundary.start if region.boundary else None,
            end_position=region.boundary.end if region.boundary else None,
            sequence=region.sequence.value if region.sequence else None,
            confidence_score=(
                region.confidence_score.value
                if region.confidence_score
                else None
            ),
        )

    async def _create_feature_model(
        self, feature: AntibodyFeature, chain_id: uuid.UUID
    ) -> AntibodyFeatureModel:
        """Create a feature model from domain entity."""
        feature_type_id = await self._get_feature_type_id(
            feature.feature_type.value
        )

        return AntibodyFeatureModel(
            chain_id=chain_id,
            feature_type_id=feature_type_id,
            name=feature.name,
            value=feature.value,
            start_position=(
                feature.boundary.start if feature.boundary else None
            ),
            end_position=feature.boundary.end if feature.boundary else None,
            confidence_score=(
                feature.confidence_score.value
                if feature.confidence_score
                else None
            ),
        )

    async def _model_to_entity(
        self, model: AntibodySequenceModel
    ) -> AntibodySequence:
        """Convert database model to domain entity."""
        # Convert chains
        chains = []
        for chain_model in model.chains:
            chain = await self._chain_model_to_entity(chain_model)
            chains.append(chain)

        # Create sequence entity
        sequence = AntibodySequence(
            name=model.name,
            sequence=(
                AminoAcidSequence(model.sequence) if model.sequence else None
            ),
            chains=chains,
            metadata=(
                AnnotationMetadata(
                    description=model.description,
                    source=model.source,
                    confidence_score=ConfidenceScore(
                        1.0
                    ),  # Default confidence
                )
                if model.description or model.source
                else None
            ),
        )

        return sequence

    async def _chain_model_to_entity(
        self, model: AntibodyChainModel
    ) -> AntibodyChain:
        """Convert chain model to domain entity."""
        # Convert domains
        domains = []
        for domain_model in model.domains:
            domain = await self._domain_model_to_entity(domain_model)
            domains.append(domain)

        # Convert features
        features = []
        for feature_model in model.features:
            feature = await self._feature_model_to_entity(feature_model)
            features.append(feature)

        # Get lookup values
        chain_type = await self._get_chain_type_by_id(model.chain_type_id)
        numbering_scheme = await self._get_numbering_scheme_by_id(
            model.numbering_scheme_id
        )

        return AntibodyChain(
            name=model.chain_identifier,
            chain_type=ChainType(chain_type),
            numbering_scheme=NumberingScheme(numbering_scheme),
            sequence=(
                AminoAcidSequence(model.sequence) if model.sequence else None
            ),
            domains=domains,
            features=features,
        )

    async def _domain_model_to_entity(
        self, model: AntibodyDomainModel
    ) -> AntibodyDomain:
        """Convert domain model to domain entity."""
        # Convert regions
        regions = []
        for region_model in model.regions:
            region = await self._region_model_to_entity(region_model)
            regions.append(region)

        # Get lookup values
        domain_type = await self._get_domain_type_by_id(model.domain_type_id)

        return AntibodyDomain(
            domain_type=DomainType(domain_type),
            sequence=(
                AminoAcidSequence(model.sequence) if model.sequence else None
            ),
            boundary=(
                RegionBoundary(model.start_position, model.end_position)
                if model.start_position and model.end_position
                else None
            ),
            regions=regions,
            confidence_score=(
                ConfidenceScore(model.confidence_score)
                if model.confidence_score
                else None
            ),
        )

    async def _region_model_to_entity(
        self, model: AntibodyRegionModel
    ) -> AntibodyRegion:
        """Convert region model to domain entity."""
        region_type = await self._get_region_type_by_id(model.region_type_id)

        return AntibodyRegion(
            region_type=RegionType(region_type),
            sequence=(
                AminoAcidSequence(model.sequence) if model.sequence else None
            ),
            boundary=(
                RegionBoundary(model.start_position, model.end_position)
                if model.start_position and model.end_position
                else None
            ),
            confidence_score=(
                ConfidenceScore(model.confidence_score)
                if model.confidence_score
                else None
            ),
        )

    async def _feature_model_to_entity(
        self, model: AntibodyFeatureModel
    ) -> AntibodyFeature:
        """Convert feature model to domain entity."""
        feature_type = await self._get_feature_type_by_id(
            model.feature_type_id
        )

        return AntibodyFeature(
            feature_type=FeatureType(feature_type),
            name=model.name,
            value=model.value,
            boundary=(
                RegionBoundary(model.start_position, model.end_position)
                if model.start_position and model.end_position
                else None
            ),
            confidence_score=(
                ConfidenceScore(model.confidence_score)
                if model.confidence_score
                else None
            ),
        )

    # Helper methods for lookup tables
    async def _get_chain_type_id(self, code: str) -> uuid.UUID:
        """Get chain type ID by code."""
        stmt = select(ChainTypeModel.id).where(ChainTypeModel.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def _get_domain_type_id(self, code: str) -> uuid.UUID:
        """Get domain type ID by code."""
        stmt = select(DomainTypeModel.id).where(DomainTypeModel.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def _get_numbering_scheme_id(self, code: str) -> uuid.UUID:
        """Get numbering scheme ID by code."""
        stmt = select(NumberingSchemeModel.id).where(
            NumberingSchemeModel.code == code
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def _get_region_type_id(self, code: str) -> uuid.UUID:
        """Get region type ID by code."""
        stmt = select(RegionTypeModel.id).where(RegionTypeModel.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def _get_feature_type_id(self, code: str) -> uuid.UUID:
        """Get feature type ID by code."""
        stmt = select(FeatureTypeModel.id).where(FeatureTypeModel.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def _get_chain_type_by_id(self, id: uuid.UUID) -> str:
        """Get chain type code by ID."""
        stmt = select(ChainTypeModel.code).where(ChainTypeModel.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def _get_domain_type_by_id(self, id: uuid.UUID) -> str:
        """Get domain type code by ID."""
        stmt = select(DomainTypeModel.code).where(DomainTypeModel.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def _get_numbering_scheme_by_id(self, id: uuid.UUID) -> str:
        """Get numbering scheme code by ID."""
        stmt = select(NumberingSchemeModel.code).where(
            NumberingSchemeModel.id == id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def _get_region_type_by_id(self, id: uuid.UUID) -> str:
        """Get region type code by ID."""
        stmt = select(RegionTypeModel.code).where(RegionTypeModel.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def _get_feature_type_by_id(self, id: uuid.UUID) -> str:
        """Get feature type code by ID."""
        stmt = select(FeatureTypeModel.code).where(FeatureTypeModel.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

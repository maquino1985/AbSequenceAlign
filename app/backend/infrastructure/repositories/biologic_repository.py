"""
Repository for managing biologic entities and related sequences in the database.
"""

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.domain.entities_v2 import (
    Biologic,
    BiologicChain,
    SequenceDomain,
    SequenceRegion,
    DomainFeature,
)
from backend.domain.value_objects_v2 import (
    DNASequence,
    RNASequence,
    AminoAcidSequence,
    SequenceType,
    ConfidenceScore,
    RegionBoundary,
    BiologicAlias,
)
from backend.domain.models import (
    ChainType,
    DomainType,
    NumberingScheme,
    RegionType,
    FeatureType,
)
from backend.database.models_v2 import (
    Biologic as BiologicModel,
    BiologicAlias as BiologicAliasModel,
    BiologicChain as BiologicChainModel,
    SequenceDomain as SequenceDomainModel,
    SequenceRegion as SequenceRegionModel,
    DomainFeature as DomainFeatureModel,
    DNASequence as DNASequenceModel,
    RNASequence as RNASequenceModel,
    ProteinSequence as ProteinSequenceModel,
    ChainType as ChainTypeModel,
    DomainType as DomainTypeModel,
    NumberingScheme as NumberingSchemeModel,
    RegionType as RegionTypeModel,
    FeatureType as FeatureTypeModel,
    SequenceType as SequenceTypeModel,
)
from backend.core.interfaces import Repository
from backend.logger import logger


class BiologicRepository(Repository[Biologic]):
    """Repository for biologic entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, entity: Biologic) -> Biologic:
        """Save a biologic and all its related entities."""
        try:
            # Check if biologic already exists
            existing = await self.find_by_name(entity.name)
            if existing:
                logger.info(f"Updating existing biologic: {entity.name}")
                return await self._update_biologic(existing, entity)
            else:
                logger.info(f"Creating new biologic: {entity.name}")
                return await self._create_biologic(entity)
        except Exception as e:
            logger.error(f"Error saving biologic {entity.name}: {e}")
            raise

    async def find_by_id(self, entity_id: str) -> Optional[Biologic]:
        """Find biologic by ID."""
        try:
            stmt = (
                select(BiologicModel)
                .options(
                    selectinload(BiologicModel.aliases),
                    selectinload(BiologicModel.chains)
                    .selectinload(BiologicChainModel.sequence_domains)
                    .selectinload(SequenceDomainModel.sequence_regions),
                    selectinload(BiologicModel.chains).selectinload(
                        BiologicChainModel.domain_features
                    ),
                    selectinload(BiologicModel.dna_sequences),
                    selectinload(BiologicModel.rna_sequences),
                    selectinload(BiologicModel.protein_sequences),
                    selectinload(BiologicModel.domain_features),
                )
                .where(BiologicModel.id == uuid.UUID(entity_id))
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return await self._model_to_entity(model)
            return None
        except Exception as e:
            logger.error(f"Error finding biologic by ID {entity_id}: {e}")
            raise

    async def find_by_name(self, name: str) -> Optional[Biologic]:
        """Find biologic by name."""
        try:
            stmt = (
                select(BiologicModel)
                .options(
                    selectinload(BiologicModel.aliases),
                    selectinload(BiologicModel.chains)
                    .selectinload(BiologicChainModel.sequence_domains)
                    .selectinload(SequenceDomainModel.sequence_regions),
                    selectinload(BiologicModel.chains).selectinload(
                        BiologicChainModel.domain_features
                    ),
                    selectinload(BiologicModel.dna_sequences),
                    selectinload(BiologicModel.rna_sequences),
                    selectinload(BiologicModel.protein_sequences),
                    selectinload(BiologicModel.domain_features),
                )
                .where(BiologicModel.name == name)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return await self._model_to_entity(model)
            return None
        except Exception as e:
            logger.error(f"Error finding biologic by name {name}: {e}")
            raise

    async def find_by_alias(self, alias: str) -> Optional[Biologic]:
        """Find biologic by alias."""
        try:
            stmt = (
                select(BiologicModel)
                .join(BiologicAliasModel)
                .options(
                    selectinload(BiologicModel.aliases),
                    selectinload(BiologicModel.chains)
                    .selectinload(BiologicChainModel.sequence_domains)
                    .selectinload(SequenceDomainModel.sequence_regions),
                    selectinload(BiologicModel.chains).selectinload(
                        BiologicChainModel.domain_features
                    ),
                    selectinload(BiologicModel.dna_sequences),
                    selectinload(BiologicModel.rna_sequences),
                    selectinload(BiologicModel.protein_sequences),
                    selectinload(BiologicModel.domain_features),
                )
                .where(BiologicAliasModel.alias == alias)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return await self._model_to_entity(model)
            return None
        except Exception as e:
            logger.error(f"Error finding biologic by alias {alias}: {e}")
            raise

    async def find_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[Biologic]:
        """Find all biologics with optional pagination."""
        try:
            stmt = select(BiologicModel).options(
                selectinload(BiologicModel.aliases),
                selectinload(BiologicModel.chains)
                .selectinload(BiologicChainModel.sequence_domains)
                .selectinload(SequenceDomainModel.sequence_regions),
                selectinload(BiologicModel.chains).selectinload(
                    BiologicChainModel.domain_features
                ),
                selectinload(BiologicModel.dna_sequences),
                selectinload(BiologicModel.rna_sequences),
                selectinload(BiologicModel.protein_sequences),
                selectinload(BiologicModel.domain_features),
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
            logger.error(f"Error finding all biologics: {e}")
            raise

    async def find_by_chain_type(
        self, chain_type: ChainType
    ) -> List[Biologic]:
        """Find biologics by chain type."""
        try:
            # Get chain type ID
            chain_type_id = await self._get_chain_type_id(chain_type.value)

            stmt = (
                select(BiologicModel)
                .join(BiologicChainModel)
                .options(
                    selectinload(BiologicModel.aliases),
                    selectinload(BiologicModel.chains)
                    .selectinload(BiologicChainModel.sequence_domains)
                    .selectinload(SequenceDomainModel.sequence_regions),
                    selectinload(BiologicModel.chains).selectinload(
                        BiologicChainModel.domain_features
                    ),
                    selectinload(BiologicModel.dna_sequences),
                    selectinload(BiologicModel.rna_sequences),
                    selectinload(BiologicModel.protein_sequences),
                    selectinload(BiologicModel.domain_features),
                )
                .where(BiologicChainModel.chain_type_id == chain_type_id)
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
                f"Error finding biologics by chain type {chain_type}: {e}"
            )
            raise

    async def delete(self, entity_id: str) -> bool:
        """Delete a biologic by ID."""
        try:
            stmt = select(BiologicModel).where(
                BiologicModel.id == uuid.UUID(entity_id)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                await self.session.delete(model)
                await self.session.commit()
                logger.info(f"Deleted biologic: {entity_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting biologic {entity_id}: {e}")
            raise

    async def count(self) -> int:
        """Count total biologics."""
        try:
            stmt = select(BiologicModel)
            result = await self.session.execute(stmt)
            return len(result.scalars().all())
        except Exception as e:
            logger.error(f"Error counting biologics: {e}")
            raise

    async def _create_biologic(self, entity: Biologic) -> Biologic:
        """Create a new biologic in the database."""
        # Create biologic model
        biologic_model = BiologicModel(
            name=entity.name,
            description=entity.metadata.get("description"),
            source=entity.metadata.get("source"),
            is_valid=True,
        )

        self.session.add(biologic_model)
        await self.session.flush()  # Get the ID

        # Create aliases
        for alias in entity.aliases:
            alias_model = BiologicAliasModel(
                biologic_id=biologic_model.id,
                alias=alias.alias,
                alias_type=alias.alias_type,
                source=alias.source,
            )
            self.session.add(alias_model)

        # Create sequences
        for dna_seq in entity.dna_sequences:
            dna_model = DNASequenceModel(
                biologic_id=biologic_model.id,
                sequence=dna_seq.sequence,
                length=len(dna_seq.sequence),
            )
            self.session.add(dna_model)

        for rna_seq in entity.rna_sequences:
            rna_model = RNASequenceModel(
                biologic_id=biologic_model.id,
                sequence=rna_seq.sequence,
                length=len(rna_seq.sequence),
            )
            self.session.add(rna_model)

        for protein_seq in entity.protein_sequences:
            protein_model = ProteinSequenceModel(
                biologic_id=biologic_model.id,
                sequence=protein_seq.sequence,
                length=len(protein_seq.sequence),
            )
            self.session.add(protein_model)

        # Create chains
        for chain in entity.chains:
            chain_model = await self._create_chain_model(
                chain, biologic_model.id
            )
            self.session.add(chain_model)

        # Create features
        for feature in entity.features:
            feature_model = await self._create_feature_model(
                feature, biologic_model.id
            )
            self.session.add(feature_model)

        await self.session.commit()

        # Return the created entity
        return await self._model_to_entity(biologic_model)

    async def _update_biologic(
        self, existing: Biologic, updated: Biologic
    ) -> Biologic:
        """Update an existing biologic."""
        # For now, we'll delete and recreate to handle complex relationships
        # In a production system, you'd want more sophisticated update logic
        existing_id = existing.id
        await self.delete(existing_id)
        return await self._create_biologic(updated)

    async def _create_chain_model(
        self, chain: BiologicChain, biologic_id: uuid.UUID
    ) -> BiologicChainModel:
        """Create a chain model from domain entity."""
        # Get lookup IDs
        chain_type_id = await self._get_chain_type_id(chain.chain_type.value)
        numbering_scheme_id = await self._get_numbering_scheme_id(
            chain.numbering_scheme.value
        )
        sequence_type_id = await self._get_sequence_type_id(
            chain.sequence_type.value
        )

        chain_model = BiologicChainModel(
            biologic_id=biologic_id,
            chain_type_id=chain_type_id,
            numbering_scheme_id=numbering_scheme_id,
            sequence_type_id=sequence_type_id,
            chain_identifier=chain.name,
            sequence=str(chain.sequence),
            length=len(chain.sequence),
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
                feature, biologic_id, chain_id=chain_model.id
            )
            self.session.add(feature_model)

        return chain_model

    async def _create_domain_model(
        self, domain: SequenceDomain, chain_id: uuid.UUID
    ) -> SequenceDomainModel:
        """Create a domain model from domain entity."""
        domain_type_id = await self._get_domain_type_id(
            domain.domain_type.value
        )
        sequence_type_id = await self._get_sequence_type_id(
            domain.sequence_type.value
        )

        domain_model = SequenceDomainModel(
            chain_id=chain_id,
            domain_type_id=domain_type_id,
            sequence_type_id=sequence_type_id,
            domain_name=f"{domain.domain_type.value}_{domain.sequence_type.value}",
            sequence=str(domain.sequence),
            start_position=0,  # This would need to be calculated based on position in chain
            end_position=len(domain.sequence) - 1,
            length=len(domain.sequence),
        )

        # Create regions
        for region in domain.regions.values():
            region_model = await self._create_region_model(
                region, chain_id, domain_model.id
            )
            self.session.add(region_model)

        return domain_model

    async def _create_region_model(
        self, region: SequenceRegion, chain_id: uuid.UUID, domain_id: uuid.UUID
    ) -> SequenceRegionModel:
        """Create a region model from domain entity."""
        region_type_id = await self._get_region_type_id(
            region.region_type.value
        )
        numbering_scheme_id = await self._get_numbering_scheme_id(
            region.numbering_scheme.value
        )

        return SequenceRegionModel(
            chain_id=chain_id,
            domain_id=domain_id,
            region_type_id=region_type_id,
            numbering_scheme_id=numbering_scheme_id,
            sequence=str(region.sequence),
            start_position=region.boundary.start,
            end_position=region.boundary.end,
            length=region.boundary.length(),
        )

    async def _create_feature_model(
        self,
        feature: DomainFeature,
        biologic_id: uuid.UUID,
        chain_id: Optional[uuid.UUID] = None,
        domain_id: Optional[uuid.UUID] = None,
        region_id: Optional[uuid.UUID] = None,
    ) -> DomainFeatureModel:
        """Create a feature model from domain entity."""
        feature_type_id = await self._get_feature_type_id(
            feature.feature_type.value
        )

        return DomainFeatureModel(
            biologic_id=biologic_id,
            chain_id=chain_id,
            domain_id=domain_id,
            region_id=region_id,
            feature_type_id=feature_type_id,
            feature_name=feature.name,
            description=feature.value,
            start_position=(
                feature.boundary.start if feature.boundary else None
            ),
            end_position=feature.boundary.end if feature.boundary else None,
            confidence_score=(
                feature.confidence_score.score
                if feature.confidence_score
                else None
            ),
        )

    async def _model_to_entity(self, model: BiologicModel) -> Biologic:
        """Convert database model to domain entity."""
        # Convert aliases
        aliases = []
        for alias_model in model.aliases:
            alias = BiologicAlias(
                alias=alias_model.alias,
                alias_type=alias_model.alias_type,
                source=alias_model.source,
            )
            aliases.append(alias)

        # Convert sequences
        dna_sequences = []
        for dna_model in model.dna_sequences:
            dna_sequences.append(DNASequence(dna_model.sequence))

        rna_sequences = []
        for rna_model in model.rna_sequences:
            rna_sequences.append(RNASequence(rna_model.sequence))

        protein_sequences = []
        for protein_model in model.protein_sequences:
            protein_sequences.append(AminoAcidSequence(protein_model.sequence))

        # Convert chains
        chains = []
        for chain_model in model.chains:
            chain = await self._chain_model_to_entity(chain_model)
            chains.append(chain)

        # Convert features
        features = []
        for feature_model in model.domain_features:
            feature = await self._feature_model_to_entity(feature_model)
            features.append(feature)

        # Create biologic entity
        biologic = Biologic(
            name=model.name,
            aliases=aliases,
            chains=chains,
            dna_sequences=dna_sequences,
            rna_sequences=rna_sequences,
            protein_sequences=protein_sequences,
            features=features,
            metadata={
                "description": model.description,
                "source": model.source,
            },
        )

        return biologic

    async def _chain_model_to_entity(
        self, model: BiologicChainModel
    ) -> BiologicChain:
        """Convert chain model to domain entity."""
        # Convert domains
        domains = []
        for domain_model in model.sequence_domains:
            domain = await self._domain_model_to_entity(domain_model)
            domains.append(domain)

        # Convert features
        features = []
        for feature_model in model.domain_features:
            feature = await self._feature_model_to_entity(feature_model)
            features.append(feature)

        # Get lookup values
        chain_type = await self._get_chain_type_by_id(model.chain_type_id)
        numbering_scheme = await self._get_numbering_scheme_by_id(
            model.numbering_scheme_id
        )
        sequence_type = await self._get_sequence_type_by_id(
            model.sequence_type_id
        )

        # Determine sequence type and create appropriate sequence object
        if sequence_type == "DNA":
            sequence = DNASequence(model.sequence)
        elif sequence_type == "RNA":
            sequence = RNASequence(model.sequence)
        else:  # PROTEIN
            sequence = AminoAcidSequence(model.sequence)

        return BiologicChain(
            name=model.chain_identifier,
            chain_type=ChainType(chain_type),
            sequence=sequence,
            sequence_type=SequenceType(sequence_type),
            numbering_scheme=NumberingScheme(numbering_scheme),
            domains=domains,
            features=features,
        )

    async def _domain_model_to_entity(
        self, model: SequenceDomainModel
    ) -> SequenceDomain:
        """Convert domain model to domain entity."""
        # Convert regions
        regions = {}
        for region_model in model.sequence_regions:
            region = await self._region_model_to_entity(region_model)
            regions[region.name] = region

        # Get lookup values
        domain_type = await self._get_domain_type_by_id(model.domain_type_id)
        sequence_type = await self._get_sequence_type_by_id(
            model.sequence_type_id
        )
        numbering_scheme = await self._get_numbering_scheme_by_id(
            model.numbering_scheme_id
        )

        # Determine sequence type and create appropriate sequence object
        if sequence_type == "DNA":
            sequence = DNASequence(model.sequence)
        elif sequence_type == "RNA":
            sequence = RNASequence(model.sequence)
        else:  # PROTEIN
            sequence = AminoAcidSequence(model.sequence)

        return SequenceDomain(
            domain_type=DomainType(domain_type),
            sequence=sequence,
            sequence_type=SequenceType(sequence_type),
            numbering_scheme=NumberingScheme(numbering_scheme),
            regions=regions,
        )

    async def _region_model_to_entity(
        self, model: SequenceRegionModel
    ) -> SequenceRegion:
        """Convert region model to domain entity."""
        region_type = await self._get_region_type_by_id(model.region_type_id)
        numbering_scheme = await self._get_numbering_scheme_by_id(
            model.numbering_scheme_id
        )

        # For now, we'll assume protein sequences for regions
        # In a full implementation, you'd need to determine the sequence type
        sequence = AminoAcidSequence(model.sequence)

        return SequenceRegion(
            name=f"{region_type}_{model.start_position}_{model.end_position}",
            region_type=RegionType(region_type),
            sequence=sequence,
            numbering_scheme=NumberingScheme(numbering_scheme),
            boundary=RegionBoundary(model.start_position, model.end_position),
        )

    async def _feature_model_to_entity(
        self, model: DomainFeatureModel
    ) -> DomainFeature:
        """Convert feature model to domain entity."""
        feature_type = await self._get_feature_type_by_id(
            model.feature_type_id
        )

        return DomainFeature(
            feature_type=FeatureType(feature_type),
            name=model.feature_name,
            value=model.description or "",
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
    async def _get_sequence_type_id(self, code: str) -> uuid.UUID:
        """Get sequence type ID by code."""
        stmt = select(SequenceTypeModel.id).where(
            SequenceTypeModel.code == code
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

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

    async def _get_sequence_type_by_id(self, id: uuid.UUID) -> str:
        """Get sequence type code by ID."""
        stmt = select(SequenceTypeModel.code).where(SequenceTypeModel.id == id)
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

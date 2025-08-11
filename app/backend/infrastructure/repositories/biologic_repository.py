"""
Repository for managing biologic entities in the database.
Implements the Repository pattern with async operations.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

    Chain,
    Sequence,
    ChainSequence,
    SequenceDomain,
    DomainFeature,
)
from backend.core.interfaces import BiologicRepository


class BiologicRepositoryImpl(BiologicRepository[Biologic]):
    """Concrete repository implementation for biologic entities."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger = logger

    async def save(self, entity: Biologic) -> Biologic:
        """Save a biologic entity."""
        try:
            self._logger.info(f"Saving biologic entity: {entity.name}")

            if entity.id is None:
                # New entity
                self.session.add(entity)
                self._logger.debug(f"Added new biologic entity: {entity.name}")
            else:
                # Existing entity - merge
                entity = await self.session.merge(entity)
                self._logger.debug(
                    f"Merged existing biologic entity: {entity.name}"
                )

            await self.session.commit()
            await self.session.refresh(entity)

            self._logger.info(
                f"Successfully saved biologic entity: {entity.name} (ID: {entity.id})"
            )
            return entity

        except Exception as e:
            await self.session.rollback()
            self._logger.error(
                f"Error saving biologic entity {entity.name}: {e}"
            )
            raise

    async def find_by_id(self, entity_id: str) -> Optional[Biologic]:
        """Find biologic entity by ID."""
        try:
            stmt = select(Biologic).where(Biologic.id == uuid.UUID(entity_id))
            result = await self.session.execute(stmt)
            biologic = result.scalar_one_or_none()

            if biologic:
                self._logger.debug(f"Found biologic entity by ID: {entity_id}")
            else:
                self._logger.debug(
                    f"No biologic entity found with ID: {entity_id}"
                )

            return biologic

        except Exception as e:
            self._logger.error(
                f"Error finding biologic entity by ID {entity_id}: {e}"
            )
            raise

    async def find_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[Biologic]:
        """Find all biologic entities with optional pagination."""
        try:
            stmt = select(Biologic)

            if offset:
                stmt = stmt.offset(offset)
            if limit:
                stmt = stmt.limit(limit)

            result = await self.session.execute(stmt)
            biologics = result.scalars().all()

            self._logger.debug(f"Found {len(biologics)} biologic entities")
            return list(biologics)

        except Exception as e:
            self._logger.error(f"Error finding all biologic entities: {e}")
            raise

    async def delete(self, entity_id: str) -> bool:
        """Delete a biologic entity by ID."""
        try:
            biologic = await self.find_by_id(entity_id)
            if not biologic:
                self._logger.warning(
                    f"Cannot delete: biologic entity not found with ID: {entity_id}"
                )
                return False

            await self.session.delete(biologic)
            await self.session.commit()

            self._logger.info(
                f"Successfully deleted biologic entity: {biologic.name} (ID: {entity_id})"
            )
            return True

        except Exception as e:
            await self.session.rollback()
            self._logger.error(
                f"Error deleting biologic entity {entity_id}: {e}"
            )
            raise

    async def count(self) -> int:
        """Count total biologic entities."""
        try:
            stmt = select(Biologic)
            result = await self.session.execute(stmt)
            count = len(result.scalars().all())

            self._logger.debug(f"Total biologic entities count: {count}")
            return count

        except Exception as e:
            self._logger.error(f"Error counting biologic entities: {e}")
            raise

    async def exists(self, entity_id: str) -> bool:
        """Check if a biologic entity exists."""
        try:
            biologic = await self.find_by_id(entity_id)
            exists = biologic is not None

            self._logger.debug(
                f"Biologic entity exists check for ID {entity_id}: {exists}"
            )
            return exists

        except Exception as e:
            self._logger.error(
                f"Error checking existence of biologic entity {entity_id}: {e}"
            )
            raise

    async def find_by_organism(
        self, organism: str, limit: Optional[int] = None
    ) -> List[Biologic]:
        """Find biologics by organism."""
        try:
            stmt = select(Biologic).where(Biologic.organism == organism)

            if limit:
                stmt = stmt.limit(limit)

            result = await self.session.execute(stmt)
            biologics = result.scalars().all()

            self._logger.debug(
                f"Found {len(biologics)} biologic entities for organism: {organism}"
            )
            return list(biologics)

        except Exception as e:
            self._logger.error(
                f"Error finding biologic entities by organism {organism}: {e}"
            )
            raise

    async def find_by_type(
        self, biologic_type: str, limit: Optional[int] = None
    ) -> List[Biologic]:
        """Find biologics by type."""
        try:
            stmt = select(Biologic).where(
                Biologic.biologic_type == biologic_type
            )

            if limit:
                stmt = stmt.limit(limit)

            result = await self.session.execute(stmt)
            biologics = result.scalars().all()

            self._logger.debug(
                f"Found {len(biologics)} biologic entities for type: {biologic_type}"
            )
            return list(biologics)

        except Exception as e:
            self._logger.error(
                f"Error finding biologic entities by type {biologic_type}: {e}"
            )
            raise

    async def find_by_name_pattern(
        self, name_pattern: str, limit: Optional[int] = None
    ) -> List[Biologic]:
        """Find biologics by name pattern."""
        try:
            stmt = select(Biologic).where(
                Biologic.name.ilike(f"%{name_pattern}%")
            )

            if limit:
                stmt = stmt.limit(limit)

            result = await self.session.execute(stmt)
            biologics = result.scalars().all()

            self._logger.debug(
                f"Found {len(biologics)} biologic entities matching pattern: {name_pattern}"
            )
            return list(biologics)

        except Exception as e:
            self._logger.error(
                f"Error finding biologic entities by name pattern {name_pattern}: {e}"
            )
            raise

    async def find_with_chains(self, entity_id: str) -> Optional[Biologic]:
        """Find biologic with all its chains loaded."""
        try:
            stmt = (
                select(Biologic)
                .options(selectinload(Biologic.chains))
                .where(Biologic.id == uuid.UUID(entity_id))
            )
            result = await self.session.execute(stmt)
            biologic = result.scalar_one_or_none()

            if biologic:
                self._logger.debug(
                    f"Found biologic entity with chains: {entity_id}"
                )
            else:
                self._logger.debug(
                    f"No biologic entity found with chains for ID: {entity_id}"
                )

            return biologic

        except Exception as e:
            self._logger.error(
                f"Error finding biologic entity with chains for ID {entity_id}: {e}"
            )
            raise

    async def find_with_full_hierarchy(
        self, entity_id: str
    ) -> Optional[Biologic]:
        """Find biologic with full hierarchy (chains, sequences, domains, features)."""
        try:
            stmt = (
                select(Biologic)
                .options(
                    selectinload(Biologic.aliases),
                    selectinload(Biologic.chains)
                    .selectinload(Chain.sequences)
                    .selectinload(ChainSequence.domains)
                    .selectinload(SequenceDomain.features),
                )
                .where(Biologic.id == uuid.UUID(entity_id))
            )
            result = await self.session.execute(stmt)
            biologic = result.scalar_one_or_none()

            if biologic:
                self._logger.debug(
                    f"Found biologic entity with full hierarchy: {entity_id}"
                )
            else:
                self._logger.debug(
                    f"No biologic entity found with full hierarchy for ID: {entity_id}"
                )

            return biologic

        except Exception as e:
            self._logger.error(
                f"Error finding biologic entity with full hierarchy for ID {entity_id}: {e}"
            )
            raise

    async def search_biologics(
        self, search_criteria: Dict[str, Any], limit: Optional[int] = None
    ) -> List[Biologic]:
        """Search biologics by multiple criteria."""
        try:
            stmt = select(Biologic)
            conditions = []

            # Build search conditions
            if "name" in search_criteria:
                conditions.append(
                    Biologic.name.ilike(f"%{search_criteria['name']}%")
                )

            if "organism" in search_criteria:
                conditions.append(
                    Biologic.organism == search_criteria["organism"]
                )

            if "biologic_type" in search_criteria:
                conditions.append(
                    Biologic.biologic_type == search_criteria["biologic_type"]
                )

            if "description" in search_criteria:
                conditions.append(
                    Biologic.description.ilike(
                        f"%{search_criteria['description']}%"
                    )
                )

            # Apply conditions
            if conditions:
                stmt = stmt.where(and_(*conditions))

            # Apply pagination
            if limit:
                stmt = stmt.limit(limit)

            result = await self.session.execute(stmt)
            biologics = result.scalars().all()

            self._logger.debug(
                f"Found {len(biologics)} biologic entities matching search criteria: {search_criteria}"
            )
            return list(biologics)

        except Exception as e:
            self._logger.error(
                f"Error searching biologic entities with criteria {search_criteria}: {e}"
            )
            raise

    async def find_by_metadata_key(
        self, key: str, value: Any, limit: Optional[int] = None
    ) -> List[Biologic]:
        """Find biologics by metadata key-value pair."""
        try:
            stmt = select(Biologic).where(
                Biologic.metadata_json.contains({key: value})
            )

            if limit:
                stmt = stmt.limit(limit)

            result = await self.session.execute(stmt)
            biologics = result.scalars().all()

            self._logger.debug(
                f"Found {len(biologics)} biologic entities with metadata {key}={value}"
            )
            return list(biologics)

        except Exception as e:
            self._logger.error(
                f"Error finding biologic entities by metadata {key}={value}: {e}"
            )
            raise

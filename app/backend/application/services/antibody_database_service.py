"""
Database service for managing antibody sequences and their persistence.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from backend.domain.entities import AntibodySequence
from backend.domain.models import ChainType
from backend.infrastructure.repositories.antibody_repository import (
    AntibodyRepository,
)
from backend.core.interfaces import ProcessingResult
from backend.core.exceptions import ValidationError
from backend.logger import logger


class AntibodyDatabaseService:
    """Service for managing antibody sequence persistence."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = AntibodyRepository(session)

    async def save_antibody_sequence(
        self,
        antibody_sequence: AntibodySequence,
        persist_metadata: bool = True,
    ) -> ProcessingResult:
        """Save an antibody sequence and all its related entities to the database."""
        try:
            logger.info(
                f"Saving antibody sequence to database: {antibody_sequence.name}"
            )

            # Validate the sequence before saving
            if not self._validate_antibody_sequence(antibody_sequence):
                raise ValidationError(
                    "Invalid antibody sequence for database persistence"
                )

            # Save the sequence using the repository
            saved_sequence = await self.repository.save(antibody_sequence)

            logger.info(
                f"Successfully saved antibody sequence: {saved_sequence.name}"
            )

            return ProcessingResult(
                success=True,
                data={"saved_sequence": saved_sequence},
                metadata={
                    "sequence_name": saved_sequence.name,
                    "chains_count": len(saved_sequence.chains),
                    "total_domains": sum(
                        len(chain.domains) for chain in saved_sequence.chains
                    ),
                    "total_regions": sum(
                        len(domain.regions)
                        for chain in saved_sequence.chains
                        for domain in chain.domains
                    ),
                },
            )

        except SQLAlchemyError as e:
            error_msg = f"Database error saving antibody sequence {antibody_sequence.name}: {str(e)}"
            logger.error(error_msg)
            await self.session.rollback()
            return ProcessingResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Error saving antibody sequence {antibody_sequence.name}: {str(e)}"
            logger.error(error_msg)
            await self.session.rollback()
            return ProcessingResult(success=False, error=error_msg)

    async def find_antibody_sequence_by_name(
        self, name: str
    ) -> ProcessingResult:
        """Find an antibody sequence by name."""
        try:
            logger.info(f"Looking up antibody sequence by name: {name}")

            sequence = await self.repository.find_by_name(name)

            if sequence:
                logger.info(f"Found antibody sequence: {name}")
                return ProcessingResult(
                    success=True,
                    data={"antibody_sequence": sequence},
                    metadata={"sequence_name": name},
                )
            else:
                logger.info(f"Antibody sequence not found: {name}")
                return ProcessingResult(
                    success=False, error=f"Antibody sequence not found: {name}"
                )

        except Exception as e:
            error_msg = f"Error finding antibody sequence {name}: {str(e)}"
            logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    async def find_antibody_sequence_by_id(
        self, sequence_id: str
    ) -> ProcessingResult:
        """Find an antibody sequence by ID."""
        try:
            logger.info(f"Looking up antibody sequence by ID: {sequence_id}")

            sequence = await self.repository.find_by_id(sequence_id)

            if sequence:
                logger.info(f"Found antibody sequence: {sequence.name}")
                return ProcessingResult(
                    success=True,
                    data={"antibody_sequence": sequence},
                    metadata={
                        "sequence_id": sequence_id,
                        "sequence_name": sequence.name,
                    },
                )
            else:
                logger.info(f"Antibody sequence not found: {sequence_id}")
                return ProcessingResult(
                    success=False,
                    error=f"Antibody sequence not found: {sequence_id}",
                )

        except Exception as e:
            error_msg = (
                f"Error finding antibody sequence {sequence_id}: {str(e)}"
            )
            logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    async def find_antibody_sequences_by_chain_type(
        self,
        chain_type: ChainType,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> ProcessingResult:
        """Find antibody sequences by chain type."""
        try:
            logger.info(
                f"Looking up antibody sequences by chain type: {chain_type.value}"
            )

            sequences = await self.repository.find_by_chain_type(chain_type)

            # Apply pagination if specified
            if offset is not None:
                sequences = sequences[offset:]
            if limit is not None:
                sequences = sequences[:limit]

            logger.info(
                f"Found {len(sequences)} antibody sequences with chain type {chain_type.value}"
            )

            return ProcessingResult(
                success=True,
                data={"antibody_sequences": sequences},
                metadata={
                    "chain_type": chain_type.value,
                    "count": len(sequences),
                    "limit": limit,
                    "offset": offset,
                },
            )

        except Exception as e:
            error_msg = f"Error finding antibody sequences by chain type {chain_type.value}: {str(e)}"
            logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    async def list_all_antibody_sequences(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> ProcessingResult:
        """List all antibody sequences with optional pagination."""
        try:
            logger.info("Retrieving all antibody sequences")

            sequences = await self.repository.find_all(
                limit=limit, offset=offset
            )
            total_count = await self.repository.count()

            logger.info(
                f"Retrieved {len(sequences)} antibody sequences (total: {total_count})"
            )

            return ProcessingResult(
                success=True,
                data={"antibody_sequences": sequences},
                metadata={
                    "count": len(sequences),
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                },
            )

        except Exception as e:
            error_msg = f"Error listing antibody sequences: {str(e)}"
            logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    async def delete_antibody_sequence(
        self, sequence_id: str
    ) -> ProcessingResult:
        """Delete an antibody sequence by ID."""
        try:
            logger.info(f"Deleting antibody sequence: {sequence_id}")

            success = await self.repository.delete(sequence_id)

            if success:
                logger.info(
                    f"Successfully deleted antibody sequence: {sequence_id}"
                )
                return ProcessingResult(
                    success=True,
                    data={"deleted": True},
                    metadata={"sequence_id": sequence_id},
                )
            else:
                logger.warning(
                    f"Antibody sequence not found for deletion: {sequence_id}"
                )
                return ProcessingResult(
                    success=False,
                    error=f"Antibody sequence not found: {sequence_id}",
                )

        except Exception as e:
            error_msg = (
                f"Error deleting antibody sequence {sequence_id}: {str(e)}"
            )
            logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    async def get_antibody_sequence_statistics(self) -> ProcessingResult:
        """Get statistics about stored antibody sequences."""
        try:
            logger.info("Retrieving antibody sequence statistics")

            total_count = await self.repository.count()

            # Get counts by chain type
            heavy_chains = await self.repository.find_by_chain_type(
                ChainType.HEAVY
            )
            light_chains = await self.repository.find_by_chain_type(
                ChainType.LIGHT
            )
            single_chains = await self.repository.find_by_chain_type(
                ChainType.SINGLE_CHAIN
            )

            stats = {
                "total_sequences": total_count,
                "by_chain_type": {
                    "heavy": len(heavy_chains),
                    "light": len(light_chains),
                    "single_chain": len(single_chains),
                },
                "total_chains": len(heavy_chains)
                + len(light_chains)
                + len(single_chains),
            }

            logger.info(f"Retrieved statistics: {stats}")

            return ProcessingResult(
                success=True,
                data={"statistics": stats},
                metadata={"statistics_type": "antibody_sequences"},
            )

        except Exception as e:
            error_msg = (
                f"Error retrieving antibody sequence statistics: {str(e)}"
            )
            logger.error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def _validate_antibody_sequence(self, sequence: AntibodySequence) -> bool:
        """Validate an antibody sequence for database persistence."""
        try:
            # Basic validation
            if not sequence.name or not sequence.name.strip():
                logger.warning("Antibody sequence missing name")
                return False

            if not sequence.chains:
                logger.warning(
                    f"Antibody sequence {sequence.name} has no chains"
                )
                return False

            # Validate each chain
            for chain in sequence.chains:
                if not self._validate_chain(chain):
                    return False

            return True

        except Exception as e:
            logger.error(
                f"Error validating antibody sequence {sequence.name}: {e}"
            )
            return False

    def _validate_chain(self, chain) -> bool:
        """Validate a chain for database persistence."""
        try:
            if not chain.name or not chain.name.strip():
                logger.warning("Chain missing name")
                return False

            if not chain.chain_type:
                logger.warning(f"Chain {chain.name} missing chain type")
                return False

            if not chain.numbering_scheme:
                logger.warning(f"Chain {chain.name} missing numbering scheme")
                return False

            # Validate domains
            for domain in chain.domains:
                if not self._validate_domain(domain):
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating chain {chain.name}: {e}")
            return False

    def _validate_domain(self, domain) -> bool:
        """Validate a domain for database persistence."""
        try:
            if not domain.domain_type:
                logger.warning("Domain missing domain type")
                return False

            # Validate regions
            for region in domain.regions:
                if not self._validate_region(region):
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating domain: {e}")
            return False

    def _validate_region(self, region) -> bool:
        """Validate a region for database persistence."""
        try:
            if not region.region_type:
                logger.warning("Region missing region type")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating region: {e}")
            return False

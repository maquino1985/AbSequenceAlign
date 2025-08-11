"""
Repository for antibody sequence data persistence.
Implements the Repository pattern for data access abstraction.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os

from backend.core.interfaces import Repository
from backend.domain.entities import BiologicEntity

from backend.logger import logger


class SequenceRepository(Repository[BiologicEntity]):
    """Repository for antibody sequence data persistence"""

    def __init__(self, storage_path: str = "data/sequences"):
        self.storage_path = storage_path
        self._ensure_storage_directory()
        logger.info(
            f"Sequence repository initialized with storage path: {storage_path}"
        )

    def save(self, entity: BiologicEntity) -> BiologicEntity:
        """Save an antibody sequence"""
        try:
            # Use the entity's computed ID
            entity_id = entity.id

            # Convert to dictionary
            sequence_data = self._entity_to_dict(entity)

            # Save to file
            file_path = self._get_file_path(entity_id)
            with open(file_path, "w") as f:
                json.dump(sequence_data, f, indent=2, default=str)

            logger.debug(f"Saved sequence {entity.name} with ID {entity_id}")
            return entity

        except Exception as e:
            error_msg = f"Failed to save sequence {entity.name}: {str(e)}"
            logger.error(error_msg)
            raise

    def find_by_id(self, entity_id: str) -> Optional[BiologicEntity]:
        """Find a sequence by its ID"""
        try:
            file_path = self._get_file_path(entity_id)

            if not os.path.exists(file_path):
                logger.debug(f"Sequence with ID {entity_id} not found")
                return None

            with open(file_path, "r") as f:
                sequence_data = json.load(f)

            sequence = self._dict_to_entity(sequence_data)
            logger.debug(f"Found sequence {sequence.name} with ID {entity_id}")
            return sequence

        except Exception as e:
            error_msg = (
                f"Failed to find sequence with ID {entity_id}: {str(e)}"
            )
            logger.error(error_msg)
            return None

    def find_all(self) -> List[BiologicEntity]:
        """Find all sequences"""
        try:
            sequences = []

            if not os.path.exists(self.storage_path):
                return sequences

            for filename in os.listdir(self.storage_path):
                if filename.endswith(".json"):
                    entity_id = filename[:-5]  # Remove .json extension
                    sequence = self.find_by_id(entity_id)
                    if sequence:
                        sequences.append(sequence)

            logger.debug(f"Found {len(sequences)} sequences")
            return sequences

        except Exception as e:
            error_msg = f"Failed to find all sequences: {str(e)}"
            logger.error(error_msg)
            return []

    def delete(self, entity_id: str) -> bool:
        """Delete a sequence by its ID"""
        try:
            file_path = self._get_file_path(entity_id)

            if not os.path.exists(file_path):
                logger.debug(
                    f"Sequence with ID {entity_id} not found for deletion"
                )
                return False

            os.remove(file_path)
            logger.debug(f"Deleted sequence with ID {entity_id}")
            return True

        except Exception as e:
            error_msg = (
                f"Failed to delete sequence with ID {entity_id}: {str(e)}"
            )
            logger.error(error_msg)
            return False

    def find_by_name(self, name: str) -> Optional[BiologicEntity]:
        """Find a sequence by its name"""
        try:
            sequences = self.find_all()
            for sequence in sequences:
                if sequence.name == name:
                    logger.debug(f"Found sequence by name: {name}")
                    return sequence

            logger.debug(f"Sequence with name {name} not found")
            return None

        except Exception as e:
            error_msg = f"Failed to find sequence by name {name}: {str(e)}"
            logger.error(error_msg)
            return None

    def find_by_chain_type(self, chain_type: str) -> List[BiologicEntity]:
        """Find sequences containing specific chain types"""
        try:
            sequences = self.find_all()
            matching_sequences = []

            for sequence in sequences:
                for chain in sequence.chains:
                    if chain.chain_type == chain_type:
                        matching_sequences.append(sequence)
                        break

            logger.debug(
                f"Found {len(matching_sequences)} sequences with chain type {chain_type}"
            )
            return matching_sequences

        except Exception as e:
            error_msg = f"Failed to find sequences by chain type {chain_type}: {str(e)}"
            logger.error(error_msg)
            return []

    def find_by_domain_type(self, domain_type: str) -> List[BiologicEntity]:
        """Find sequences containing specific domain types"""
        try:
            sequences = self.find_all()
            matching_sequences = []

            for sequence in sequences:
                for chain in sequence.chains:
                    for sequence_obj in chain.sequences:
                        for domain in sequence_obj.domains:
                            if domain.domain_type == domain_type:
                                matching_sequences.append(sequence)
                                break
                        if sequence in matching_sequences:
                            break
                    if sequence in matching_sequences:
                        break

            logger.debug(
                f"Found {len(matching_sequences)} sequences with domain type {domain_type}"
            )
            return matching_sequences

        except Exception as e:
            error_msg = f"Failed to find sequences by domain type {domain_type}: {str(e)}"
            logger.error(error_msg)
            return []

    def count(self) -> int:
        """Get the total number of sequences"""
        try:
            if not os.path.exists(self.storage_path):
                return 0

            count = len(
                [
                    f
                    for f in os.listdir(self.storage_path)
                    if f.endswith(".json")
                ]
            )
            logger.debug(f"Total sequence count: {count}")
            return count

        except Exception as e:
            error_msg = f"Failed to count sequences: {str(e)}"
            logger.error(error_msg)
            return 0

    def _ensure_storage_directory(self):
        """Ensure the storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)

    def _generate_id(self, name: str) -> str:
        """Generate a unique ID for a sequence"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(
            c for c in name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_name = safe_name.replace(" ", "_")
        return f"{safe_name}_{timestamp}"

    def _get_file_path(self, entity_id: str) -> str:
        """Get the file path for a sequence ID"""
        return os.path.join(self.storage_path, f"{entity_id}.json")

    def _entity_to_dict(self, entity: BiologicEntity) -> Dict[str, Any]:
        """Convert an entity to a dictionary for storage"""
        return {
            "id": getattr(entity, "id", None),
            "name": entity.name,
            "chains": [
                {
                    "name": chain.name,
                    "chain_type": chain.chain_type,
                    "sequences": [
                        {
                            "sequence_type": seq.sequence_type,
                            "sequence_data": seq.sequence_data,
                            "description": seq.description,
                            "domains": [
                                {
                                    "domain_type": domain.domain_type,
                                    "start_position": domain.start_position,
                                    "end_position": domain.end_position,
                                    "confidence_score": domain.confidence_score,
                                }
                                for domain in seq.domains
                            ],
                        }
                        for seq in chain.sequences
                    ],
                }
                for chain in entity.chains
            ],
            "metadata": entity.metadata or {},
            "created_at": datetime.now().isoformat(),
        }

    def _dict_to_entity(self, data: Dict[str, Any]) -> BiologicEntity:
        """Convert a dictionary to an entity"""
        # This is a simplified conversion - in a real implementation,
        # you'd need to properly reconstruct all the domain objects
        from backend.domain.entities import (
            BiologicChain,
            BiologicDomain,
            BiologicFeature,
        )

        # Reconstruct chains
        chains = []
        for chain_data in data.get("chains", []):
            # Create biologic chain
            chain = BiologicChain(
                name=chain_data["name"],
                chain_type=chain_data["chain_type"],
            )

            # Add sequences to chain if present
            if "sequences" in chain_data:
                for seq_data in chain_data["sequences"]:
                    from backend.domain.entities import BiologicSequence

                    sequence = BiologicSequence(
                        sequence_type=seq_data.get("sequence_type", "PROTEIN"),
                        sequence_data=seq_data.get("sequence_data", ""),
                        description=seq_data.get("description"),
                    )

                    # Add domains to sequence if present
                    if "domains" in seq_data:
                        for domain_data in seq_data["domains"]:
                            domain = BiologicDomain(
                                domain_type=domain_data["domain_type"],
                                start_position=domain_data["start_position"],
                                end_position=domain_data["end_position"],
                                confidence_score=domain_data[
                                    "confidence_score"
                                ],
                            )
                            sequence.domains.append(domain)

                    chain.add_sequence(sequence)

            chains.append(chain)

        # Create sequence
        sequence = BiologicEntity(name=data["name"], biologic_type="antibody")
        for chain in chains:
            sequence.add_chain(chain)

        # Set metadata if present
        if "metadata" in data:
            sequence.metadata = data["metadata"]

        return sequence

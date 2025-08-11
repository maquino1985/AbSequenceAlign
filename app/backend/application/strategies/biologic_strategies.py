"""
Strategy patterns for processing different biologic types.
Implements the Strategy pattern for flexible biologic processing.
"""

    BiologicProcessingStrategy,
    BiologicValidationStrategy,
)
from backend.core.exceptions import ValidationError
from backend.domain.entities import BiologicEntity
from backend.models.biologic_models import BiologicCreate, BiologicResponse
from backend.logger import logger


class AntibodyProcessingStrategy(BiologicProcessingStrategy):
    """Strategy for processing antibody biologics."""

    def __init__(self):
        self._logger = logger

    def can_process(self, biologic_type: str) -> bool:
        """Check if this strategy can process the given biologic type."""
        return biologic_type.lower() == "antibody"

    def process(self, biologic_data: BiologicCreate) -> BiologicResponse:
        """Process antibody biologic data according to this strategy."""
        try:
            self._logger.debug(
                f"Processing antibody biologic: {biologic_data.name}"
            )

            # Create domain entity
            domain_entity = BiologicEntity(
                name=biologic_data.name,
                description=biologic_data.description,
                organism=biologic_data.organism,
                biologic_type="antibody",
                chains=[],  # Would be populated from biologic_data.chains
                metadata={
                    "processing_strategy": "antibody",
                    **(biologic_data.metadata or {}),
                },
            )

            # Apply antibody-specific processing
            domain_entity = self._apply_antibody_processing(
                domain_entity, biologic_data
            )

            # Convert to response
            biologic_response = BiologicResponse(
                id=str(uuid.uuid4()),
                name=domain_entity.name,
                description=domain_entity.metadata.get("description"),
                organism=domain_entity.metadata.get("organism"),
                biologic_type="antibody",
                metadata=domain_entity.metadata,
                chains=[],  # Would be populated from domain_entity.chains
                created_at=None,
                updated_at=None,
            )

            self._logger.debug(
                f"Successfully processed antibody biologic: {biologic_data.name}"
            )
            return biologic_response

        except Exception as e:
            self._logger.error(f"Error processing antibody biologic: {e}")
            raise

    def validate(self, biologic_data: BiologicCreate) -> bool:
        """Validate antibody biologic data according to this strategy."""
        try:
            self._logger.debug(
                f"Validating antibody biologic: {biologic_data.name}"
            )

            # Basic validation
            if not biologic_data.name:
                raise ValidationError("Antibody name is required")

            # Antibody-specific validation
            if biologic_data.metadata:
                # Check for required antibody fields
                if "chains" in biologic_data.metadata:
                    chains = biologic_data.metadata["chains"]
                    if not isinstance(chains, list):
                        raise ValidationError("Chains must be a list")

                    # Validate chain types
                    valid_chain_types = ["HEAVY", "LIGHT", "KAPPA", "LAMBDA"]
                    for chain in chains:
                        if "chain_type" in chain:
                            if chain["chain_type"] not in valid_chain_types:
                                raise ValidationError(
                                    f"Invalid chain type: {chain['chain_type']}"
                                )

            self._logger.debug(
                f"Successfully validated antibody biologic: {biologic_data.name}"
            )
            return True

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error validating antibody biologic: {e}")
            raise ValidationError(f"Validation failed: {str(e)}")

    def _apply_antibody_processing(
        self, domain_entity: BiologicEntity, biologic_data: BiologicCreate
    ) -> BiologicEntity:
        """Apply antibody-specific processing logic."""
        try:
            # Add antibody-specific metadata
            domain_entity.metadata.update(
                {
                    "processing_stage": "annotated",
                    "antibody_type": "standard",  # Could be determined from chains
                    "has_constant_regions": True,  # Would be determined from analysis
                    "has_variable_regions": True,  # Would be determined from analysis
                }
            )

            # Apply antibody-specific business rules
            if biologic_data.metadata and "chains" in biologic_data.metadata:
                chain_count = len(biologic_data.metadata["chains"])
                domain_entity.metadata["chain_count"] = chain_count

                if chain_count == 2:
                    domain_entity.metadata["antibody_type"] = "standard"
                elif chain_count == 1:
                    domain_entity.metadata["antibody_type"] = "scfv"
                else:
                    domain_entity.metadata["antibody_type"] = "multichain"

            return domain_entity

        except Exception as e:
            self._logger.error(f"Error applying antibody processing: {e}")
            raise


class ProteinProcessingStrategy(BiologicProcessingStrategy):
    """Strategy for processing protein biologics."""

    def __init__(self):
        self._logger = logger

    def can_process(self, biologic_type: str) -> bool:
        """Check if this strategy can process the given biologic type."""
        return biologic_type.lower() == "protein"

    def process(self, biologic_data: BiologicCreate) -> BiologicResponse:
        """Process protein biologic data according to this strategy."""
        try:
            self._logger.debug(
                f"Processing protein biologic: {biologic_data.name}"
            )

            # Create domain entity
            domain_entity = BiologicEntity(
                name=biologic_data.name,
                biologic_type="protein",
                description=biologic_data.description,
                organism=biologic_data.organism,
                chains=[],  # Would be populated from biologic_data.chains
                metadata={
                    "processing_strategy": "protein",
                    **(biologic_data.metadata or {}),
                },
            )

            # Apply protein-specific processing
            domain_entity = self._apply_protein_processing(
                domain_entity, biologic_data
            )

            # Convert to response
            biologic_response = BiologicResponse(
                id=str(uuid.uuid4()),
                name=domain_entity.name,
                description=domain_entity.metadata.get("description"),
                organism=domain_entity.metadata.get("organism"),
                biologic_type="protein",
                metadata=domain_entity.metadata,
                chains=[],  # Would be populated from domain_entity.chains
                created_at=None,
                updated_at=None,
            )

            self._logger.debug(
                f"Successfully processed protein biologic: {biologic_data.name}"
            )
            return biologic_response

        except Exception as e:
            self._logger.error(f"Error processing protein biologic: {e}")
            raise

    def validate(self, biologic_data: BiologicCreate) -> bool:
        """Validate protein biologic data according to this strategy."""
        try:
            self._logger.debug(
                f"Validating protein biologic: {biologic_data.name}"
            )

            # Basic validation
            if not biologic_data.name:
                raise ValidationError("Protein name is required")

            # Protein-specific validation
            if biologic_data.metadata and "sequence" in biologic_data.metadata:
                sequence = biologic_data.metadata["sequence"]
                if not isinstance(sequence, str):
                    raise ValidationError("Protein sequence must be a string")

                # Validate amino acid sequence
                valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
                invalid_chars = set(sequence.upper()) - valid_aa
                if invalid_chars:
                    raise ValidationError(
                        f"Invalid amino acid characters: {invalid_chars}"
                    )

            self._logger.debug(
                f"Successfully validated protein biologic: {biologic_data.name}"
            )
            return True

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error validating protein biologic: {e}")
            raise ValidationError(f"Validation failed: {str(e)}")

    def _apply_protein_processing(
        self, domain_entity: BiologicEntity, biologic_data: BiologicCreate
    ) -> BiologicEntity:
        """Apply protein-specific processing logic."""
        try:
            # Add protein-specific metadata
            domain_entity.metadata.update(
                {
                    "processing_stage": "validated",
                    "protein_type": "general",  # Could be determined from analysis
                    "molecular_weight": None,  # Would be calculated
                    "isoelectric_point": None,  # Would be calculated
                }
            )

            # Apply protein-specific business rules
            if biologic_data.metadata and "sequence" in biologic_data.metadata:
                sequence = biologic_data.metadata["sequence"]
                domain_entity.metadata["sequence_length"] = len(sequence)

                # Calculate basic properties
                domain_entity.metadata["molecular_weight"] = (
                    self._calculate_molecular_weight(sequence)
                )
                domain_entity.metadata["isoelectric_point"] = (
                    self._calculate_isoelectric_point(sequence)
                )

            return domain_entity

        except Exception as e:
            self._logger.error(f"Error applying protein processing: {e}")
            raise

    def _calculate_molecular_weight(self, sequence: str) -> float:
        """Calculate molecular weight of protein sequence."""
        # Simplified calculation - in reality, you'd use a proper library
        aa_weights = {
            "A": 89.1,
            "R": 174.2,
            "N": 132.1,
            "D": 133.1,
            "C": 121.2,
            "E": 147.1,
            "Q": 146.2,
            "G": 75.1,
            "H": 155.2,
            "I": 131.2,
            "L": 131.2,
            "K": 146.2,
            "M": 149.2,
            "F": 165.2,
            "P": 115.1,
            "S": 105.1,
            "T": 119.1,
            "W": 204.2,
            "Y": 181.2,
            "V": 117.1,
        }

        total_weight = sum(aa_weights.get(aa.upper(), 0) for aa in sequence)
        return round(total_weight, 2)

    def _calculate_isoelectric_point(self, sequence: str) -> float:
        """Calculate isoelectric point of protein sequence."""
        # Simplified calculation - in reality, you'd use a proper library
        # This is a placeholder implementation
        return 7.0


class DNAProcessingStrategy(BiologicProcessingStrategy):
    """Strategy for processing DNA biologics."""

    def __init__(self):
        self._logger = logger

    def can_process(self, biologic_type: str) -> bool:
        """Check if this strategy can process the given biologic type."""
        return biologic_type.lower() == "dna"

    def process(self, biologic_data: BiologicCreate) -> BiologicResponse:
        """Process DNA biologic data according to this strategy."""
        try:
            self._logger.debug(
                f"Processing DNA biologic: {biologic_data.name}"
            )

            # Create domain entity
            domain_entity = BiologicEntity(
                name=biologic_data.name,
                biologic_type="dna",
                description=biologic_data.description,
                organism=biologic_data.organism,
                chains=[],  # Would be populated from biologic_data.chains
                metadata={
                    "processing_strategy": "dna",
                    **(biologic_data.metadata or {}),
                },
            )

            # Apply DNA-specific processing
            domain_entity = self._apply_dna_processing(
                domain_entity, biologic_data
            )

            # Convert to response
            biologic_response = BiologicResponse(
                id=str(uuid.uuid4()),
                name=domain_entity.name,
                description=domain_entity.metadata.get("description"),
                organism=domain_entity.metadata.get("organism"),
                biologic_type="dna",
                metadata=domain_entity.metadata,
                chains=[],  # Would be populated from domain_entity.chains
                created_at=None,
                updated_at=None,
            )

            self._logger.debug(
                f"Successfully processed DNA biologic: {biologic_data.name}"
            )
            return biologic_response

        except Exception as e:
            self._logger.error(f"Error processing DNA biologic: {e}")
            raise

    def validate(self, biologic_data: BiologicCreate) -> bool:
        """Validate DNA biologic data according to this strategy."""
        try:
            self._logger.debug(
                f"Validating DNA biologic: {biologic_data.name}"
            )

            # Basic validation
            if not biologic_data.name:
                raise ValidationError("DNA name is required")

            # DNA-specific validation
            if biologic_data.metadata and "sequence" in biologic_data.metadata:
                sequence = biologic_data.metadata["sequence"]
                if not isinstance(sequence, str):
                    raise ValidationError("DNA sequence must be a string")

                # Validate DNA sequence
                valid_bases = set("ATCG")
                invalid_chars = set(sequence.upper()) - valid_bases
                if invalid_chars:
                    raise ValidationError(
                        f"Invalid DNA bases: {invalid_chars}"
                    )

            self._logger.debug(
                f"Successfully validated DNA biologic: {biologic_data.name}"
            )
            return True

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error validating DNA biologic: {e}")
            raise ValidationError(f"Validation failed: {str(e)}")

    def _apply_dna_processing(
        self, domain_entity: BiologicEntity, biologic_data: BiologicCreate
    ) -> BiologicEntity:
        """Apply DNA-specific processing logic."""
        try:
            # Add DNA-specific metadata
            domain_entity.metadata.update(
                {
                    "processing_stage": "validated",
                    "dna_type": "genomic",  # Could be determined from analysis
                    "gc_content": None,  # Would be calculated
                    "length_bp": None,  # Would be calculated
                }
            )

            # Apply DNA-specific business rules
            if biologic_data.metadata and "sequence" in biologic_data.metadata:
                sequence = biologic_data.metadata["sequence"]
                domain_entity.metadata["length_bp"] = len(sequence)
                domain_entity.metadata["gc_content"] = (
                    self._calculate_gc_content(sequence)
                )

            return domain_entity

        except Exception as e:
            self._logger.error(f"Error applying DNA processing: {e}")
            raise

    def _calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content of DNA sequence."""
        sequence = sequence.upper()
        gc_count = sequence.count("G") + sequence.count("C")
        total_count = len(sequence)

        if total_count == 0:
            return 0.0

        return round((gc_count / total_count) * 100, 2)


class RNAProcessingStrategy(BiologicProcessingStrategy):
    """Strategy for processing RNA biologics."""

    def __init__(self):
        self._logger = logger

    def can_process(self, biologic_type: str) -> bool:
        """Check if this strategy can process the given biologic type."""
        return biologic_type.lower() == "rna"

    def process(self, biologic_data: BiologicCreate) -> BiologicResponse:
        """Process RNA biologic data according to this strategy."""
        try:
            self._logger.debug(
                f"Processing RNA biologic: {biologic_data.name}"
            )

            # Create domain entity
            domain_entity = BiologicEntity(
                name=biologic_data.name,
                biologic_type="rna",
                description=biologic_data.description,
                organism=biologic_data.organism,
                chains=[],  # Would be populated from biologic_data.chains
                metadata={
                    "processing_strategy": "rna",
                    **(biologic_data.metadata or {}),
                },
            )

            # Apply RNA-specific processing
            domain_entity = self._apply_rna_processing(
                domain_entity, biologic_data
            )

            # Convert to response
            biologic_response = BiologicResponse(
                id=str(uuid.uuid4()),
                name=domain_entity.name,
                description=domain_entity.metadata.get("description"),
                organism=domain_entity.metadata.get("organism"),
                biologic_type="rna",
                metadata=domain_entity.metadata,
                chains=[],  # Would be populated from domain_entity.chains
                created_at=None,
                updated_at=None,
            )

            self._logger.debug(
                f"Successfully processed RNA biologic: {biologic_data.name}"
            )
            return biologic_response

        except Exception as e:
            self._logger.error(f"Error processing RNA biologic: {e}")
            raise

    def validate(self, biologic_data: BiologicCreate) -> bool:
        """Validate RNA biologic data according to this strategy."""
        try:
            self._logger.debug(
                f"Validating RNA biologic: {biologic_data.name}"
            )

            # Basic validation
            if not biologic_data.name:
                raise ValidationError("RNA name is required")

            # RNA-specific validation
            if biologic_data.metadata and "sequence" in biologic_data.metadata:
                sequence = biologic_data.metadata["sequence"]
                if not isinstance(sequence, str):
                    raise ValidationError("RNA sequence must be a string")

                # Validate RNA sequence
                valid_bases = set("AUCG")
                invalid_chars = set(sequence.upper()) - valid_bases
                if invalid_chars:
                    raise ValidationError(
                        f"Invalid RNA bases: {invalid_chars}"
                    )

            self._logger.debug(
                f"Successfully validated RNA biologic: {biologic_data.name}"
            )
            return True

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error validating RNA biologic: {e}")
            raise ValidationError(f"Validation failed: {str(e)}")

    def _apply_rna_processing(
        self, domain_entity: BiologicEntity, biologic_data: BiologicCreate
    ) -> BiologicEntity:
        """Apply RNA-specific processing logic."""
        try:
            # Add RNA-specific metadata
            domain_entity.metadata.update(
                {
                    "processing_stage": "validated",
                    "rna_type": "mrna",  # Could be determined from analysis
                    "gc_content": None,  # Would be calculated
                    "length_nt": None,  # Would be calculated
                }
            )

            # Apply RNA-specific business rules
            if biologic_data.metadata and "sequence" in biologic_data.metadata:
                sequence = biologic_data.metadata["sequence"]
                domain_entity.metadata["length_nt"] = len(sequence)
                domain_entity.metadata["gc_content"] = (
                    self._calculate_gc_content(sequence)
                )

            return domain_entity

        except Exception as e:
            self._logger.error(f"Error applying RNA processing: {e}")
            raise

    def _calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content of RNA sequence."""
        sequence = sequence.upper()
        gc_count = sequence.count("G") + sequence.count("C")
        total_count = len(sequence)

        if total_count == 0:
            return 0.0

        return round((gc_count / total_count) * 100, 2)


# Validation strategies
class AntibodyValidationStrategy(BiologicValidationStrategy):
    """Strategy for validating antibody biologics."""

    def can_validate(self, biologic_type: str) -> bool:
        """Check if this strategy can validate the given biologic type."""
        return biologic_type.lower() == "antibody"

    def validate(self, biologic_data: BiologicCreate) -> List[str]:
        """Validate antibody biologic data and return list of errors."""
        errors = []

        try:
            # Basic validation
            if not biologic_data.name:
                errors.append("Antibody name is required")

            # Antibody-specific validation
            if biologic_data.metadata:
                if "chains" in biologic_data.metadata:
                    chains = biologic_data.metadata["chains"]
                    if not isinstance(chains, list):
                        errors.append("Chains must be a list")
                    else:
                        # Validate each chain
                        for i, chain in enumerate(chains):
                            if not isinstance(chain, dict):
                                errors.append(
                                    f"Chain {i} must be a dictionary"
                                )
                            elif "chain_type" not in chain:
                                errors.append(
                                    f"Chain {i} must have a chain_type"
                                )
                            elif chain["chain_type"] not in [
                                "HEAVY",
                                "LIGHT",
                                "KAPPA",
                                "LAMBDA",
                            ]:
                                errors.append(
                                    f"Chain {i} has invalid chain_type: {chain['chain_type']}"
                                )

        except Exception as e:
            errors.append(f"Validation error: {str(e)}")

        return errors


class ProteinValidationStrategy(BiologicValidationStrategy):
    """Strategy for validating protein biologics."""

    def can_validate(self, biologic_type: str) -> bool:
        """Check if this strategy can validate the given biologic type."""
        return biologic_type.lower() == "protein"

    def validate(self, biologic_data: BiologicCreate) -> List[str]:
        """Validate protein biologic data and return list of errors."""
        errors = []

        try:
            # Basic validation
            if not biologic_data.name:
                errors.append("Protein name is required")

            # Protein-specific validation
            if biologic_data.metadata and "sequence" in biologic_data.metadata:
                sequence = biologic_data.metadata["sequence"]
                if not isinstance(sequence, str):
                    errors.append("Protein sequence must be a string")
                else:
                    # Validate amino acid sequence
                    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
                    invalid_chars = set(sequence.upper()) - valid_aa
                    if invalid_chars:
                        errors.append(
                            f"Invalid amino acid characters: {invalid_chars}"
                        )

        except Exception as e:
            errors.append(f"Validation error: {str(e)}")

        return errors

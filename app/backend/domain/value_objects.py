"""
Value objects for the antibody sequence analysis domain.
Value objects are immutable and represent concepts that are defined by their attributes.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum

from ..core.exceptions import ValidationError, SequenceValidationError


@dataclass(frozen=True)
class AminoAcidSequence:
    """Value object representing an amino acid sequence"""

    sequence: str

    def __post_init__(self):
        if not self._is_valid_sequence():
            raise SequenceValidationError(
                f"Invalid amino acid sequence: {self.sequence}",
                field="sequence",
                value=self.sequence,
            )

    def _is_valid_sequence(self) -> bool:
        """Validate that the sequence contains only valid amino acids"""
        if not self.sequence or not isinstance(self.sequence, str):
            return False

        # Valid amino acid characters (including X for unknown)
        valid_chars = set("ACDEFGHIKLMNPQRSTVWYX")
        return all(char.upper() in valid_chars for char in self.sequence)

    def __len__(self) -> int:
        return len(self.sequence)

    def __str__(self) -> str:
        return self.sequence

    def upper(self) -> "AminoAcidSequence":
        """Return uppercase version of the sequence"""
        return AminoAcidSequence(self.sequence.upper())

    def substring(self, start: int, end: int) -> "AminoAcidSequence":
        """Extract a substring from the sequence"""
        if start < 0 or end > len(self.sequence) or start > end:
            raise ValidationError(
                f"Invalid substring bounds: start={start}, end={end}, length={len(self.sequence)}",
                field="substring_bounds",
                value={
                    "start": start,
                    "end": end,
                    "length": len(self.sequence),
                },
            )
        return AminoAcidSequence(self.sequence[start:end])

    def contains(self, subsequence: str) -> bool:
        """Check if the sequence contains a subsequence"""
        return subsequence.upper() in self.sequence.upper()

    def count_amino_acid(self, amino_acid: str) -> int:
        """Count occurrences of a specific amino acid"""
        return self.sequence.upper().count(amino_acid.upper())


@dataclass(frozen=True)
class SequencePosition:
    """Value object representing a position in a sequence"""

    position: int
    insertion: Optional[str] = None

    def __post_init__(self):
        if self.position < 0:
            raise ValidationError(
                f"Position must be non-negative, got: {self.position}",
                field="position",
                value=self.position,
            )

    def __str__(self) -> str:
        if self.insertion:
            return f"{self.position}{self.insertion}"
        return str(self.position)

    def __lt__(self, other: "SequencePosition") -> bool:
        """Compare positions for ordering"""
        if not isinstance(other, SequencePosition):
            return NotImplemented
        return self.position < other.position

    def __eq__(self, other: object) -> bool:
        """Check equality of positions"""
        if not isinstance(other, SequencePosition):
            return NotImplemented
        return (
            self.position == other.position
            and self.insertion == other.insertion
        )

    def __hash__(self) -> int:
        """Hash for use in sets and dicts"""
        return hash((self.position, self.insertion))


@dataclass(frozen=True)
class RegionBoundary:
    """Value object representing the boundaries of a region"""

    start: int
    end: int

    def __post_init__(self):
        if self.start < 0 or self.end < 0:
            raise ValidationError(
                f"Boundaries must be non-negative: start={self.start}, end={self.end}",
                field="boundaries",
                value={"start": self.start, "end": self.end},
            )
        if self.start > self.end:
            raise ValidationError(
                f"Start position must be <= end position: start={self.start}, "
                f"end={self.end}",
                field="boundaries",
                value={"start": self.start, "end": self.end},
            )

    def contains(self, position: int) -> bool:
        """Check if a position is within this boundary"""
        return self.start <= position <= self.end

    def length(self) -> int:
        """Get the length of this region"""
        return self.end - self.start + 1

    def overlaps_with(self, other: "RegionBoundary") -> bool:
        """Check if this boundary overlaps with another"""
        return not (self.end < other.start or other.end < self.start)

    def intersection(
        self, other: "RegionBoundary"
    ) -> Optional["RegionBoundary"]:
        """Get the intersection of two boundaries"""
        if not self.overlaps_with(other):
            return None

        intersection_start = max(self.start, other.start)
        intersection_end = min(self.end, other.end)
        return RegionBoundary(intersection_start, intersection_end)

    def union(self, other: "RegionBoundary") -> "RegionBoundary":
        """Get the union of two boundaries"""
        union_start = min(self.start, other.start)
        union_end = max(self.end, other.end)
        return RegionBoundary(union_start, union_end)

    def is_adjacent_to(self, other: "RegionBoundary") -> bool:
        """Check if this boundary is adjacent to another"""
        return self.end + 1 == other.start or other.end + 1 == self.start


@dataclass(frozen=True)
class SequenceIdentifier:
    """Value object representing a unique sequence identifier"""

    identifier: str
    source: str
    version: Optional[str] = None

    def __post_init__(self):
        if not self.identifier or not isinstance(self.identifier, str):
            raise ValidationError(
                "Identifier must be a non-empty string",
                field="identifier",
                value=self.identifier,
            )
        if not self.source or not isinstance(self.source, str):
            raise ValidationError(
                "Source must be a non-empty string",
                field="source",
                value=self.source,
            )

    def __str__(self) -> str:
        if self.version:
            return f"{self.source}:{self.identifier}:{self.version}"
        return f"{self.source}:{self.identifier}"

    def __eq__(self, other: object) -> bool:
        """Check equality of identifiers"""
        if not isinstance(other, SequenceIdentifier):
            return NotImplemented
        return (
            self.identifier == other.identifier
            and self.source == other.source
            and self.version == other.version
        )

    def __hash__(self) -> int:
        """Hash for use in sets and dicts"""
        return hash((self.identifier, self.source, self.version))


@dataclass(frozen=True)
class ConfidenceScore:
    """Value object representing a confidence score"""

    score: float
    method: str

    def __post_init__(self):
        if not isinstance(self.score, (int, float)):
            raise ValidationError(
                "Score must be a number", field="score", value=self.score
            )
        if not (0.0 <= self.score <= 1.0):
            raise ValidationError(
                "Score must be between 0.0 and 1.0",
                field="score",
                value=self.score,
            )
        if not self.method or not isinstance(self.method, str):
            raise ValidationError(
                "Method must be a non-empty string",
                field="method",
                value=self.method,
            )

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if the confidence is above a threshold"""
        return self.score >= threshold

    def is_low_confidence(self, threshold: float = 0.5) -> bool:
        """Check if the confidence is below a threshold"""
        return self.score < threshold

    def __str__(self) -> str:
        return f"{self.score:.3f} ({self.method})"


@dataclass(frozen=True)
class AnnotationMetadata:
    """Value object representing annotation metadata"""

    tool_version: str
    timestamp: str
    parameters: dict
    confidence_score: Optional[ConfidenceScore] = None

    def __post_init__(self):
        if not self.tool_version or not isinstance(self.tool_version, str):
            raise ValidationError(
                "Tool version must be a non-empty string",
                field="tool_version",
                value=self.tool_version,
            )
        if not self.timestamp or not isinstance(self.timestamp, str):
            raise ValidationError(
                "Timestamp must be a non-empty string",
                field="timestamp",
                value=self.timestamp,
            )
        if not isinstance(self.parameters, dict):
            raise ValidationError(
                "Parameters must be a dictionary",
                field="parameters",
                value=self.parameters,
            )

    def get_parameter(self, key: str, default=None):
        """Get a parameter value"""
        return self.parameters.get(key, default)

    def has_parameter(self, key: str) -> bool:
        """Check if a parameter exists"""
        return key in self.parameters

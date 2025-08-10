from typing import List, Tuple, Optional, Dict, Any

SequenceType = Tuple[str, str]
NumberingType = Optional[List[Tuple[str, int, int]]]
AlignmentDetailsType = Optional[Dict[str, Any]]
HitTableType = Optional[List[List[Any]]]


class Chain:
    def __init__(self, name: str, sequence: str, domains: List["Domain"]) -> None:
        self.name: str = name
        self.sequence: str = sequence
        self.domains: List["Domain"] = domains
        for domain in self.domains:
            domain.chain = self

    def __repr__(self) -> str:
        return (
            f"Chain(name={self.name}, sequence={self.sequence}, domains={self.domains})"
        )


class Domain:
    def __init__(
        self,
        sequence: str,
        numbering: NumberingType,
        alignment_details: AlignmentDetailsType,
        hit_table: HitTableType,
        isotype: str,
        germlines: dict,
        species: str,
        chain: "Chain" = None,
    ) -> None:
        self.sequence: str = sequence
        self.numbering: NumberingType = numbering
        self.alignment_details: AlignmentDetailsType = alignment_details
        self.hit_table: HitTableType = hit_table
        self.species: str = species
        self.germlines: dict = germlines
        self.isotype: str = isotype
        self.chain: Optional["Chain"] = chain
        # New fields for constant region information
        self.domain_type: str = "V"  # 'V' for variable, 'C' for constant
        self.constant_region_info: Optional[Dict[str, Any]] = (
            None  # Details about constant region if this is one
        )

    def __repr__(self) -> str:
        base = f"Domain(sequence={self.sequence}, numbering={self.numbering})"
        if hasattr(self, "regions") and self.regions:
            region_str = ", ".join(
                [
                    f"[{r.name}, {r.start}, {r.stop}, {r.sequence}]"
                    for r in self.regions.values()
                ]
            )
            return f"Domain(sequence={self.sequence}, regions: {region_str})"
        return base

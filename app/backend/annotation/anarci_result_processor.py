import itertools
import logging
from typing import List, Optional, Dict, Any

from anarci import run_anarci  # type: ignore[import-untyped]

from backend.utils.chain_type_util import ChainTypeUtil
from .antibody_region_annotator import AntibodyRegionAnnotator
from .isotype_hmmer import detect_isotype_with_hmmer

from backend.models.models_v2 import (
    ChainType,
    Domain,
    Region,
    Chain,
    DomainType,
)


class AnarciResultObject:
    def __init__(self, biologic_name: str, chains: List[Chain]) -> None:
        self.biologic_name: str = biologic_name
        self.chains: List[Chain] = chains

    def __repr__(self) -> str:
        return f"AnarciResultObject(biologic_name={self.biologic_name}, chains={self.chains})"


class AnarciResultProcessor:

    def __init__(
        self,
        input_dict: Dict[str, Dict[str, str]],
        numbering_scheme: str = "imgt",
    ) -> None:
        self.original_scheme = numbering_scheme
        self.numbering_scheme = numbering_scheme
        self.results = self._process_results(input_dict)

    def process(
        self,
        input_dict: Dict[str, Dict[str, str]],
        numbering_scheme: str = "imgt",
    ) -> List[AnarciResultObject]:
        """
        Process the input dictionary and return a list of AnarciResultObject.
        """
        return self._process_results(input_dict, numbering_scheme)

    def _detect_constant_region(
        self, sequence: str, start_pos: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Detect constant region in a sequence using HMMER.

        Args:
            sequence: The amino acid sequence to analyze
            start_pos: Starting position in the original sequence (for position tracking)

        Returns:
            Dictionary with constant region information or None if not found
        """
        isotype = detect_isotype_with_hmmer(sequence)
        if not isotype:
            return None

        return {
            "isotype": isotype,
            "sequence": sequence,
            "start": start_pos,
            "end": start_pos + len(sequence),
            "domain_type": "C",
        }

    def _run_anarci_with_fallback(self, anarci_input, scheme, **kwargs):
        # If CGG, use Kabat for ANARCI, but keep track of original scheme
        anarci_scheme = "kabat" if scheme == "cgg" else scheme
        try:
            return (
                run_anarci(anarci_input, scheme=anarci_scheme, **kwargs),
                scheme,
            )
        except Exception as e:
            if anarci_scheme != "imgt":
                logging.warning(
                    f"ANARCI failed with scheme '{anarci_scheme}' ({e}), retrying with 'imgt'."
                )
                return (
                    run_anarci(anarci_input, scheme="imgt", **kwargs),
                    "imgt",
                )
            else:
                raise

    def _parse_best_hits_by_chain(self, hit_table) -> Dict[str, Any]:
        """
        Parse the ANARCI hit table to extract the best germline hit for each chain.
        """
        header = hit_table[0] if hit_table and len(hit_table) > 0 else []
        rows = hit_table[1:] if hit_table and len(hit_table) > 1 else []
        best_hits = {}
        if not header or not rows:
            return best_hits

        id_idx = header.index("id") if "id" in header else None
        bitscore_idx = (
            header.index("bitscore") if "bitscore" in header else None
        )
        if id_idx is None or bitscore_idx is None:
            return best_hits

        for key, group in itertools.groupby(
            sorted(rows, key=lambda row: row[id_idx]),
            key=lambda row: (
                row[id_idx].split("_")[0] + "_" + row[id_idx].split("_")[1]
            ),
        ):
            best_row = max(
                list(group),
                key=lambda row: row[bitscore_idx],
            )
            best_hits[key] = best_row
        return best_hits

    def _create_linker_domain(self, linker_seq, start, end, species) -> Domain:
        """
        Create a linker domain object.
        """
        return Domain(
            sequence=linker_seq,
            numbering=None,
            alignment_details={
                "domain_type": "LINKER",
                "sequence": linker_seq,
                "start": start,
                "end": end,
            },
            hit_table=None,
            isotype=None,
            species=species,
            germlines=None,
            domain_type=DomainType.LINKER,
            regions=[
                Region(
                    name="LINKER",
                    start=start + 1,
                    stop=end,
                    sequence=linker_seq,
                )
            ],
        )

    def _adjust_region_positions(self, domain, domain_start):
        """
        Adjust region positions from domain-relative to sequence-absolute.
        """
        if hasattr(domain, "regions") and domain.regions:
            for region in domain.regions:

                def to_int(pos):
                    if isinstance(pos, (list, tuple)):
                        return int(pos[0])
                    return int(pos)

                start_rel = to_int(region.start)
                stop_rel = to_int(region.stop)
                start_abs = domain_start + (start_rel - 1) + 1
                stop_abs = domain_start + (stop_rel - 1) + 1
                region.start = start_abs
                region.stop = stop_abs

    def _process_domain(
        self,
        numbered_domain,
        domain_alignment,
        raw_sequence,
        domain_start,
        domain_end,
        best_hit,
        used_scheme,
        species,
    ) -> Domain:
        """
        Process a single domain, annotate regions, and adjust region positions.
        """
        domain = Domain(
            sequence=raw_sequence[domain_start:domain_end],
            numbering=numbered_domain,
            alignment_details=domain_alignment,
            hit_table=best_hit,
            species=species,
            germlines=domain_alignment.get("germlines"),
        )
        domain.domain_type = DomainType.VARIABLE
        AntibodyRegionAnnotator.annotate_domain(domain, scheme=used_scheme)
        self._adjust_region_positions(domain, domain_start)
        return domain

    def _process_constant_domain(self, constant_info, species) -> Domain:
        """
        Create a constant region domain object.
        """
        constant_domain = Domain(
            sequence=constant_info["sequence"],
            numbering=None,
            alignment_details={"domain_type": "C"},
            hit_table=None,
            isotype=constant_info["isotype"],
            species=species,
            germlines=None,
        )
        constant_domain.domain_type = DomainType.CONSTANT
        constant_domain.regions = [
            Region(
                name="CONSTANT",
                start=constant_info["start"],
                stop=constant_info["end"],
                sequence=constant_info["sequence"],
            )
        ]
        return constant_domain

    def _process_results(
        self,
        input_dict: Dict[str, Dict[str, str]],
        numbering_scheme: Optional[str] = None,
    ) -> List[AnarciResultObject]:
        result_objects = []
        _scheme = None
        if numbering_scheme:
            _scheme = numbering_scheme
        else:
            _scheme = self.numbering_scheme
        for biologic_name, chains_dict in input_dict.items():
            chains = []
            for chain_name, chain_seq in chains_dict.items():
                anarci_input = [(chain_name, chain_seq)]
                (
                    sequences,
                    numbered,
                    alignment_details,
                    hit_tables,
                ), used_scheme = self._run_anarci_with_fallback(
                    anarci_input,
                    scheme=_scheme,
                    allowed_species=["human", "mouse", "rat"],
                    assign_germline=True,
                )

                seq_name, raw_sequence = sequences[0]
                seq_numbered = numbered[0]
                seq_aligns = alignment_details[0]
                seq_hits = hit_tables[0]

                best_hits_by_chain = self._parse_best_hits_by_chain(seq_hits)

                domains = []
                domain_positions = [
                    (
                        dom_idx,
                        domain_alignment.get("query_start", 0),
                        domain_alignment.get("query_end", 0),
                    )
                    for dom_idx, domain_alignment in enumerate(seq_aligns)
                    if domain_alignment
                ]
                domain_positions.sort(key=lambda x: x[1])

                prev_domain_end = 0
                for dom_idx, domain_start, domain_end in domain_positions:
                    numbered_domain = seq_numbered[dom_idx]
                    domain_alignment = seq_aligns[dom_idx]
                    chain_type = (
                        domain_alignment.get("chain_type")
                        if isinstance(domain_alignment, dict)
                        else None
                    )
                    species = (
                        domain_alignment.get("species")
                        if isinstance(domain_alignment, dict)
                        else None
                    )
                    best_hit = None
                    if chain_type and species:
                        key = f"{species}_{chain_type}"
                        best_hit = best_hits_by_chain.get(key)

                    # Add linker if needed
                    if prev_domain_end > 0 and domain_start > prev_domain_end:
                        linker_seq = raw_sequence[prev_domain_end:domain_start]
                        linker_domain = self._create_linker_domain(
                            linker_seq, prev_domain_end, domain_start, species
                        )
                        domains.append(linker_domain)

                    # Process variable domain
                    domain = self._process_domain(
                        numbered_domain,
                        domain_alignment,
                        raw_sequence,
                        domain_start,
                        domain_end,
                        best_hit,
                        used_scheme,
                        species,
                    )
                    domains.append(domain)

                    # Check for constant region after variable domain
                    if domain_end < len(raw_sequence):
                        remaining_seq = raw_sequence[domain_end:]
                        constant_info = self._detect_constant_region(
                            remaining_seq, domain_end
                        )
                        if constant_info:
                            constant_domain = self._process_constant_domain(
                                constant_info, species
                            )
                            domains.append(constant_domain)
                            prev_domain_end = constant_info["end"]
                        else:
                            prev_domain_end = domain_end
                    else:
                        prev_domain_end = domain_end

                chain_type: ChainType = ChainTypeUtil.extract_chain_type(
                    seq_aligns
                )
                chain = Chain(
                    name=chain_name,
                    sequence=raw_sequence,
                    chain_type=chain_type,
                )
                chain.domains = domains
                chains.append(chain)
            result_objects.append(AnarciResultObject(biologic_name, chains))
        return result_objects

    def get_result_by_biologic_name(
        self, biologic_name: str
    ) -> Optional[AnarciResultObject]:
        for result in self.results:
            if result.biologic_name == biologic_name:
                return result
        return None

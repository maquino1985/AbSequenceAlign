import itertools
import logging
from typing import List, Optional, Dict, Any

from anarci import run_anarci

from .AntibodyRegionAnnotator import AntibodyRegionAnnotator
from .isotype_hmmer import detect_isotype_with_hmmer
from ..utils.types import Chain, Domain


class AnarciResultObject:
    def __init__(self, biologic_name: str, chains: List[Chain]) -> None:
        self.biologic_name: str = biologic_name
        self.chains: List[Chain] = chains

    def __repr__(self) -> str:
        return f"AnarciResultObject(biologic_name={self.biologic_name}, chains={self.chains})"


class AnarciResultProcessor:
    def __init__(
        self, input_dict: Dict[str, Dict[str, str]], numbering_scheme: str = "imgt"
    ) -> None:
        self.original_scheme = numbering_scheme
        self.numbering_scheme = numbering_scheme
        self.results = self._process_results(input_dict)

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
            return run_anarci(anarci_input, scheme=anarci_scheme, **kwargs), scheme
        except Exception as e:
            if anarci_scheme != "imgt":
                logging.warning(
                    f"ANARCI failed with scheme '{anarci_scheme}' ({e}), retrying with 'imgt'."
                )
                return run_anarci(anarci_input, scheme="imgt", **kwargs), "imgt"
            else:
                raise

    def _process_results(
        self, input_dict: Dict[str, Dict[str, str]]
    ) -> List[AnarciResultObject]:
        result_objects = []
        for biologic_name, chains_dict in input_dict.items():
            # We'll create one chain per input sequence, regardless of how many domains ANARCI finds
            chains = []
            for chain_name, chain_seq in chains_dict.items():
                anarci_input = [(chain_name, chain_seq)]
                (sequences, numbered, alignment_details, hit_tables), used_scheme = (
                    self._run_anarci_with_fallback(
                        anarci_input,
                        scheme=self.numbering_scheme,
                        allowed_species=["human", "mouse", "rat"],
                        assign_germline=True,
                    )
                )

                # Process one sequence at a time (ANARCI processes one sequence per call)
                seq_name, raw_sequence = sequences[0]
                seq_numbered = numbered[0]
                seq_aligns = alignment_details[0]
                seq_hits = hit_tables[0]

                # Process hit tables for germline info
                hit_table_header = seq_hits[0] if seq_hits and len(seq_hits) > 0 else []
                hit_table_rows = seq_hits[1:] if seq_hits and len(seq_hits) > 1 else []
                best_hits_by_chain = {}

                if hit_table_header and hit_table_rows:
                    id_idx = (
                        hit_table_header.index("id")
                        if "id" in hit_table_header
                        else None
                    )
                    bitscore_idx = (
                        hit_table_header.index("bitscore")
                        if "bitscore" in hit_table_header
                        else None
                    )
                    for key, group in itertools.groupby(
                        sorted(hit_table_rows, key=lambda row: row[id_idx]),
                        key=lambda row: (
                            row[id_idx].split("_")[0] + "_" + row[id_idx].split("_")[1]
                            if id_idx is not None
                            else None
                        ),
                    ):
                        best_row = max(
                            list(group),
                            key=lambda row: (
                                row[bitscore_idx] if bitscore_idx is not None else 0
                            ),
                        )
                        best_hits_by_chain[key] = best_row

                # Create domains list for this chain
                domains = []

                # Sort domains by their position in the sequence
                domain_positions = []
                for dom_idx, (numbered_domain, domain_alignment) in enumerate(
                    zip(seq_numbered, seq_aligns)
                ):
                    if not domain_alignment:
                        continue

                    domain_start = domain_alignment.get("query_start", 0)
                    domain_end = domain_alignment.get("query_end", 0)
                    domain_positions.append((dom_idx, domain_start, domain_end))

                # Sort domains by their start position to maintain sequence order
                domain_positions.sort(key=lambda x: x[1])

                # Process domains in sequence order
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

                    # Get germline info
                    best_hit = None
                    if chain_type and species:
                        key = f"{species}_{chain_type}"
                        best_hit = best_hits_by_chain.get(key)

                    # Create the domain object
                    domain = Domain(
                        sequence=raw_sequence[domain_start:domain_end],
                        numbering=numbered_domain,
                        alignment_details=domain_alignment,
                        hit_table=best_hit,
                        isotype=chain_type,
                        species=species,
                        germlines=domain_alignment.get("germlines"),
                    )

                    # Add linker information if there's a gap between domains
                    if prev_domain_end > 0 and domain_start > prev_domain_end:
                        linker_seq = raw_sequence[prev_domain_end:domain_start]
                        # Create a linker domain
                        linker_domain = Domain(
                            sequence=linker_seq,
                            numbering=None,  # Linkers don't get numbered
                            alignment_details={
                                "domain_type": "LINKER",
                                "sequence": linker_seq,
                                "start": prev_domain_end,
                                "end": domain_start,
                            },
                            hit_table=None,
                            isotype=None,
                            species=species,  # Use same species as variable domain
                            germlines=None,
                        )
                        linker_domain.domain_type = "LINKER"
                        # Add linker region directly to the domain
                        linker_domain.regions = {
                            "LINKER": {
                                "name": "LINKER",
                                "start": prev_domain_end,
                                "stop": domain_start,
                                "sequence": linker_seq,
                                "domain_type": "LINKER",
                            }
                        }
                        domains.append(linker_domain)

                    # Attach annotation scheme and annotate regions
                    domain.domain_type = "V"  # Mark as variable domain
                    domain.annotation_scheme = used_scheme
                    AntibodyRegionAnnotator.annotate_domain(domain, scheme=used_scheme)
                    # Shift region coordinates to absolute positions within the original sequence
                    if hasattr(domain, "regions") and domain.regions:
                        absolute_regions = {}
                        for region_name, region in domain.regions.items():
                            # region.start/stop may be ints or like [pos, ' ']; normalize to int
                            def to_int(pos):
                                if isinstance(pos, (list, tuple)):
                                    return int(pos[0])
                                return int(pos)

                            start_rel = to_int(region.start)
                            stop_rel = to_int(region.stop)
                            # Convert domain-relative numbering start to index offset using numbering list
                            # Here, ANARCI numbering positions are 1-based; domain_start is 0-based index into raw_sequence
                            # We therefore add domain_start - 1 to convert to absolute 1-based positions
                            start_abs = domain_start + (start_rel - 1)
                            stop_abs = domain_start + (stop_rel - 1)
                            absolute_regions[region_name] = type(region)(
                                name=region.name,
                                start=start_abs,
                                stop=stop_abs,
                                sequence=region.sequence,
                            )
                        domain.regions = absolute_regions
                    domains.append(domain)

                    # Check for constant region after variable domain
                    if domain_end < len(raw_sequence):
                        remaining_seq = raw_sequence[domain_end:]
                        constant_info = self._detect_constant_region(
                            remaining_seq, domain_end
                        )
                        if constant_info:
                            # Create a new domain for the constant region
                            constant_domain = Domain(
                                sequence=constant_info["sequence"],
                                numbering=None,  # Constant regions don't get numbered like variable regions
                                alignment_details={"domain_type": "C"},
                                hit_table=None,
                                isotype=constant_info["isotype"],
                                species=species,  # Use same species as variable domain
                                germlines=None,
                            )
                            constant_domain.domain_type = "C"
                            constant_domain.constant_region_info = constant_info
                            # Add constant region directly to the domain
                            constant_domain.regions = {
                                "CONSTANT": {
                                    "name": "CONSTANT",
                                    "start": constant_info["start"],
                                    "stop": constant_info["end"],
                                    "sequence": constant_info["sequence"],
                                    "domain_type": "C",
                                    "isotype": constant_info["isotype"],
                                }
                            }
                            domains.append(constant_domain)
                            prev_domain_end = constant_info["end"]
                        else:
                            prev_domain_end = domain_end
                    else:
                        prev_domain_end = domain_end

                # Create a single chain containing all domains
                chains.append(Chain(chain_name, raw_sequence, domains))

            result_objects.append(AnarciResultObject(biologic_name, chains))
        return result_objects

    def get_result_by_biologic_name(
        self, biologic_name: str
    ) -> Optional[AnarciResultObject]:
        for result in self.results:
            if result.biologic_name == biologic_name:
                return result
        return None

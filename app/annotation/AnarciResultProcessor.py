import itertools
import logging
from typing import List, Optional, Dict

from anarci import run_anarci

from app.annotation.AntibodyRegionAnnotator import AntibodyRegionAnnotator
from app.utils.types import Chain, Domain


class AnarciResultObject:
    def __init__(self, biologic_name: str, chains: List[Chain]) -> None:
        self.biologic_name: str = biologic_name
        self.chains: List[Chain] = chains

    def __repr__(self) -> str:
        return f"AnarciResultObject(biologic_name={self.biologic_name}, chains={self.chains})"


class AnarciResultProcessor:
    def __init__(self, input_dict: Dict[str, Dict[str, str]], numbering_scheme: str = "imgt") -> None:
        self.original_scheme = numbering_scheme
        self.numbering_scheme = numbering_scheme
        self.results = self._process_results(input_dict)

    def _run_anarci_with_fallback(self, anarci_input, scheme, **kwargs):
        # If CGG, use Kabat for ANARCI, but keep track of original scheme
        anarci_scheme = "kabat" if scheme == "cgg" else scheme
        try:
            return run_anarci(anarci_input, scheme=anarci_scheme, **kwargs), scheme
        except Exception as e:
            if anarci_scheme != "imgt":
                logging.warning(f"ANARCI failed with scheme '{anarci_scheme}' ({e}), retrying with 'imgt'.")
                return run_anarci(anarci_input, scheme="imgt", **kwargs), "imgt"
            else:
                raise

    def _process_results(self, input_dict: Dict[str, Dict[str, str]]) -> List[AnarciResultObject]:
        result_objects = []
        for biologic_name, chains_dict in input_dict.items():
            chains = []
            for chain_name, chain_seq in chains_dict.items():
                anarci_input = [(chain_name, chain_seq)]
                (sequences, numbered, alignment_details, hit_tables), used_scheme = self._run_anarci_with_fallback(
                    anarci_input,
                    scheme=self.numbering_scheme,
                    allowed_species=["human", "mouse", "rat"],
                    assign_germline=True
                )
                # Only one chain per call, so index 0
                domains = []
                seq_name, raw_sequence = sequences[0]
                seq_numbered = numbered[0]
                seq_aligns = alignment_details[0]
                seq_hits = hit_tables[0]
                # Prepare hit_table header and rows
                hit_table_header = seq_hits[0] if seq_hits and len(seq_hits) > 0 else []
                hit_table_rows = seq_hits[1:] if seq_hits and len(seq_hits) > 1 else []
                # Group hit_table by (species, chain_type) and select best bitscore
                best_hits_by_chain = {}
                if hit_table_header and hit_table_rows:
                    id_idx = hit_table_header.index('id') if 'id' in hit_table_header else None
                    bitscore_idx = hit_table_header.index('bitscore') if 'bitscore' in hit_table_header else None
                    for key, group in itertools.groupby(
                            sorted(hit_table_rows, key=lambda row: row[id_idx]),
                            key=lambda row: row[id_idx].split('_')[0] + '_' + row[id_idx].split('_')[
                                1] if id_idx is not None else None
                    ):
                        best_row = max(list(group),
                                       key=lambda row: row[bitscore_idx] if bitscore_idx is not None else 0)
                        best_hits_by_chain[key] = best_row
                # Domains for this chain
                for dom_idx, (numbered_domain, domain_alignment) in enumerate(zip(seq_numbered, seq_aligns)):
                    chain_type = domain_alignment.get('chain_type') if domain_alignment and isinstance(domain_alignment,
                                                                                                       dict) else None
                    species = domain_alignment.get('species') if domain_alignment and isinstance(domain_alignment,
                                                                                                 dict) else None
                    best_hit = None
                    if chain_type and species:
                        key = f"{species}_{chain_type}"
                        best_hit = best_hits_by_chain.get(key)
                    domain_start = domain_alignment.get('query_start')
                    domain_end = domain_alignment.get('query_end')
                    domain = Domain(sequence=raw_sequence[domain_start:domain_end], numbering=numbered_domain,
                                    alignment_details=domain_alignment, hit_table=best_hit, isotype=chain_type,
                                    species=species, germlines=domain_alignment.get("germlines"))
                    # Attach the annotation scheme used for this domain
                    domain.annotation_scheme = used_scheme
                    # Annotate the domain with regions using the correct scheme
                    AntibodyRegionAnnotator.annotate_domain(domain, scheme=used_scheme)
                    domains.append(domain)
                chains.append(Chain(chain_name, raw_sequence, domains))
            result_objects.append(AnarciResultObject(biologic_name, chains))
        return result_objects

    def get_result_by_biologic_name(self, biologic_name: str) -> Optional[AnarciResultObject]:
        for result in self.results:
            if result.biologic_name == biologic_name:
                return result
        return None

from dataclasses import dataclass
from typing import Dict, Literal, Any
from backend.utils.types import Chain, Domain

from backend.numbering.kabat import KABAT_REGIONS
from backend.numbering.chothia import CHOTHIA_REGIONS
from backend.numbering.imgt import IMGT_REGIONS
from backend.numbering.cgg import CGG_REGIONS
from backend.annotation.region_utils import RegionIndexHelper


@dataclass
class AntibodyRegion:
    name: str
    start: Any  # residue number, e.g. (27, 'A')
    stop: Any
    sequence: str

    def to_dict(self):
        def format_pos(pos):
            if isinstance(pos, (list, tuple)):
                if len(pos) == 2 and pos[1] != " ":
                    return f"{pos[0]}{pos[1]}"
                return int(pos[0])
            return pos

        return {
            "name": self.name,
            "start": format_pos(self.start),
            "stop": format_pos(self.stop),
            "sequence": self.sequence,
        }


for _regions in (KABAT_REGIONS, CHOTHIA_REGIONS, IMGT_REGIONS):
    if "L" in _regions and "K" not in _regions:
        _regions["K"] = _regions["L"]

SCHEME_MAP = {
    "imgt": IMGT_REGIONS,
    "kabat": KABAT_REGIONS,
    "chothia": CHOTHIA_REGIONS,
    "cgg": CGG_REGIONS,
}


def get_chain_type(domain: Domain) -> str:
    # Use chain_type from alignment_details if available
    if domain.alignment_details:
        t = domain.alignment_details.get("chain_type", "").upper()
        if t in ("K", "L"):
            return t
    return "H"  # default to heavy


class AntibodyRegionAnnotator:
    @staticmethod
    def annotate_domain(
        domain: Domain, scheme: Literal["imgt", "kabat", "chothia", "cgg"] = "cgg"
    ) -> Domain:
        chain_type = get_chain_type(domain)
        region_defs = SCHEME_MAP[scheme]
        region_map = region_defs[chain_type]
        if not domain.numbering:
            domain.regions = {}
            return domain
        numbering = domain.numbering[0]  # Use only the residue numbering
        pos_to_idx = RegionIndexHelper.build_pos_to_idx(numbering)
        regions: Dict[str, AntibodyRegion] = {}
        for region, (start, stop) in region_map.items():
            start_idx, stop_idx = RegionIndexHelper.find_region_indices(
                pos_to_idx, start, stop
            )
            seq = RegionIndexHelper.extract_region_sequence(
                numbering, start_idx, stop_idx
            )
            regions[region] = AntibodyRegion(region, start, stop, seq)
        # Convert to dict with formatted positions and sequences
        domain.regions = regions
        return domain

    @staticmethod
    def annotate_chain_domains(
        chain: Chain, scheme: Literal["imgt", "kabat", "chothia", "cgg"] = "imgt"
    ) -> Chain:
        # chain_type = get_chain_type(chain)
        for domain in chain.domains:
            AntibodyRegionAnnotator.annotate_domain(domain, scheme)
        return chain

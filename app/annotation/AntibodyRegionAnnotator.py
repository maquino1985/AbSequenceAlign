import logging
from dataclasses import dataclass
from typing import Dict, Literal, Any
from app.utils.types import Chain, Domain
logger = logging.getLogger(__name__)


@dataclass
class AntibodyRegion:
    name: str
    start: Any  # residue number, e.g. (27, 'A')
    stop: Any
    sequence: str


# Robust region definitions for Kabat/Chothia (see http://www.bioinf.org.uk/abs/info.html)
# Each region is a list of residue numbers (number, insertion_code)
# For Kabat/Chothia, heavy and light chains differ
KABAT_REGIONS = {
    'H': {
        'FR1': [(1, ' '), (30, ' ')],
        'CDR1': [(31, ' '), (35, 'A')],
        'FR2': [(36, ' '), (49, ' ')],
        'CDR2': [(50, ' '), (65, ' ')],
        'FR3': [(66, ' '), (94, ' ')],
        'CDR3': [(95, ' '), (102, ' ')],
        'FR4': [(103, ' '), (113, ' ')],
    },
    'L': {
        'FR1': [(1, ' '), (23, ' ')],
        'CDR1': [(24, ' '), (34, ' ')],
        'FR2': [(35, ' '), (49, ' ')],
        'CDR2': [(50, ' '), (56, ' ')],
        'FR3': [(57, ' '), (88, ' ')],
        'CDR3': [(89, ' '), (97, ' ')],
        'FR4': [(98, ' '), (107, ' ')],
    }
}
CHOTHIA_REGIONS = {
    'H': {
        'FR1': [(1, ' '), (26, ' ')],
        'CDR1': [(27, ' '), (32, ' ')],
        'FR2': [(33, ' '), (52, ' ')],
        'CDR2': [(53, ' '), (56, ' ')],
        'FR3': [(57, ' '), (95, ' ')],
        'CDR3': [(96, ' '), (102, ' ')],
        'FR4': [(103, ' '), (113, ' ')],
    },
    'L': {
        'FR1': [(1, ' '), (23, ' ')],
        'CDR1': [(24, ' '), (34, ' ')],
        'FR2': [(35, ' '), (50, ' ')],
        'CDR2': [(51, ' '), (54, ' ')],
        'FR3': [(55, ' '), (88, ' ')],
        'CDR3': [(89, ' '), (97, ' ')],
        'FR4': [(98, ' '), (107, ' ')],
    }
}
IMGT_REGIONS = {
    'H': {
        'FR1': [(1, ' '), (26, ' ')],
        'CDR1': [(27, ' '), (38, ' ')],
        'FR2': [(39, ' '), (55, ' ')],
        'CDR2': [(56, ' '), (65, ' ')],
        'FR3': [(66, ' '), (104, ' ')],
        'CDR3': [(105, ' '), (117, ' ')],
        'FR4': [(118, ' '), (128, ' ')],
    },
    'L': {
        'FR1': [(1, ' '), (26, ' ')],
        'CDR1': [(27, ' '), (38, ' ')],
        'FR2': [(39, ' '), (55, ' ')],
        'CDR2': [(56, ' '), (65, ' ')],
        'FR3': [(66, ' '), (104, ' ')],
        'CDR3': [(105, ' '), (117, ' ')],
        'FR4': [(118, ' '), (129, ' ')],
    }
}
# CGG / AbbVie region definitions (see e.g. https://www.antibodyresource.com/numbering-schemes and internal AbbVie docs)
# These are typically based on Kabat but with specific CDR/FR boundaries for therapeutic antibody engineering.
# Here is a commonly used CGG/AbbVie definition (for both heavy and light chains):
# - FR1: 1-24
# - CDR1: 25-34
# - FR2: 35-49
# - CDR2: 50-65
# - FR3: 66-94
# - CDR3: 95-102
# - FR4: 103-113
CGG_REGIONS = {
    'H': {
        'FR1': [(1, ' '), (24, ' ')],
        'CDR1': [(25, ' '), (34, ' ')],
        'FR2': [(35, ' '), (49, ' ')],
        'CDR2': [(50, ' '), (65, ' ')],
        'FR3': [(66, ' '), (94, ' ')],
        'CDR3': [(95, ' '), (102, ' ')],
        'FR4': [(103, ' '), (113, ' ')],
    },
    'K': {
        'FR1': [(1, ' '), (23, ' ')],
        'CDR1': [(24, ' '), (34, ' ')],
        'FR2': [(35, ' '), (49, ' ')],
        'CDR2': [(50, ' '), (56, ' ')],
        'FR3': [(57, ' '), (88, ' ')],
        'CDR3': [(89, ' '), (97, ' ')],
        'FR4': [(98, ' '), (107, ' ')],
    },
    'L': {
        'FR1': [(1, ' '), (23, ' ')],
        'CDR1': [(24, ' '), (34, ' ')],
        'FR2': [(35, ' '), (49, ' ')],
        'CDR2': [(50, ' '), (56, ' ')],
        'FR3': [(57, ' '), (88, ' ')],
        'CDR3': [(89, ' '), (97, ' ')],
        'FR4': [(98, ' '), (107, ' ')],
    }
}
for _regions in (KABAT_REGIONS, CHOTHIA_REGIONS, IMGT_REGIONS):
    if 'L' in _regions and 'K' not in _regions:
        _regions['K'] = _regions['L']

SCHEME_MAP = {
    'imgt': IMGT_REGIONS,
    'kabat': KABAT_REGIONS,
    'chothia': CHOTHIA_REGIONS,
    'cgg': CGG_REGIONS,
}


def get_chain_type(domain: Domain) -> str:
    # Use chain_type from alignment_details if available
    if domain.alignment_details:
        t = domain.alignment_details.get('chain_type', '').upper()
        if t in ('K', 'L'):
            return t
    return 'H'  # default to heavy


class AntibodyRegionAnnotator:
    @staticmethod
    def annotate_domain(domain: Domain, scheme: Literal['imgt', 'kabat', 'chothia', 'cgg'] = 'cgg') -> Domain:
        chain_type = get_chain_type(domain)
        region_defs = SCHEME_MAP[scheme]
        region_map = region_defs[chain_type]
        if not domain.numbering:
            domain.regions = {}
            return domain
        numbering = domain.numbering
        pos_to_idx = {num[0]: idx for idx, num in enumerate(numbering) if isinstance(num, tuple) and len(num) > 1}
        regions: Dict[str, AntibodyRegion] = {}
        for region, (start, stop) in region_map.items():
            start_idx = pos_to_idx.get(tuple(start))
            stop_idx = pos_to_idx.get(tuple(stop))
            if start_idx is not None and stop_idx is not None:
                seq = ''.join([numbering[i][1] for i in range(start_idx, stop_idx + 1)])
                regions[region] = AntibodyRegion(region, start, stop, seq)
            else:
                regions[region] = AntibodyRegion(region, start, stop, "")
        domain.regions = regions
        return domain

    @staticmethod
    def annotate_chain_domains(chain: Chain, scheme: Literal['imgt', 'kabat', 'chothia'] = 'imgt') -> Chain:
        # chain_type = get_chain_type(chain)
        for domain in chain.domains:
            AntibodyRegionAnnotator.annotate_domain(domain, scheme)
        return chain

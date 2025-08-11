from typing import List, Tuple, Dict, Literal

from backend.numbering_conversion_utils import convert_numbering

# Supported schemes
NumberingScheme = Literal["imgt", "kabat", "chothia"]

# Kabat boundaries (heavy chain)
KABAT_HEAVY = {
    "FR1": lambda pos, ins: 1 <= pos <= 31,
    "CDR1": lambda pos, ins: (pos == 31 and ins) or (31 < pos <= 35),
    "FR2": lambda pos, ins: 36 <= pos <= 49,
    "CDR2": lambda pos, ins: 50 <= pos <= 65,
    "FR3": lambda pos, ins: 66 <= pos <= 94,
    "CDR3": lambda pos, ins: 95 <= pos <= 102,
    "FR4": lambda pos, ins: 103 <= pos <= 113,
}

# Chothia boundaries (heavy chain)
CHOTHIA_HEAVY = {
    "FR1": lambda pos, ins: 1 <= pos <= 26,
    "CDR1": lambda pos, ins: 27 <= pos <= 32,
    "FR2": lambda pos, ins: 33 <= pos <= 52,
    "CDR2": lambda pos, ins: 53 <= pos <= 56,
    "FR3": lambda pos, ins: 57 <= pos <= 94,
    "CDR3": lambda pos, ins: 95 <= pos <= 102,
    "FR4": lambda pos, ins: 103 <= pos <= 113,
}

# IMGT boundaries (heavy chain)
IMGT_HEAVY = {
    "FR1": lambda pos, ins: 1 <= pos <= 26,
    "CDR1": lambda pos, ins: 27 <= pos <= 38,
    "FR2": lambda pos, ins: 39 <= pos <= 55,
    "CDR2": lambda pos, ins: 56 <= pos <= 65,
    "FR3": lambda pos, ins: 66 <= pos <= 104,
    "CDR3": lambda pos, ins: 105 <= pos <= 117,
    "FR4": lambda pos, ins: 118 <= pos <= 128,
}

# Add light chain boundaries for Kabat and Chothia
KABAT_LIGHT = {
    "FR1": lambda pos, ins: 1 <= pos <= 23,
    "CDR1": lambda pos, ins: 24 <= pos <= 34,
    "FR2": lambda pos, ins: 35 <= pos <= 49,
    "CDR2": lambda pos, ins: 50 <= pos <= 56,
    "FR3": lambda pos, ins: 57 <= pos <= 88,
    "CDR3": lambda pos, ins: 89 <= pos <= 97,
    "FR4": lambda pos, ins: 98 <= pos <= 107,
}

CHOTHIA_LIGHT = {
    "FR1": lambda pos, ins: 1 <= pos <= 23,
    "CDR1": lambda pos, ins: 24 <= pos <= 34,
    "FR2": lambda pos, ins: 35 <= pos <= 49,
    "CDR2": lambda pos, ins: 50 <= pos <= 56,
    "FR3": lambda pos, ins: 57 <= pos <= 88,
    "CDR3": lambda pos, ins: 89 <= pos <= 97,
    "FR4": lambda pos, ins: 98 <= pos <= 107,
}

# Update SCHEME_MAP to be keyed by (scheme, chain_type)
SCHEME_MAP = {
    ("imgt", "H"): IMGT_HEAVY,
    (
        "imgt",
        "L",
    ): IMGT_HEAVY,  # IMGT light chain boundaries are similar, can be replaced with IMGT_LIGHT if needed
    ("kabat", "H"): KABAT_HEAVY,
    ("kabat", "L"): KABAT_LIGHT,
    ("chothia", "H"): CHOTHIA_HEAVY,
    ("chothia", "L"): CHOTHIA_LIGHT,
}


def find_kabat_cdrs(
    numbering: List[Tuple[Tuple[int, str], str]], chain_type: str
) -> Dict[str, Tuple[int, int]]:
    """
    Use anchor/motif heuristics to find Kabat CDR boundaries as described at http://www.bioinf.org.uk/abs/info.html
    Returns a dict of region name to (start_idx, end_idx) in the numbering list.
    """
    seq = "".join([aa for (_, aa) in numbering])
    cdrs = {}
    # Example for heavy chain CDR1 (motif: C...W)
    if chain_type == "H":
        # CDR1: starts after first C, ends before first W after C
        c_start = seq.find("C")
        w_after_c = seq.find("W", c_start)
        if c_start != -1 and w_after_c != -1:
            cdrs["CDR1"] = (c_start + 1, w_after_c)
        # CDR2: after first W, before first G after W
        g_after_w = seq.find("G", w_after_c)
        if w_after_c != -1 and g_after_w != -1:
            cdrs["CDR2"] = (w_after_c + 1, g_after_w)
        # CDR3: after last C, to end
        last_c = seq.rfind("C")
        if last_c != -1:
            cdrs["CDR3"] = (last_c + 1, len(seq))
    else:
        # Light chain heuristics (example, real rules are more complex)
        c_start = seq.find("C")
        w_after_c = seq.find("W", c_start)
        if c_start != -1 and w_after_c != -1:
            cdrs["CDR1"] = (c_start + 1, w_after_c)
        g_after_w = seq.find("G", w_after_c)
        if w_after_c != -1 and g_after_w != -1:
            cdrs["CDR2"] = (w_after_c + 1, g_after_w)
        last_c = seq.rfind("C")
        if last_c != -1:
            cdrs["CDR3"] = (last_c + 1, len(seq))
    return cdrs


def annotate_regions(
    numbering: List[Tuple[Tuple[int, str], str]],
    scheme: str = "imgt",
    chain_type: str = "H",
) -> Dict[str, str]:
    """
    Given a list of ((pos, ins), aa), a numbering scheme, and chain type, return region annotations.
    """
    if scheme == "imgt":
        boundaries = SCHEME_MAP[(scheme, chain_type)]
        regions: Dict[str, List[str]] = {k: [] for k in boundaries}
        for (pos, ins), aa in numbering:
            for region, rule in boundaries.items():
                if rule(pos, ins):
                    regions[region].append(aa)
                    break
        return {k: "".join(v) for k, v in regions.items() if v}
    elif scheme == "kabat":
        # Use heuristics for Kabat
        cdrs = find_kabat_cdrs(numbering, chain_type)
        seq = "".join([aa for (_, aa) in numbering])
        kabat_regions: Dict[str, str] = {}
        # Assign regions based on CDR boundaries
        last = 0
        for cdr in ["CDR1", "CDR2", "CDR3"]:
            if cdr in cdrs:
                start, end = cdrs[cdr]
                kabat_regions[f"FR{cdr[-1]}"] = seq[last:start]
                kabat_regions[cdr] = seq[start:end]
                last = end
        kabat_regions["FR4"] = seq[last:]
        return {k: v for k, v in kabat_regions.items() if v}
    elif scheme == "chothia":
        # For demonstration, use same as Kabat; real Chothia heuristics differ
        cdrs = find_kabat_cdrs(numbering, chain_type)
        seq = "".join([aa for (_, aa) in numbering])
        chothia_regions: Dict[str, str] = {}
        last = 0
        for cdr in ["CDR1", "CDR2", "CDR3"]:
            if cdr in cdrs:
                start, end = cdrs[cdr]
                chothia_regions[f"FR{cdr[-1]}"] = seq[last:start]
                chothia_regions[cdr] = seq[start:end]
                last = end
        chothia_regions["FR4"] = seq[last:]
        return {k: v for k, v in chothia_regions.items() if v}
    else:
        raise ValueError(f"Unknown scheme: {scheme}")


def annotate_all_schemes(
    numbering: List[Tuple[Tuple[int, str], str]],
    chain_type: str = "H",
    from_scheme: str = "imgt",
    scheme: str = "all",
) -> Dict[str, Dict[str, str]]:
    """
    Return region annotations for the specified scheme or all supported schemes, converting numbering as needed.
    scheme: "imgt", "kabat", "chothia", or "all" (default: all)
    """
    if chain_type != "H":
        chain_type = "L"
    schemes = ["imgt", "kabat", "chothia"] if scheme == "all" else [scheme]
    out = {}
    for sch in schemes:
        converted = convert_numbering(
            numbering, from_scheme, sch, chain_type=chain_type
        )
        out[sch] = annotate_regions(converted, sch, chain_type)
    return out

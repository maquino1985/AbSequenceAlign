from typing import List, Tuple, Literal

# This is a simplified mapping for demonstration. Real mapping should be based on published tables.
# For a production system, use a comprehensive mapping table or a library like abnumber.

NumberingScheme = Literal["imgt", "kabat", "chothia"]

# Complete mapping for heavy chain (IMGT -> Kabat)
IMGT_TO_KABAT_HEAVY = {i: (i, "") for i in range(1, 118)}
# Insertions (example, real mapping may differ)
IMGT_TO_KABAT_HEAVY.update({32: (31, "A"), 33: (31, "B"), 38: (35, "A"), 39: (35, "B")})

# Complete mapping for light chain (IMGT -> Kabat)
IMGT_TO_KABAT_LIGHT = {i: (i, "") for i in range(1, 111)}
# Insertions (example, real mapping may differ)
IMGT_TO_KABAT_LIGHT.update({27: (26, "A"), 28: (26, "B"), 38: (35, "A"), 39: (35, "B")})

# Complete mapping for heavy chain (IMGT -> Chothia)
IMGT_TO_CHOTHIA_HEAVY = {i: (i, "") for i in range(1, 118)}
# Insertions (example, real mapping may differ)
IMGT_TO_CHOTHIA_HEAVY.update(
    {32: (31, "A"), 33: (31, "B"), 38: (35, "A"), 39: (35, "B")}
)

# Complete mapping for light chain (IMGT -> Chothia)
IMGT_TO_CHOTHIA_LIGHT = {i: (i, "") for i in range(1, 111)}
# Insertions (example, real mapping may differ)
IMGT_TO_CHOTHIA_LIGHT.update(
    {27: (26, "A"), 28: (26, "B"), 38: (35, "A"), 39: (35, "B")}
)


# For demonstration, only a partial mapping is provided. Real mapping is more complex.
def convert_imgt_to_kabat(
    imgt_numbering: List[Tuple[Tuple[int, str], str]], chain_type: str = "H"
) -> List[Tuple[Tuple[int, str], str]]:
    if chain_type == "L":
        mapping = IMGT_TO_KABAT_LIGHT
    else:
        mapping = IMGT_TO_KABAT_HEAVY
    kabat_numbering = []
    for (imgt_pos, imgt_ins), aa in imgt_numbering:
        if imgt_pos in mapping:
            kabat_pos, kabat_ins = mapping[imgt_pos]
            kabat_numbering.append(((kabat_pos, kabat_ins), aa))
        else:
            kabat_numbering.append(((imgt_pos, imgt_ins), aa))
    return kabat_numbering


def convert_imgt_to_chothia(
    imgt_numbering: List[Tuple[Tuple[int, str], str]], chain_type: str = "H"
) -> List[Tuple[Tuple[int, str], str]]:
    if chain_type == "L":
        mapping = IMGT_TO_CHOTHIA_LIGHT
    else:
        mapping = IMGT_TO_CHOTHIA_HEAVY
    chothia_numbering = []
    for (imgt_pos, imgt_ins), aa in imgt_numbering:
        if imgt_pos in mapping:
            chothia_pos, chothia_ins = mapping[imgt_pos]
            chothia_numbering.append(((chothia_pos, chothia_ins), aa))
        else:
            chothia_numbering.append(((imgt_pos, imgt_ins), aa))
    return chothia_numbering


def convert_numbering(
    numbering: List[Tuple[Tuple[int, str], str]],
    from_scheme: str,
    to_scheme: str,
    chain_type: str = "H",
) -> List[Tuple[Tuple[int, str], str]]:
    if from_scheme == to_scheme:
        return numbering
    if from_scheme == "imgt" and to_scheme == "kabat":
        return convert_imgt_to_kabat(numbering, chain_type)
    if from_scheme == "imgt" and to_scheme == "chothia":
        return convert_imgt_to_chothia(numbering, chain_type)
    raise NotImplementedError(
        f"Conversion from {from_scheme} to {to_scheme} not implemented."
    )

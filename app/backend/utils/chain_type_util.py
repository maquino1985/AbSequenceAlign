from backend.core.constants import ChainType


class ChainTypeUtil:
    @staticmethod
    def extract_chain_type(seq_aligns) -> ChainType:
        """
        Extracts the chain type from a sequence alignment dictionary.

        Args:
            seq_aligns (dict): A dictionary containing sequence alignments with keys as chain labels.

        Returns:
            str: The chain type extracted from the first key in the dictionary.
        """
        if not seq_aligns:
            return ChainType.UNKNOWN

        # Get the first key in the dictionary
        best_alignment = next(iter(seq_aligns))
        chain_type = best_alignment.get("chain_type")
        # Extract the chain type from the key
        if "h" in chain_type.lower():
            return ChainType.HEAVY
        elif chain_type.lower() in ["k", "l", "light"]:
            return ChainType.LIGHT
        elif "b" in chain_type.lower():
            return ChainType.BETA
        elif "a" in chain_type.lower():
            return ChainType.ALPHA
        else:
            raise ValueError(f"Unknown chain type for key: {best_alignment}")

from typing import List, Tuple, Dict, Any


class RegionIndexHelper:
    @staticmethod
    def build_pos_to_idx(numbering: List[Tuple[Any, Any]]) -> Dict[Any, int]:
        """
        Build a mapping from (pos, ins) to index in numbering.
        """
        return {
            num[0]: idx
            for idx, num in enumerate(numbering)
            if isinstance(num, tuple) and len(num) > 1
        }

    @staticmethod
    def find_region_indices(
        pos_to_idx: Dict[Any, int], start: Any, stop: Any
    ) -> Tuple[int, int]:
        start_key = tuple(start)
        stop_key = tuple(stop)
        start_idx = pos_to_idx.get(start_key)
        stop_idx = pos_to_idx.get(stop_key)
        # Fallback: find closest available position if not found
        if start_idx is None:
            for k, idx in pos_to_idx.items():
                if (k[0] > start[0]) or (k[0] == start[0] and k[1] >= start[1]):
                    start_idx = idx
                    break
        if stop_idx is None:
            for k, idx in reversed(list(pos_to_idx.items())):
                if (k[0] < stop[0]) or (k[0] == stop[0] and k[1] <= stop[1]):
                    stop_idx = idx
                    break
        return start_idx, stop_idx

    @staticmethod
    def extract_region_sequence(
        numbering: List[Tuple[Any, Any]], start_idx: int, stop_idx: int
    ) -> str:
        if start_idx is not None and stop_idx is not None and start_idx <= stop_idx:
            return "".join([numbering[i][1] for i in range(start_idx, stop_idx + 1)])
        return ""

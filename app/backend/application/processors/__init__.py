"""
Processors package for biologic entities.
"""

from .biologic_processor import BiologicProcessorImpl
from .strategy_biologic_processor import StrategyBiologicProcessorImpl

__all__ = [
    "BiologicProcessorImpl",
    "StrategyBiologicProcessorImpl",
]

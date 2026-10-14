"""HeatGuard - rule-based heatwave early-warning & advisory expert system."""

from .engine import InferenceEngine
from .knowledge_base import RULES, SOURCES


def build_engine() -> InferenceEngine:
    return InferenceEngine(RULES)


__all__ = ["InferenceEngine", "RULES", "SOURCES", "build_engine"]

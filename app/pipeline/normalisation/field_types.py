"""
Field type constants and processing method labels for the normalisation pipeline.
"""

from __future__ import annotations


class ProcessingMethod:
    PRESERVE = "PRESERVE"
    CALENDAR = "CALENDAR"
    NUMERIC = "NUMERIC"
    VOCABULARY = "VOCABULARY"
    GEOGRAPHIC = "GEOGRAPHIC"
    REPOSITORY = "REPOSITORY"
    TRANSLITERATION = "TRANSLITERATION"
    CHARACTER_MAP = "CHARACTER_MAP"
    NMT = "NMT"
    LLM = "LLM"
    UNRESOLVED = "UNRESOLVED"


STRATEGY_CONFIDENCE: dict[str, float] = {
    ProcessingMethod.PRESERVE: 1.0,
    ProcessingMethod.CALENDAR: 0.98,
    ProcessingMethod.NUMERIC: 0.90,
    ProcessingMethod.VOCABULARY: 0.95,
    ProcessingMethod.GEOGRAPHIC: 0.90,
    ProcessingMethod.REPOSITORY: 0.97,
    ProcessingMethod.TRANSLITERATION: 0.80,
    ProcessingMethod.CHARACTER_MAP: 0.85,
    ProcessingMethod.NMT: 0.80,
    ProcessingMethod.LLM: 0.70,
    ProcessingMethod.UNRESOLVED: 0.0,
}


GEOGRAPHIC_FIELDS: list[str] = [
    "nationality",
    "country",
    "country_of_residence",
    "place_of_birth",
    "city",
]

PROSE_FIELDS: list[str] = [
    # T6-1: alias/AKA fields — route to NMT (Strategy H) before transliteration
    "alias",
    "aka",
    "also_known_as",
    "notes",
    "remarks",
    "free_text",
    # Original prose fields
    "nature_of_business",
    "business_purpose",
    "accounting_policies",
    "locality_information",
    "capital_changes_narrative",
    "unstructured_text",
]

"""Deterministic field type detector for sentence tab auto mode."""

from __future__ import annotations

import re


def detect_field_type(text: str, language: str = "") -> tuple[str, float]:
    """Infer likely KYC field type from pasted text."""
    text_stripped = text.strip()

    if re.match(r"^[\w._%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$", text_stripped):
        return ("email", 0.95)

    date_patterns = [
        r"\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}",
        r"\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2}",
        r"[٠-٩]{1,2}[/\-.][٠-٩]{1,2}[/\-.][٠-٩]{2,4}",
        r"令和|平成|昭和|大正|明治",
        r"\d{1,2}\s+\w+\s+\d{4}",
        r"\d{4}年\d{1,2}月\d{1,2}日",
    ]
    for pattern in date_patterns:
        if re.search(pattern, text_stripped):
            return ("date_of_birth", 0.85)

    if re.match(r"^[A-Z0-9][A-Z0-9\-]{5,19}$", text_stripped.upper()) and " " not in text_stripped:
        return ("id_number", 0.85)

    street_keywords = [
        "street", "road", "avenue", "boulevard", "lane", "drive", "place",
        "rue", "via", "calle", "strasse", "straße", "ulica", "улица",
        "شارع", "طريق", "通り", "路", "街", "로",
    ]
    lower_text = text_stripped.lower()
    if any(kw in lower_text for kw in street_keywords):
        return ("address", 0.85)

    tokens = text_stripped.split()
    if 1 <= len(tokens) <= 4 and not _has_sentence_structure(text_stripped):
        latin_legal_suffixes = {
            "llc", "ltd", "inc", "corp", "plc", "gmbh", "sarl", "sas", "sa",
            "bv", "nv", "ag", "kg", "oy", "ab", "as", "srl", "spa",
        }
        last_token = tokens[-1].lower().rstrip(".")
        if last_token in latin_legal_suffixes:
            return ("company_name", 0.90)
        return ("person_name", 0.80)

    if len(tokens) > 8 or _has_sentence_structure(text_stripped):
        return ("nature_of_business", 0.60)

    return ("unstructured_text", 0.50)


def _has_sentence_structure(text: str) -> bool:
    has_verb_indicators = bool(re.search(r"\b(is|are|was|were|has|have|the|and|of|in)\b", text, re.I))
    has_punctuation = bool(re.search(r"[,;:।。、]", text))
    return has_verb_indicators or has_punctuation

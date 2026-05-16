"""Tests for Epic 07 Strategy G — Character Map Normaliser.

No mocks. All tests call apply_character_map() directly or route_field().
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for p in (str(ROOT), str(SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest

from app.pipeline.normalisation.character_map_normaliser import apply_character_map


# ── Existing language handlers — must still pass ───────────────────────────────

def test_german_umlaut_expansion():
    assert apply_character_map("Müller", "de", "person_name")["normalised_form"] == "MUELLER"


def test_german_umlaut_drop_variant():
    assert "MULLER" in apply_character_map("Müller", "de", "person_name")["allowed_variants"]


def test_german_sz():
    assert apply_character_map("Straße", "de", "person_name")["normalised_form"] == "STRASSE"


def test_french_accent():
    assert apply_character_map("Élodie", "fr", "person_name")["normalised_form"] == "ELODIE"


def test_spanish_n_tilde_primary():
    assert apply_character_map("Muñoz", "es", "person_name")["normalised_form"] == "MUNOZ"


def test_spanish_n_tilde_ny_variant():
    assert "MUNYOZ" in apply_character_map("Muñoz", "es", "person_name")["allowed_variants"]


def test_english_obrien_variant():
    r = apply_character_map("O'Brien", "en", "person_name")
    assert "OBRIEN" in r["allowed_variants"] or "O BRIEN" in r["allowed_variants"]


# ── New language handlers ─────────────────────────────────────────────────────

def test_turkish_dotted_i():
    assert apply_character_map("İstanbul", "tr", "person_name")["normalised_form"] == "ISTANBUL"


def test_turkish_dotless_i():
    assert apply_character_map("Işık", "tr", "person_name")["normalised_form"] == "ISIK"


def test_turkish_soft_g():
    assert apply_character_map("Ağaoğlu", "tr", "person_name")["normalised_form"] == "AGAOGLU"


def test_dutch_ij_ligature():
    assert apply_character_map("Ĳsselmeer", "nl", "person_name")["normalised_form"] == "IJSSELMEER"


def test_scandinavian_ae():
    assert apply_character_map("Ærø", "da", "person_name")["normalised_form"] == "AERO"


def test_scandinavian_o_stroke():
    assert apply_character_map("Bjørn", "no", "person_name")["normalised_form"] == "BJORN"


def test_scandinavian_a_ring():
    assert apply_character_map("Åberg", "sv", "person_name")["normalised_form"] == "ABERG"


def test_polish_l_stroke():
    assert apply_character_map("Łódź", "pl", "person_name")["normalised_form"] == "LODZ"


def test_polish_nasal_a():
    assert apply_character_map("Wąsik", "pl", "person_name")["normalised_form"] == "WASIK"


def test_portuguese_tilde():
    assert apply_character_map("João", "pt", "person_name")["normalised_form"] == "JOAO"


def test_portuguese_cedilla():
    assert apply_character_map("Gonçalves", "pt", "person_name")["normalised_form"] == "GONCALVES"


# ── Non-Latin returns None ─────────────────────────────────────────────────────

def test_arabic_returns_none():
    assert apply_character_map("محمد", "ar", "person_name") is None


def test_japanese_returns_none():
    assert apply_character_map("田中", "ja", "person_name") is None


# ── Router ─────────────────────────────────────────────────────────────────────

def test_german_routes_to_character_map():
    # Router requires Flask app context
    import os
    os.environ.setdefault("FLASK_ENV", "development")

    from app import create_app
    flask_app = create_app("development")
    with flask_app.app_context():
        from app.pipeline.normalisation.router import route_field
        r = route_field({"original_text": "Müller", "field_type": "person_name", "language": "de"})
        assert r["processing_method"] == "CHARACTER_MAP"
        assert r["normalised_form"] == "MUELLER"

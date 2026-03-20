import unicodedata


def to_normalised_form(text: str) -> str:
    """Strip diacritics and return uppercase ASCII — the canonical matching form."""
    nfkd = unicodedata.normalize("NFKD", text)
    return nfkd.encode("ascii", "ignore").decode().upper()

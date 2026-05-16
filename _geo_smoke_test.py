from app.pipeline.normalisation.geographic_lookup import lookup_geographic, validate_hierarchy

tests = [
    ("\u0633\u0639\u0648\u062f\u064a", "nationality", "ar", "SAUDI ARABIA"),
    ("Tokyo", "city", "en", "TOKYO"),
    ("Germany", "nationality", "en", "GERMANY"),
    ("GmbH", "legal_form", "de", None),
    ("", "nationality", "en", None),
]
for text, ft, lang, expected in tests:
    r = lookup_geographic(text, ft, lang)
    got = r["normalised_form"] if r else None
    status = "PASS" if got == expected else "FAIL"
    print(f"{status}: {repr(text)} -> {got!r}  (expected {expected!r})")

v, reason = validate_hierarchy("Tokyo", "Tokyo", "Germany")
print(f"hierarchy Tokyo/Germany valid={v}, reason={reason}")

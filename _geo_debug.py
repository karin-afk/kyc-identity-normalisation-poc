import sys
from pathlib import Path
sys.path.insert(0, str(Path(".") / "src"))

from app import create_app

# Simulate exactly what the test fixture does
app = create_app("testing")
ctx = app.app_context()
ctx.push()

from app.pipeline.normalisation.geographic_lookup import (
    _ensure_index, _ALIAS_INDEX, _normalise_text, lookup_geographic, _INDEX_BUILT
)

print("=== After create_app (fixture equivalent) ===")
print(f"_INDEX_BUILT: {_INDEX_BUILT}")
print(f"_ALIAS_INDEX size: {len(_ALIAS_INDEX)}")

_ensure_index()
print(f"\n=== After explicit _ensure_index() ===")
print(f"_INDEX_BUILT: {_INDEX_BUILT}")
print(f"_ALIAS_INDEX size: {len(_ALIAS_INDEX)}")

text = "\u0623\u0644\u0645\u0627\u0646\u064a\u0627"  # ألمانيا
key = _normalise_text(text)
print(f"\n=== Normalise check ===")
print(f"Input: {repr(text)}")
print(f"Normalised key: {repr(key)}")
print(f"Key in _ALIAS_INDEX: {key in _ALIAS_INDEX}")

# Count non-ASCII keys
non_ascii = [(k, v['english_name']) for k, v in _ALIAS_INDEX.items() if any(ord(c) > 127 for c in k)]
print(f"\nNon-ASCII alias entries: {len(non_ascii)}")
if non_ascii:
    print(f"Sample: {non_ascii[:3]}")

print(f"\n=== Direct lookup ===")
result = lookup_geographic(text, "nationality", "ar")
print(f"Result: {result}")

ctx.pop()


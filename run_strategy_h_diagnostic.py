"""
T-8-4: Strategy H (NMT) isolated sub-diagnostic.

Bypasses the router entirely and calls apply_nmt() directly.
Reports whether Azure credentials are configured, and for each test case:
  - PASS   : apply_nmt returned a result dict (credentials present, call succeeded)
  - SKIP   : apply_nmt returned None due to missing credentials (expected in CI)
  - FAIL   : apply_nmt raised an exception

Run:
    python run_strategy_h_diagnostic.py

The script exits with code 0 whether credentials are present or absent.
SKIP results are not failures — they mean "routing is correct, translation
quality requires Azure credentials to verify."
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("LLM_ENABLED", "false")
os.environ.setdefault("CLASSIFIER_MODE", "regex")

# ---------------------------------------------------------------------------
# Test cases — representative subset of H.1–H.12
# Five inputs spanning alias connector detection and invoice prose,
# covering Russian, Chinese, Greek, French, and Arabic.
# ---------------------------------------------------------------------------
# (id, description, text, field_type, language, expected_keywords)
# expected_keywords: words that SHOULD appear in the translated output
# (case-insensitive).  Only checked when credentials are present.
# ---------------------------------------------------------------------------
H_TESTS = [
    (
        "H.1",
        "Russian alias with prose connector по прозвищу",
        "Александр по прозвищу Саша",
        "alias",
        "ru",
        ["alexander", "sasha"],
    ),
    (
        "H.2",
        "Chinese alias connector 又名",
        "王强又名王小强",
        "alias",
        "zh",
        ["wang"],
    ),
    (
        "H.3",
        "Greek alias γνωστός ως",
        "γνωστός ως Νίκος",
        "alias",
        "el",
        ["known", "nikos"],
    ),
    (
        "H.7",
        "Arabic invoice prose with amount",
        "تاريخ الاستحقاق ٠٥/٠٩/٢٠٢٦ والمبلغ ١٢٬٥٠٠ ريال",
        "free_text",
        "ar",
        ["date", "amount"],
    ),
    (
        "H.10",
        "Russian invoice prose with date and amount",
        "Срок оплаты: 05.09.2026, сумма: 12 500 руб.",
        "free_text",
        "ru",
        ["date", "amount", "2026"],
    ),
]


def _credentials_present() -> bool:
    return bool(
        os.environ.get("AZURE_TRANSLATOR_ENDPOINT", "")
        and os.environ.get("AZURE_TRANSLATOR_KEY", "")
    )


def _sdk_available() -> bool:
    try:
        import azure.ai.translation.text  # noqa: F401
        return True
    except ImportError:
        return False


def main() -> None:
    from app import create_app
    app = create_app()

    with app.app_context():
        from app.pipeline.normalisation.nmt_translator import apply_nmt

        creds = _credentials_present()
        sdk = _sdk_available()
        can_translate = creds and sdk
        print()
        print("Strategy H (NMT) — isolated sub-diagnostic")
        print("=" * 60)
        print(f"Azure credentials configured: {'YES' if creds else 'NO'}")
        print(f"azure-ai-translation-text SDK: {'installed' if sdk else 'NOT INSTALLED'}")
        if not can_translate:
            reasons = []
            if not creds:
                reasons.append("no credentials")
            if not sdk:
                reasons.append("SDK not installed (pip install azure-ai-translation-text)")
            print(f"Translation not available: {'; '.join(reasons)}")
            print("All tests will SKIP — routing was verified by T6.")
        print()

        passed = 0
        skipped = 0
        failed = 0

        for tid, description, text, field_type, language, keywords in H_TESTS:
            try:
                result = apply_nmt(text, field_type, language)
            except Exception as exc:
                print(f"FAIL  {tid}: apply_nmt() raised {type(exc).__name__}: {exc}")
                failed += 1
                continue

            if result is None:
                if can_translate:
                    # Credentials + SDK present but call returned None — unexpected
                    print(f"FAIL  {tid}: apply_nmt() returned None despite credentials + SDK being available")
                    print(f"            text={repr(text[:60])}")
                    failed += 1
                else:
                    reason = "no SDK" if not sdk else "no credentials"
                    print(f"SKIP  {tid}: {reason} — routing verified by T6; translation quality TBD")
                    skipped += 1
                continue

            # result is a dict — check structure
            method = result.get("processing_method", "")
            normalised = result.get("normalised_form", "")

            structural_ok = (
                method == "NMT"
                and isinstance(normalised, str)
                and len(normalised.strip()) > 0
            )

            if not structural_ok:
                print(f"FAIL  {tid}: unexpected result structure: method={method!r} normalised={normalised!r}")
                failed += 1
                continue

            # Keyword check (only when translation is available and call succeeded)
            if can_translate and keywords:
                normalised_lower = normalised.lower()
                missing = [kw for kw in keywords if kw.lower() not in normalised_lower]
                if missing:
                    print(
                        f"WARN  {tid}: translated but missing expected keywords {missing}\n"
                        f"            normalised_form={normalised!r}"
                    )
                    # Warn only — NMT phrasing varies; don't hard-fail on keywords
                else:
                    print(f"PASS  {tid}: {normalised!r}")
            else:
                print(f"PASS  {tid}: {normalised!r}")

            passed += 1

        print()
        print("-" * 60)
        print(f"Results: {passed} passed, {skipped} skipped (no credentials), {failed} failed")
        if skipped and not can_translate:
            print()
            if not sdk:
                print("NOTE: Install SDK to enable translation:  pip install azure-ai-translation-text")
            if not creds:
                print("NOTE: Set AZURE_TRANSLATOR_ENDPOINT + AZURE_TRANSLATOR_KEY to verify")
            print("      translation output quality.")
        print()

        sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

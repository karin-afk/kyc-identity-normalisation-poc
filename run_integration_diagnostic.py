#!/usr/bin/env python3
"""
Integration Diagnostic Runner — Sentence Tab Pipeline
======================================================

Runs every test example through the REAL pipeline with NO mocks:
  - Real GPT-4o-mini call (OPENAI_API_KEY must be set in .env)
  - Real field_type_detector.detect_field_type()
  - Real app.pipeline.orchestrator.process_field_row()
  - Real app.pipeline.normalisation.router.route_field()
  - Real strategy modules (A, B, C, D, E, F, G)

For each example prints and records:
  Step 1  GPT-4o-mini classification — what it returned vs what was expected
  Step 2  Orchestrator input — what was passed in
  Step 3  Router output — which strategy ran, what the result was
  Step 4  Final comparison — expected vs actual normalised form

Output saved to: reports/integration-report.md

Usage (from repo root):
    python run_integration_diagnostic.py

Requirements:
    OPENAI_API_KEY must be set in .env
    Flask app dependencies installed (pip install -r requirements.txt)
"""

import sys
import os
import time
import traceback
from datetime import datetime
from pathlib import Path

# ── Path setup ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=True)
except ImportError:
    pass

# Create Flask app context so app/ imports work
os.environ.setdefault("FLASK_ENV", "development")

# ── Test cases ─────────────────────────────────────────────────────────────────
# Format:
#   (id, description, paste_text,
#    expected_field_type, expected_language,
#    expected_normalised_form, expected_method,
#    notes)
#
# expected_normalised_form = None means we expect UNRESOLVED / review queue
# expected_method can be a list of acceptable values

TEST_CASES = [

    # ── Strategy A — Preserve ──────────────────────────────────────────────────
    ("A.1", "Passport number",
     "TK1234567",
     "passport_no", "en",
     "TK1234567", "PRESERVE",
     "Must come back byte-for-byte identical"),

    ("A.2", "Registration number",
     "DE123456789",
     "registration_no", "en",
     "DE123456789", "PRESERVE",
     "Must come back byte-for-byte identical"),

    ("A.3", "Email address",
     "test.user@example.com",
     "email", "en",
     "test.user@example.com", "PRESERVE",
     "Must come back byte-for-byte identical"),

    # ── Strategy B — Calendar ──────────────────────────────────────────────────
    ("B.1", "Thai Buddhist Era date",
     "2568/5/8",
     "date_of_birth", "th",
     "2025-05-08", "CALENDAR",
     "2568 BE minus 543 = 2025 CE"),

    ("B.2", "Japanese Reiwa era date",
     "令和5年7月3日",
     "date_of_birth", "ja",
     "2023-07-03", "CALENDAR",
     "Reiwa 5 = 2023"),

    ("B.3", "Japanese Showa era date",
     "昭和60年3月12日",
     "date_of_birth", "ja",
     "1985-03-12", "CALENDAR",
     "Showa 60 = 1985"),

    ("B.4", "Hijri date with Arabic-Indic digits",
     "١٤٤٥/٠٩/٠١",
     "date_of_birth", "ar",
     "2024-03-11", "CALENDAR",
     "Arabic-Indic digits converted then Hijri→Gregorian"),

    ("B.5", "Solar Hijri date",
     "1404/2/15",
     "date_of_birth", "fa",
     "2025-05-05", "CALENDAR",
     "Persian Solar Hijri calendar"),

    ("B.6", "Minguo (Taiwan ROC) date",
     "114/5/8",
     "date_of_birth", "zh",
     "2025-05-08", ["CALENDAR"],
     "Minguo 114 + 1911 = 2025"),

    # ── Strategy B — Numeric ───────────────────────────────────────────────────
    ("B.7", "Japanese triangle negative",
     "△4,191",
     "total_assets", "ja",
     "-4191", "NUMERIC",
     "Japanese accounting triangle notation for negative"),

    ("B.8", "Full-width parenthetical negative",
     "（4,191）",
     "total_assets", "ja",
     "-4191", "NUMERIC",
     "Full-width parentheses negative"),

    ("B.9", "European number format",
     "1.234.567,89",
     "total_assets", "de",
     "1234567.89", "NUMERIC",
     "Period=thousands, comma=decimal in German format"),

    ("B.10", "Swiss apostrophe number format",
     "1'234'567.89",
     "total_assets", "fr",
     "1234567.89", "NUMERIC",
     "Swiss apostrophe thousands separator"),

    ("B.11", "Arabic-Indic digits",
     "٠١٢٣٤٥٦٧٨٩",
     "id_no", "ar",
     "٠١٢٣٤٥٦٧٨٩", "PRESERVE",
     "Arabic-Indic digits in an ID field must be preserved verbatim (Strategy A)"),

    # ── Strategy C — Vocabulary ────────────────────────────────────────────────
    ("C.1", "Japanese legal form KK",
     "株式会社",
     "legal_form", "ja",
     "KK", "VOCABULARY",
     "Most common Japanese corporate form"),

    ("C.2", "German GmbH",
     "GmbH",
     "legal_form", "de",
     "GMBH", "VOCABULARY",
     "German limited liability company"),

    ("C.3", "Russian LLC",
     "ООО",
     "legal_form", "ru",
     "LLC", "VOCABULARY",
     "Russian OOO = LLC"),

    ("C.4", "Japanese status active",
     "現役",
     "status", "ja",
     "ACTIVE", "VOCABULARY",
     "Active status in Japanese"),

    ("C.5", "Arabic status dissolved",
     "منتهي",
     "status", "ar",
     "DISSOLVED", "VOCABULARY",
     "Dissolved status in Arabic"),

    ("C.6", "Japanese role director",
     "取締役",
     "role", "ja",
     "DIRECTOR", "VOCABULARY",
     "Standard director role"),

    ("C.7", "Japanese role representative director",
     "代表取締役",
     "role", "ja",
     "REPRESENTATIVE DIRECTOR", "VOCABULARY",
     "Most senior role in Japanese company"),

    ("C.8", "German status dissolved",
     "aufgelöst",
     "status", "de",
     "DISSOLVED", "VOCABULARY",
     "German dissolved status"),

    ("C.9", "Greek legal form SA",
     "Α.Ε.",
     "legal_form", "el",
     "SA", "VOCABULARY",
     "Greek Anonymi Etaireia = SA"),

    # ── Strategy D — Geographic ────────────────────────────────────────────────
    ("D.1", "Country name in Arabic",
     "ألمانيا",
     "nationality", "ar",
     "GERMANY", "GEOGRAPHIC",
     "Germany in Arabic"),

    ("D.2", "Country name in Japanese",
     "日本",
     "nationality", "ja",
     "JAPAN", "GEOGRAPHIC",
     "Japan in Japanese"),

    ("D.3", "Country name in Russian",
     "Германия",
     "nationality", "ru",
     "GERMANY", "GEOGRAPHIC",
     "Germany in Russian"),

    ("D.4", "Country name in Greek",
     "Γερμανία",
     "nationality", "el",
     "GERMANY", "GEOGRAPHIC",
     "Germany in Greek"),

    # ── Strategy F — Transliteration ──────────────────────────────────────────
    ("F.1", "Russian female name",
     "Наталья",
     "person_name", "ru",
     "NATALYA", ["TRANSLITERATION", "TRANSLITERATE"],
     "BGN/PCGN standard"),

    ("F.2", "Russian male name",
     "Александр",
     "person_name", "ru",
     "ALEKSANDR", ["TRANSLITERATION", "TRANSLITERATE"],
     "BGN/PCGN standard"),

    ("F.3", "Greek male name",
     "Νίκος",
     "person_name", "el",
     "NIKOS", ["TRANSLITERATION", "TRANSLITERATE"],
     "Greek to Latin"),

    ("F.4", "Japanese surname",
     "田中",
     "person_name", "ja",
     "TANAKA", ["TRANSLITERATION", "TRANSLITERATE"],
     "Hepburn romanisation"),

    ("F.5", "Chinese name",
     "王小明",
     "person_name", "zh",
     "WANG XIAOMING", ["TRANSLITERATION", "TRANSLITERATE"],
     "Pinyin romanisation"),

    # ── Strategy G — Character maps ────────────────────────────────────────────
    ("G.1", "German umlaut expansion",
     "Müller",
     "person_name", "de",
     "MUELLER", "CHARACTER_MAP",
     "ü→UE primary form, MULLER variant"),

    ("G.2", "German ß",
     "Straße",
     "person_name", "de",
     "STRASSE", "CHARACTER_MAP",
     "ß→SS"),

    ("G.3", "Spanish ñ",
     "Muñoz",
     "person_name", "es",
     "MUNOZ", "CHARACTER_MAP",
     "ñ→N primary, MUNYOZ variant"),

    ("G.4", "Turkish dotted I",
     "İstanbul",
     "person_name", "tr",
     "ISTANBUL", "CHARACTER_MAP",
     "İ (U+0130) → I"),

    ("G.5", "Polish ł",
     "Łódź",
     "person_name", "pl",
     "LODZ", "CHARACTER_MAP",
     "Ł→L, ó→O, ź→Z"),

    ("G.6", "Scandinavian Æ",
     "Ærø",
     "person_name", "da",
     "AERO", "CHARACTER_MAP",
     "Æ→AE, ø→O"),

    ("G.7", "Portuguese tilde",
     "João",
     "person_name", "pt",
     "JOAO", "CHARACTER_MAP",
     "ã→A"),

    # ── Unresolved — should route to review ───────────────────────────────────
    ("I.1", "Arabic person name (unresolved)",
     "محمد عبد الله",
     "person_name", "ar",
     None, "UNRESOLVED",
     "Arabic names cannot be deterministically transliterated — correct to route to review"),

# ── Compound names (harder than single tokens) ─────────────────────────────
    ("F.6", "Japanese full name surname + given",
     "田中 太郎",
     "person_name", "ja",
     "TANAKA TARO", ["TRANSLITERATION", "TRANSLITERATE"],
     "Compound Japanese name — expected to fail until Epic 06 wired"),

    ("F.7", "Russian full name with patronymic",
     "Иванова Наталья Александровна",
     "person_name", "ru",
     "IVANOVA NATALYA ALEKSANDROVNA", ["TRANSLITERATION", "TRANSLITERATE"],
     "Russian three-part name — expected to fail until Epic 06 wired"),

    ("F.8", "Chinese full name",
     "王小明",
     "person_name", "zh",
     "WANG XIAOMING", ["TRANSLITERATION", "TRANSLITERATE"],
     "Already in suite but keeping for reference"),

    ("F.9", "Greek full name",
     "Νίκος Παπαδόπουλος",
     "person_name", "el",
     "NIKOS PAPADOPOULOS", ["TRANSLITERATION", "TRANSLITERATE"],
     "Compound Greek name — expected to fail until Epic 06 wired"),

    ("F.10", "Korean full name",
     "이민준",
     "person_name", "ko",
     "I MINJUN", ["TRANSLITERATION", "TRANSLITERATE"],
     "Korean name romanisation"),

    # ── Legal form embedded in company name (suffix extraction) ────────────────
    ("C.10", "Japanese legal form at end of company name",
     "三菱商事株式会社",
     "company_name", "ja",
     "KK", "VOCABULARY",
     "Suffix 株式会社 must be extracted from full company name string"),

    ("C.11", "German legal form at end of company name",
     "Müller & Söhne GmbH",
     "company_name", "de",
     "GMBH", "VOCABULARY",
     "Suffix GmbH must be extracted from full string"),

    ("C.12", "Russian legal form at end of company name",
     "Газпром ПАО",
     "company_name", "ru",
     "PJSC", "VOCABULARY",
     "ПАО = PJSC suffix extraction"),

    # ── Date format variants not in current suite ──────────────────────────────
    ("B.12", "Thai date day-first format",
     "08/05/2568",
     "date_of_birth", "th",
     "2025-05-08", "CALENDAR",
     "Day-first Thai Buddhist date — common on Thai IDs"),

    ("B.13", "Thai date with พ.ศ. label",
     "พ.ศ. 2568",
     "issue_date", "th",
     "2025", "CALENDAR",
     "Year-only Thai date with era label"),

    ("B.14", "Hijri date day-first Arabic-Indic",
     "١٤/٠٣/١٤٤٥",
     "date_of_birth", "ar",
     "2023-09-29", "CALENDAR",
     "Day-first Hijri date format common on Gulf documents"),

    ("B.15", "Hebrew date spelled out",
     "15 תשרי 5786",
     "date_of_birth", "he",
     "2025-10-17", "CALENDAR",
     "Hebrew date with month name spelled out"),

    # ── Identifiers not yet tested ─────────────────────────────────────────────
    ("A.4", "IBAN",
     "GB29 NWBK 6016 1331 9268 19",
     "iban", "en",
     "GB29 NWBK 6016 1331 9268 19", "PRESERVE",
     "IBAN must be preserved verbatim"),

    ("A.5", "Tax ID with country prefix",
     "DE811100090",
     "tax_id", "de",
     "DE811100090", "PRESERVE",
     "German VAT number preserved verbatim"),

    ("A.6", "LEI code",
     "529900T8BM49AURSDO55",
     "lei_code", "en",
     "529900T8BM49AURSDO55", "PRESERVE",
     "Legal Entity Identifier — 20 char alphanumeric"),

    # ── Financial values with currency symbols ─────────────────────────────────
    ("B.16", "Japanese yen amount",
     "¥1,234,567",
     "share_capital", "ja",
     "1234567", "NUMERIC",
     "JPY amount — currency extracted, number normalised"),

    ("B.17", "Euro European format",
     "€2.500.000,00",
     "share_capital", "de",
     "2500000.00", "NUMERIC",
     "EUR amount in European format"),

    ("B.18", "Saudi Riyal",
     "﷼500,000",
     "share_capital", "ar",
     "500000", "NUMERIC",
     "SAR amount"),

    # ── Geography variants ─────────────────────────────────────────────────────
    ("D.5", "Country name in Chinese",
     "中国",
     "nationality", "zh",
     "CHINA", "GEOGRAPHIC",
     "China in Chinese"),

    ("D.6", "Country name in Korean",
     "미국",
     "nationality", "ko",
     "UNITED STATES", "GEOGRAPHIC",
     "USA in Korean"),

    ("D.7", "Nationality adjective in Arabic",
     "سعودي",
     "nationality", "ar",
     "SAUDI ARABIA", "GEOGRAPHIC",
     "Saudi nationality adjective — resolves to country name, not adjectival form"),

    # ── Status terms not in current suite ──────────────────────────────────────
    ("C.13", "Russian status active",
     "действующая",
     "status", "ru",
     "ACTIVE", "VOCABULARY",
     "Russian feminine active status"),

    ("C.14", "French status dissolved",
     "dissoute",
     "status", "fr",
     "DISSOLVED", "VOCABULARY",
     "French feminine dissolved status"),

    ("C.15", "Chinese status active",
     "存续",
     "status", "zh",
     "ACTIVE", "VOCABULARY",
     "Chinese active/ongoing status — appears on SAMR extracts"),

    ("C.16", "Chinese status struck off",
     "吊销",
     "status", "zh",
     "STRUCK_OFF", "VOCABULARY",
     "Chinese administrative revocation — distinct from voluntary dissolution"),

    # ── Role titles not in current suite ──────────────────────────────────────
    ("C.17", "Arabic role general manager",
     "مدير عام",
     "role", "ar",
     "GENERAL MANAGER", "VOCABULARY",
     "Common Gulf company role"),

    ("C.18", "Russian role general director",
     "Генеральный директор",
     "role", "ru",
     "GENERAL DIRECTOR", "VOCABULARY",
     "Standard Russian company role on registry extracts"),

    ("C.19", "French role manager",
     "Gérant",
     "role", "fr",
     "MANAGER", "VOCABULARY",
     "French SARL manager role"),

    # ── Character map variants (expected to fail until Epic 07) ───────────────
    ("G.8", "French accented name",
     "Élodie Lefèvre",
     "person_name", "fr",
     "ELODIE LEFEVRE", "CHARACTER_MAP",
     "French accents stripped — expected to fail until Epic 07"),

    ("G.9", "Dutch van particle",
     "van den Berg",
     "person_name", "nl",
     "VAN DEN BERG", "CHARACTER_MAP",
     "Dutch noble particle preserved — expected to fail until Epic 07"),

    ("G.10", "Norwegian o-stroke",
     "Bjørnstad",
     "person_name", "no",
     "BJORNSTAD", "CHARACTER_MAP",
     "ø→O — expected to fail until Epic 07"),

    # ── Edge cases ─────────────────────────────────────────────────────────────
    ("E.1", "Short ambiguous string",
     "SA",
     "legal_form", "fr",
     "SA", "VOCABULARY",
     "SA is both a legal form and a country code — field type resolves the ambiguity"),

    ("E.2", "Mixed script company name",
     "Sony株式会社",
     "company_name", "ja",
     "KK", "VOCABULARY",
     "Latin + kanji mixed — legal form suffix must be extracted"),

    ("E.3", "Number that looks like a date",
     "20250508",
     "date_of_birth", "en",
     "2025-05-08", "CALENDAR",
     "ISO 8601 compact format without separators"),
]


# ── ANSI colours for terminal ──────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GREY   = "\033[90m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PASS_MARK = "✓"
FAIL_MARK = "✗"
WARN_MARK = "⚠"


def ok(text):   return f"{GREEN}{PASS_MARK} {text}{RESET}"
def fail(text): return f"{RED}{FAIL_MARK} {text}{RESET}"
def warn(text): return f"{YELLOW}{WARN_MARK} {text}{RESET}"
def info(text): return f"{CYAN}{text}{RESET}"
def grey(text): return f"{GREY}{text}{RESET}"


# ── Markdown helpers ───────────────────────────────────────────────────────────

def md_pass(text): return f"✅ {text}"
def md_fail(text): return f"❌ {text}"
def md_warn(text): return f"⚠️ {text}"


# ── Main runner ────────────────────────────────────────────────────────────────

def run():
    print(f"\n{BOLD}KYC Integration Diagnostic Runner{RESET}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Examples: {len(TEST_CASES)}\n")
    print("=" * 70)

    # Boot Flask app context
    try:
        from app import create_app
        flask_app = create_app("development")
        ctx = flask_app.app_context()
        ctx.push()
        print(ok("Flask app context created"))
    except Exception as e:
        print(fail(f"Failed to create Flask app context: {e}"))
        print(traceback.format_exc())
        sys.exit(1)

    # Import pipeline functions
    try:
        from app.pipeline.normalisation.field_type_detector import detect_field_type
        from app.pipeline.orchestrator import process_field_row
        print(ok("Pipeline modules imported"))
    except Exception as e:
        print(fail(f"Failed to import pipeline modules: {e}"))
        print(traceback.format_exc())
        sys.exit(1)

    print("=" * 70 + "\n")

    # Accumulate results for markdown report
    report_lines = []
    report_lines.append("# KYC Integration Diagnostic Report")
    report_lines.append(f"\n**Run date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Examples:** {len(TEST_CASES)}")
    report_lines.append(f"**Pipeline:** `detect_field_type()` → `process_field_row()` → `route_field()` → strategy")
    report_lines.append(f"**Mocks:** None — all calls are real\n")
    report_lines.append("---\n")

    summary = []  # (id, description, overall_pass)

    for (test_id, description, paste_text,
         exp_field_type, exp_language,
         exp_normalised, exp_method, notes) in TEST_CASES:

        exp_methods = [exp_method] if isinstance(exp_method, str) else exp_method

        print(f"{BOLD}{'─' * 70}{RESET}")
        print(f"{BOLD}{test_id} — {description}{RESET}")
        print(f"  Input:    {info(repr(paste_text))}")
        print(f"  Expected: field_type={exp_field_type}, language={exp_language}")
        print(f"  Expected: normalised={repr(exp_normalised)}, method={exp_method}")
        if notes:
            print(f"  Note:     {grey(notes)}")
        print()

        report_lines.append(f"## {test_id} — {description}\n")
        report_lines.append(f"| | |")
        report_lines.append(f"|---|---|")
        report_lines.append(f"| **Input** | `{paste_text}` |")
        report_lines.append(f"| **Expected field type** | `{exp_field_type}` |")
        report_lines.append(f"| **Expected language** | `{exp_language}` |")
        report_lines.append(f"| **Expected normalised form** | `{exp_normalised}` |")
        report_lines.append(f"| **Expected method** | `{exp_method}` |")
        if notes:
            report_lines.append(f"| **Notes** | {notes} |")
        report_lines.append("")

        step_results = []
        overall_pass = True

        # ── Step 1: GPT-4o-mini classification ────────────────────────────────
        report_lines.append("### Step 1 — GPT-4o-mini classification\n")
        print(f"  {BOLD}Step 1:{RESET} GPT-4o-mini classification")

        t0 = time.time()
        try:
            got_field_type, got_confidence, got_language = detect_field_type(paste_text)
            elapsed = time.time() - t0

            ft_ok  = got_field_type == exp_field_type
            lang_ok = got_language == exp_language

            ft_mark   = ok if ft_ok else warn
            lang_mark = ok if lang_ok else warn

            print(f"    field_type:  {ft_mark(got_field_type)} (expected: {exp_field_type})")
            print(f"    language:    {lang_mark(got_language)} (expected: {exp_language})")
            print(f"    confidence:  {got_confidence:.2f}")
            print(f"    time:        {elapsed:.2f}s")

            ft_icon   = md_pass if ft_ok else md_warn
            lang_icon = md_pass if lang_ok else md_warn

            report_lines.append(f"| | Expected | Got | Status |")
            report_lines.append(f"|---|---|---|---|")
            report_lines.append(f"| **field_type** | `{exp_field_type}` | `{got_field_type}` | {ft_icon('match') if ft_ok else md_warn('mismatch')} |")
            report_lines.append(f"| **language** | `{exp_language}` | `{got_language}` | {lang_icon('match') if lang_ok else md_warn('mismatch')} |")
            report_lines.append(f"| **confidence** | — | `{got_confidence:.2f}` | — |")
            report_lines.append(f"| **latency** | — | `{elapsed:.2f}s` | — |")
            report_lines.append("")

            if not ft_ok:
                report_lines.append(f"> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `{got_field_type}` but expected `{exp_field_type}`. The router will process the field as `{got_field_type}` which may select the wrong strategy.\n")

            if not lang_ok:
                report_lines.append(f"> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `{got_language}` but expected `{exp_language}`. This may affect strategy selection (e.g. character map handler chosen for wrong language).\n")

            # Use whatever GPT-4o-mini returned — this is what the real pipeline does
            actual_field_type = got_field_type
            actual_language   = got_language

        except Exception as e:
            elapsed = time.time() - t0
            print(f"    {fail(f'EXCEPTION: {e}')}")
            print(f"    Traceback: {traceback.format_exc()}")
            report_lines.append(md_fail(f"**EXCEPTION in detect_field_type:** `{e}`\n"))
            report_lines.append(f"```\n{traceback.format_exc()}\n```\n")
            overall_pass = False
            summary.append((test_id, description, False))
            report_lines.append("---\n")
            continue

        print()

        # ── Step 2: Orchestrator receives row ─────────────────────────────────
        report_lines.append("### Step 2 — Orchestrator + Router\n")
        print(f"  {BOLD}Step 2:{RESET} Orchestrator → Router")

        row = {
            "original_text": paste_text,
            "field_type":    actual_field_type,
            "language":      actual_language,
        }

        print(f"    Row passed to orchestrator:")
        print(f"      original_text: {repr(paste_text)}")
        print(f"      field_type:    {actual_field_type}")
        print(f"      language:      {actual_language}")

        report_lines.append("**Row passed to orchestrator:**\n")
        report_lines.append(f"```json")
        report_lines.append(f'{{"original_text": "{paste_text}", "field_type": "{actual_field_type}", "language": "{actual_language}"}}')
        report_lines.append(f"```\n")

        t1 = time.time()
        try:
            result = process_field_row(row)
            elapsed2 = time.time() - t1

            got_normalised = result.get("normalised_form")
            got_method     = result.get("processing_method", "")
            got_review     = result.get("review_required", False)
            got_confidence = result.get("confidence", 0.0)
            got_variants   = result.get("allowed_variants", [])

            print(f"    processing_method: {info(got_method)}")
            print(f"    normalised_form:   {info(repr(got_normalised))}")
            print(f"    confidence:        {got_confidence:.2f}")
            print(f"    review_required:   {got_review}")
            if got_variants:
                print(f"    allowed_variants:  {got_variants}")
            print(f"    time:              {elapsed2:.2f}s")

            report_lines.append("**Router result:**\n")
            report_lines.append(f"| Field | Value |")
            report_lines.append(f"|---|---|")
            report_lines.append(f"| processing_method | `{got_method}` |")
            report_lines.append(f"| normalised_form | `{got_normalised}` |")
            report_lines.append(f"| confidence | `{got_confidence:.2f}` |")
            report_lines.append(f"| review_required | `{got_review}` |")
            if got_variants:
                report_lines.append(f"| allowed_variants | {', '.join(f'`{v}`' for v in got_variants)} |")
            report_lines.append(f"| latency | `{elapsed2:.2f}s` |")
            report_lines.append("")

        except Exception as e:
            elapsed2 = time.time() - t1
            print(f"    {fail(f'EXCEPTION: {e}')}")
            print(f"    Traceback: {traceback.format_exc()}")
            report_lines.append(md_fail(f"**EXCEPTION in process_field_row:** `{e}`\n"))
            report_lines.append(f"```\n{traceback.format_exc()}\n```\n")
            overall_pass = False
            summary.append((test_id, description, False))
            report_lines.append("---\n")
            continue

        print()

        # ── Step 3: Compare expected vs actual ────────────────────────────────
        report_lines.append("### Step 3 — Expected vs Actual\n")
        print(f"  {BOLD}Step 3:{RESET} Comparison")

        # Method check
        method_pass = got_method in exp_methods
        # Normalised form check
        if exp_normalised is None:
            # Expected UNRESOLVED
            form_pass = got_normalised is None or got_method == "UNRESOLVED"
        else:
            form_pass = (got_normalised or "").strip().upper() == exp_normalised.strip().upper()

        method_mark = ok if method_pass else fail
        form_mark   = ok if form_pass   else fail

        print(f"    method:     {method_mark(got_method)} (expected: {'/'.join(exp_methods)})")
        print(f"    normalised: {form_mark(repr(got_normalised))} (expected: {repr(exp_normalised)})")

        example_pass = method_pass and form_pass
        overall_pass = overall_pass and example_pass

        method_icon = md_pass if method_pass else md_fail
        form_icon   = md_pass if form_pass   else md_fail

        report_lines.append(f"| | Expected | Got | Status |")
        report_lines.append(f"|---|---|---|---|")
        report_lines.append(f"| **method** | `{'` or `'.join(exp_methods)}` | `{got_method}` | {method_icon('PASS') if method_pass else md_fail('FAIL')} |")
        report_lines.append(f"| **normalised_form** | `{exp_normalised}` | `{got_normalised}` | {form_icon('PASS') if form_pass else md_fail('FAIL')} |")
        report_lines.append("")

        # Diagnosis when it fails
        if not method_pass:
            diagnosis = _diagnose_method_failure(
                got_method, exp_methods, actual_field_type, actual_language,
                got_field_type if 'got_field_type' in dir() else actual_field_type,
                exp_field_type
            )
            print(f"    {warn('Diagnosis: ' + diagnosis)}")
            report_lines.append(f"> ❌ **Method failure diagnosis:** {diagnosis}\n")

        if not form_pass and method_pass:
            diagnosis = _diagnose_form_failure(
                got_normalised, exp_normalised, got_method, paste_text
            )
            print(f"    {warn('Diagnosis: ' + diagnosis)}")
            report_lines.append(f"> ❌ **Form failure diagnosis:** {diagnosis}\n")

        # Overall result line
        result_line = f"### Overall: {'✅ PASS' if example_pass else '❌ FAIL'}\n"
        report_lines.append(result_line)
        print(f"\n  {'=' * 30}")
        print(f"  {ok('PASS') if example_pass else fail('FAIL')} — {test_id} {description}")
        print()

        summary.append((test_id, description, example_pass))
        report_lines.append("---\n")

    # ── Summary ────────────────────────────────────────────────────────────────
    passed = sum(1 for _, _, p in summary if p)
    failed = len(summary) - passed

    print(f"\n{'=' * 70}")
    print(f"{BOLD}SUMMARY{RESET}")
    print(f"{'=' * 70}")
    print(f"  Total:  {len(summary)}")
    print(f"  {ok(f'Passed: {passed}')}")
    if failed:
        print(f"  {fail(f'Failed: {failed}')}")
    print()

    for test_id, description, passed_flag in summary:
        mark = ok(f"PASS  {test_id}  {description}") if passed_flag else fail(f"FAIL  {test_id}  {description}")
        print(f"  {mark}")

    # Summary in markdown
    report_lines.insert(5, f"\n## Summary\n")
    report_lines.insert(6, f"| Result | Count |")
    report_lines.insert(7, f"|---|---|")
    report_lines.insert(8, f"| ✅ Pass | {passed} |")
    report_lines.insert(9, f"| ❌ Fail | {failed} |")
    report_lines.insert(10, f"| Total | {len(summary)} |")
    report_lines.insert(11, f"\n| ID | Description | Result |")
    report_lines.insert(12, f"|---|---|---|")
    for test_id, description, p in summary:
        report_lines.insert(13, f"| {test_id} | {description} | {'✅ PASS' if p else '❌ FAIL'} |")
    report_lines.insert(13 + len(summary), "\n---\n")

    # ── Write report ───────────────────────────────────────────────────────────
    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    report_path = reports_dir / f"integration-report-{timestamp}.md"
    latest_path = reports_dir / "integration-report-latest.md"

    report_text = "\n".join(report_lines)
    report_path.write_text(report_text, encoding="utf-8")
    latest_path.write_text(report_text, encoding="utf-8")

    print(f"\n{'=' * 70}")
    print(f"Report saved to:")
    print(f"  {report_path}")
    print(f"  {latest_path}  (always the latest run)")
    print(f"{'=' * 70}\n")

    ctx.pop()
    return 0 if failed == 0 else 1


# ── Diagnosis helpers ──────────────────────────────────────────────────────────

def _diagnose_method_failure(got_method, exp_methods, actual_field_type,
                              actual_language, got_field_type, exp_field_type):
    """Return a plain-English diagnosis of why the wrong method was selected."""

    if got_method == "UNRESOLVED" and "UNRESOLVED" not in exp_methods:
        if actual_field_type != exp_field_type:
            return (
                f"GPT-4o-mini classified as '{actual_field_type}' instead of "
                f"'{exp_field_type}'. The router received the wrong field type "
                f"and could not find a matching strategy."
            )
        return (
            f"The strategy for field_type='{actual_field_type}' language='{actual_language}' "
            f"returned None or raised NotImplementedError. Check that the strategy module "
            f"is fully implemented and wired into the router."
        )

    if got_method == "PRESERVE" and "PRESERVE" not in exp_methods:
        return (
            f"Field type '{actual_field_type}' is in the PRESERVE_FIELDS list but "
            f"should not be. Check PRESERVE_FIELDS in router.py or preserve.py."
        )

    if "VOCABULARY" in exp_methods and got_method != "VOCABULARY":
        return (
            f"Expected VOCABULARY lookup but got {got_method}. "
            f"Check that the lookup table for field_type='{actual_field_type}' "
            f"language='{actual_language}' exists in data/lookup_tables/ and that "
            f"VocabularyLookupService is correctly wired in _try_strategy_c()."
        )

    if "CALENDAR" in exp_methods and got_method != "CALENDAR":
        return (
            f"Expected CALENDAR conversion but got {got_method}. "
            f"Check that calendar_rules.py is wired in _try_strategy_b() and that "
            f"the calendar detection regex matches '{actual_language}' date format."
        )

    if "CHARACTER_MAP" in exp_methods and got_method != "CHARACTER_MAP":
        return (
            f"Expected CHARACTER_MAP but got {got_method}. "
            f"Check that character_map_normaliser.py is wired in _try_strategy_g() "
            f"and that language '{actual_language}' is in LANGUAGE_CHAR_MAPS."
        )

    if any(m in exp_methods for m in ["TRANSLITERATION", "TRANSLITERATE"]) and \
       got_method not in ["TRANSLITERATION", "TRANSLITERATE"]:
        return (
            f"Expected TRANSLITERATION but got {got_method}. "
            f"Check that transliteration.py is wired in _try_strategy_f() and "
            f"handles language '{actual_language}'."
        )

    return f"Got '{got_method}', expected one of {exp_methods}. Check router.py strategy wiring."


def _diagnose_form_failure(got_form, exp_form, got_method, original_text):
    """Return a plain-English diagnosis of why the normalised form is wrong."""

    if got_form is None:
        return "normalised_form is None — the strategy ran but returned an empty result."

    got_upper = (got_form or "").strip().upper()
    exp_upper = (exp_form or "").strip().upper()

    if got_upper == exp_upper.replace(" ", "") and " " in exp_upper:
        return (
            f"Got '{got_form}' — word boundary/space missing. "
            f"Expected '{exp_form}'. Check token splitting in the strategy."
        )

    if got_method == "CHARACTER_MAP" and got_upper != exp_upper:
        return (
            f"Character map produced '{got_form}' instead of '{exp_form}'. "
            f"Check that the correct map (expansion vs drop) is applied as primary "
            f"and that all characters in '{original_text}' are in the map."
        )

    if got_method == "CALENDAR" and got_form != exp_form:
        return (
            f"Calendar conversion produced '{got_form}' instead of '{exp_form}'. "
            f"Check the epoch calculation in the relevant calendar module."
        )

    if got_method == "VOCABULARY":
        return (
            f"Vocabulary lookup returned '{got_form}' instead of '{exp_form}'. "
            f"Check the JSON lookup table entry for '{original_text}'."
        )

    return f"Got '{got_form}', expected '{exp_form}'. Inspect the strategy module output."


if __name__ == "__main__":
    sys.exit(run())

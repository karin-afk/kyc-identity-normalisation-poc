# Epic 05 — Strategy E: Verified Repository

## What you need to provide

Two JSON seed files. These pre-populate the repository before the tool processes any real documents, so common names resolve immediately without going to native speaker review.

## Ammendments to the below:
Amendment to Epic 05 — Strategy E: Verified Repository
In the store_token() function signature and docstring, add country_code as an optional parameter:
pythondef store_token(
    self,
    token: str,
    language: str,
    field_type: str,
    romanised_form: str,
    allowed_variants: list[str],
    verified_by_user_id: int,
    country_code: str = "",
) -> None:
    """
    Write a single token entry to the token_entries table.

    Uses upsert semantics on (token, language_code, field_type, country_code).
    The country_code is required for issuing_authority field types because
    the same authority name in the same language means different things across
    countries (e.g. 'وزارة الداخلية' in ar/AE vs ar/SA vs ar/EG).
    For all other field types, country_code defaults to empty string.

    Called automatically by store_verified() for applicable field types.
    Can also be called directly by the seed loader.
    """
Add a note in the seed loading section:
The flask seed-repository command also loads app/data/seed/issuing_authorities_seed.json. When loading this file, skip any object containing a _comment key. The unique key for issuing authority entries is (token, language_code, country_code, field_type) — not just (token, language_code, field_type) as for other field types.
Add a note on repository growth:
issuing_authority is a repository-managed field type, not a lookup table field type. It is not in lookup_tables/. New issuing authority names encountered in real documents and confirmed by a native speaker are written to the verified repository automatically by store_verified(). The seed file in app/data/seed/issuing_authorities_seed.json is the starting point only — it should not be manually maintained as documents are processed. The repository is the live source of truth.
In the token_entries table definition (Epic 06 database schema), add country_code column:
pythonclass TokenEntry(db.Model):
    __tablename__ = "token_entries"
    id: int
    token: str          (not null)
    language_code: str  (not null)
    country_code: str   (default "")
    field_type: str
    romanised_form: str
    allowed_variants: JSON
    verified_by: int    (FK → users.id)
    verified_at: datetime
    # Unique constraint: (token, language_code, country_code, field_type)

That is the complete amendment. The only database change is adding country_code to token_entries with an empty string default, so existing entries for names and company names are unaffected.

---

Block 4b — Strategy D: Geographic lookup#Paste thisExpected normalised formMethodPass?D.1ألمانياGERMANYGEOGRAPHICD.2日本JAPANGEOGRAPHICD.3대한민국SOUTH KOREAGEOGRAPHICD.4ГерманияGERMANYGEOGRAPHICD.5ΓερμανίαGERMANYGEOGRAPHICD.6إماراتيEMIRATIGEOGRAPHICD.7日本人JAPANESEGEOGRAPHICD.8القاهرةCAIROGEOGRAPHIC

What to check: Country names in any script resolve to their English form. Nationality demonyms resolve correctly.
If D.x fail: GeographicLookupService may not have built its index — check that pycountry and babel are installed and that the service initialises without error on startup.

---
Block 4c — Strategy F: Transliteration
#Paste thisExpected normalised formVariants includeMethodPass?F.1НатальяNATALYANATALJA, NATALIYATRANSLITERATIONF.2АлександрALEKSANDRALEXANDER, ALEKSANDERTRANSLITERATIONF.3ΙωάννηςIOANNISYANNIS, GIANNISTRANSLITERATIONF.4ΝίκοςNIKOSNIKOTRANSLITERATIONF.5TANAKA—paste as 田中TRANSLITERATIONF.6王小明WANG XIAOMINGWANG XIAO MINGTRANSLITERATIONF.7이민준I MINJUNLEE MINJUN, YI MINJUNTRANSLITERATION
Note for F.5: Paste 田中 (the kanji), not the romanisation. Expected result is TANAKA.
Note on Arabic: محمد will NOT return TRANSLITERATION — it routes to UNRESOLVED because Arabic short vowels cannot be recovered deterministically. This is correct Phase 1 behaviour.
If F.1 returns NATALJA instead of NATALYA: The BGN/PCGN post-processing corrections are not applied. Check _BGN_PCGN_CORRECTIONS in the transliteration module.
If F.3–F.4 fail: Greek handler may not be wired or the transliterate library has a Greek mode issue. Run: pytest tests/test_transliteration.py -v -k greek

---

### `person_name_tokens.json`

A JSON array of common person name tokens across six languages, with their confirmed romanisations and variant list. Apply BGN/PCGN romanisation standards throughout. Each entry is a single token — a given name or a surname — not a full name.

**Format:**
```json
[
  {
    "token": "محمد",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "MUHAMMAD",
    "allowed_variants": ["MOHAMMED", "MOHAMED", "MOHAMMAD", "MUHAMMED"]
  },
  {
    "token": "田中",
    "language_code": "ja",
    "field_type": "person_name",
    "romanised_form": "TANAKA",
    "allowed_variants": []
  }
]
```

**Fields:**
- `token` — the name token in original script, exactly as it appears in documents
- `language_code` — ISO 639-1 code
- `field_type` — always `"person_name"` for this file
- `romanised_form` — uppercase, BGN/PCGN or ICAO-standard
- `allowed_variants` — list of other romanisations that appear on sanctions databases (can be `[]`)

**Languages to cover:** Arabic (`ar`), Japanese (`ja`), Russian (`ru`), Chinese (`zh`), Korean (`ko`), Greek (`el`).

**Save to:** `app/data/seed/person_name_tokens.json`

---

### `company_names.json`

Same format as person name tokens, but for company names. Contains your most frequent counterparty names in original script with confirmed English forms.

- `field_type` is `"company_name"` for all entries
- `romanised_form` is the confirmed uppercase English name used in screening databases
- `allowed_variants` includes common short forms and alternative renderings

**Save to:** `app/data/seed/company_names.json`

Can be an empty array `[]` to start. The tool works without it — company names not in the repository go to native speaker review on first encounter.

---

## What exists in the current codebase

Nothing. Strategy E does not exist in any form. Entirely new build. The database tables (`verified_translations`, `token_entries`) are defined in Epic 06 (database schema). This epic builds the service that reads from and writes to those tables, and the seed loading mechanism.

**Dependency:** This epic requires Epic 06 (database schema) to be complete before it can run. The service class itself can be written in parallel, but the seed loading and all tests require the database tables to exist.

---

## What this epic builds

### `app/pipeline/normalisation/repository_lookup.py` — NEW FILE

```python
"""
Strategy E — Verified Repository.

Queries the PostgreSQL database for human-confirmed translation pairs.
Every result returned by this strategy has been confirmed by a native speaker
or a human analyst — confidence is always 1.0.

Two matching modes:
  1. Whole-value match — the complete original text matches a stored entry exactly.
  2. Token-level match — the text is split into tokens; each token is looked up
     individually. If all tokens resolve, the results are recombined.

Token-level matching enables partial reuse:
  - "田中 太郎" confirmed → tokens "田中" and "太郎" stored separately
  - Later document contains "田中 花子"
  - "田中" resolves from token store, "花子" does not
  - "田中" portion resolves; "花子" falls through to transliteration

The repository is checked before transliteration libraries (Strategy F) and
character maps (Strategy G). A repository hit short-circuits those strategies
entirely for that field.
"""

from app.pipeline.normalisation.field_types import ProcessingMethod, STRATEGY_CONFIDENCE


class RepositoryLookupService:

    def lookup(self, text: str, language: str, field_type: str) -> dict | None:
        """
        Main entry point called by the normalisation router.

        Tries whole-value match first, then token-level match.
        Returns None if no match found (router falls through to Strategy F).

        Args:
            text: Original text exactly as extracted from the document.
            language: ISO 639-1 language code.
            field_type: KYC field type string.

        Returns:
            Result dict with processing_method=REPOSITORY and confidence=1.0,
            or None if no match.
        """
        result = self._lookup_whole(text, language, field_type)
        if result:
            return result

        result = self._lookup_tokens(text, language, field_type)
        return result

    def _lookup_whole(self, text: str, language: str, field_type: str) -> dict | None:
        """
        Query the verified_translations table for an exact match on
        (original_text, language_code, field_type).

        Matching is case-sensitive for non-Latin scripts.
        Matching is case-insensitive for Latin-script languages
        (language in: en, de, fr, es, it, pt, nl, pl, sv, no, da, tr).

        Returns result dict or None.
        """

    def _lookup_tokens(self, text: str, language: str, field_type: str) -> dict | None:
        """
        Split text into tokens, look up each in token_entries table.

        Only applies to field types where token-level matching makes sense:
        person_name, company_name, director_name, officer_name,
        shareholder_name, parent_name_father, parent_name_mother, entity_name.

        Tokenisation strategy by language:
        - Japanese, Chinese: each character is a token (character boundary)
        - All other scripts: whitespace split

        If ALL tokens resolve → recombine romanised forms with spaces
        and merge allowed_variants lists.
        If ANY token fails to resolve → return None (fall through to Strategy F)

        Returns result dict or None.
        """

    def store_verified(
        self,
        original_text: str,
        language: str,
        field_type: str,
        normalised_form: str,
        allowed_variants: list[str],
        processing_method: str,
        verified_by_user_id: int,
        source_document_id: int | None = None,
    ) -> None:
        """
        Write a confirmed translation to the verified_translations table.

        Uses upsert semantics — if an entry already exists for
        (original_text, language_code, field_type), update it rather than
        inserting a duplicate.

        After writing the whole-value entry, also extracts and stores
        individual tokens to the token_entries table for applicable field types.

        Triggers a JSON backup after every write (see _backup()).

        Writes an AuditLog entry: action=REPOSITORY_ENTRY_WRITTEN.

        Args:
            processing_method: The strategy that originally produced this
                               translation before human confirmation.
                               Stored for traceability.
        """

    def store_token(
        self,
        token: str,
        language: str,
        field_type: str,
        romanised_form: str,
        allowed_variants: list[str],
        verified_by_user_id: int,
    ) -> None:
        """
        Write a single token entry to the token_entries table.

        Uses upsert semantics on (token, language_code, field_type).
        Called automatically by store_verified() for applicable field types.
        Can also be called directly by admin seed loading.
        """

    def _tokenise(self, text: str, language: str, field_type: str) -> list[str]:
        """
        Split text into tokens for token-level matching and storage.

        Japanese/Chinese: split on character boundaries — each Han character,
        each kana character is a separate token. Spaces and punctuation
        are stripped and not stored as tokens.

        All other scripts: split on whitespace. Strip punctuation from
        token boundaries.

        Only called for name and company field types. For all other field
        types, returns [text] (treat as single unsplittable token).
        """

    def _backup(self) -> None:
        """
        Export verified_translations and token_entries tables to JSON files.

        Output:
            backups/verified_translations_latest.json
            backups/token_entries_latest.json
            backups/verified_translations_{timestamp}.json  (timestamped copy)
            backups/token_entries_{timestamp}.json

        Rotate: keep only the most recent BACKUP_RETENTION_COUNT timestamped
        copies (from .env, default 30). Delete older ones.

        Write atomically: write to a temp file then rename, so a partial write
        never corrupts the latest backup.

        Called synchronously within store_verified() — must complete before
        store_verified() returns.
        """

    @staticmethod
    def _build_result(entry: dict) -> dict:
        """Build a standard result dict from a database row."""
        return {
            "normalised_form":          entry["normalised_form"],
            "allowed_variants":         entry.get("allowed_variants", []),
            "processing_method":        ProcessingMethod.REPOSITORY,
            "confidence":               STRATEGY_CONFIDENCE[ProcessingMethod.REPOSITORY],
            "review_required":          False,
            "review_reason":            None,
            "should_use_in_screening":  True,
        }
```

### `app/cli/seed_repository.py` — NEW FILE

A Flask CLI command that loads the seed JSON files into the database on first deployment.

```python
"""
Flask CLI command: flask seed-repository

Loads person_name_tokens.json and company_names.json into the
verified_translations and token_entries tables.

Idempotent — running twice does not create duplicates (upsert semantics).
Requires the database tables to exist (run flask db upgrade first).

Usage:
    flask seed-repository
    flask seed-repository --dry-run   # validate files without writing
"""
```

The command must:
1. Validate JSON structure and required fields before writing anything.
2. Report how many entries were inserted vs updated.
3. Trigger a backup after loading.
4. Write an `AuditLog` entry with `action=REPOSITORY_SEEDED`.

### `BACKUP_FOLDER` environment variable

Already in `.env.example`. Default is `backups/`. Create the directory if it does not exist. Do not raise if the directory already exists.

---

## Tests

`tests/test_strategy_e_repository.py`

```python
# --- Whole-value lookup ---
def test_whole_value_match_returns_result(db_session): ...
def test_whole_value_match_is_exact(db_session): ...       # "Muhammad" does not match "muhammad" for Arabic
def test_whole_value_latin_case_insensitive(db_session): ... # "mueller" matches "MUELLER" for German
def test_whole_value_no_match_returns_none(db_session): ...

# --- Token-level lookup ---
def test_token_match_all_tokens_resolve(db_session): ...    # "田中 太郎" → both tokens in store
def test_token_match_partial_returns_none(db_session): ...  # "田中 花子" → 花子 not in store → None
def test_token_match_japanese_character_split(db_session): ... # "田中" split to ["田", "中"] — no, it's a single surname token
def test_token_match_arabic_space_split(db_session): ...    # "محمد عبد الله" splits on spaces

# --- store_verified ---
def test_store_verified_creates_entry(db_session): ...
def test_store_verified_upserts_not_duplicates(db_session): ...
def test_store_verified_also_stores_tokens(db_session): ...
def test_store_verified_creates_backup(db_session, tmp_path): ...
def test_store_verified_writes_audit_log(db_session): ...

# --- store_token ---
def test_store_token_creates_entry(db_session): ...
def test_store_token_upserts(db_session): ...

# --- Seed loading ---
def test_seed_command_loads_person_names(runner): ...
def test_seed_command_is_idempotent(runner): ...
def test_seed_command_dry_run_does_not_write(runner): ...
def test_seed_command_validates_json_structure(runner): ...

# --- Backup ---
def test_backup_creates_latest_file(db_session, tmp_path): ...
def test_backup_creates_timestamped_copy(db_session, tmp_path): ...
def test_backup_rotates_old_files(db_session, tmp_path): ...
def test_backup_is_atomic(db_session, tmp_path): ...       # temp file then rename

# --- Router integration ---
def test_lookup_returns_none_for_empty_repository(db_session): ...
def test_lookup_result_has_confidence_1(db_session): ...
def test_lookup_result_review_not_required(db_session): ...
```

---

## Acceptance criteria

- `service.lookup("محمد", "ar", "person_name")` returns `normalised_form == "MUHAMMAD"` after seed data is loaded.
- `service.lookup("田中 太郎", "ja", "person_name")` returns a result if both `田中` and `太郎` are in the token store.
- `service.lookup("田中 花子", "ja", "person_name")` returns `None` if `花子` is not in the token store.
- `store_verified()` uses upsert semantics — calling it twice for the same `(original_text, language, field_type)` results in one row, not two.
- `store_verified()` writes a backup file after every call.
- `flask seed-repository` is idempotent — running it twice produces no errors and no duplicate rows.
- `flask seed-repository --dry-run` validates files and reports without writing.
- All backup writes are atomic (write to temp then rename).
- All tests pass.
- No LLM is called at any point.

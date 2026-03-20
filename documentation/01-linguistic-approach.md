# Linguistic Approach to KYC Identity Field Normalisation

This document describes the linguistic strategies applied to each script and language handled by the KYC Identity Normalisation pipeline. It covers the writing systems involved, the transliteration or translation standards chosen, the known ambiguities in each language, and the specific optimisations made to produce output suitable for KYC screening.

---

## 1. Overview — Why Normalisation Is Linguistically Complex

KYC identity screening compares names, addresses, and company names against sanctions lists, watchlists, and adverse media databases that are predominantly maintained in Latin script. Source documents arrive in a wide variety of scripts and orthographic conventions. The core linguistic challenge is **many-to-one ambiguity**: a single foreign name can be romanised in multiple equally valid ways, and screening systems must be capable of matching any of them.

For example, the Arabic name محمد maps to Muhammad, Mohammed, Mohamed, Mohammad, and Muhammed, all of which appear on sanctioned-entity lists. A system that produces only one form and discards the others will generate false negatives — the most dangerous failure mode in a compliance context.

The pipeline therefore produces not only a **primary normalised form** but also an **`allowed_variants` list**, enabling downstream screening tools to test all plausible romanisations simultaneously.

---

## 2. Arabic (ar) — Script: Arabic

### Writing system
Arabic is written right-to-left using a cursive abjad: only consonants and long vowels are represented; short vowels (fatḥa /a/, kasra /i/, ḍamma /u/) are normally omitted from everyday text, including passports and official documents. This vowel absence is the primary source of transliteration ambiguity.

### Standard applied
**BGN/PCGN romanisation** (United States Board on Geographic Names / Permanent Committee on Geographical Names) is the standard used for Arabic person names. This standard is widely used in passport control, sanctions lists, and international law-enforcement databases.

### Transliteration strategy
Because short vowels are absent from the input text, purely rule-based transliteration produces consonant strings that are unreadable and useless for screening (e.g. محمد → "mhmd"). For this reason, Arabic person names and aliases are routed to the **LLM layer** (GPT-4o), which uses world-knowledge to supply the correct vowels.

The LLM prompt instructs the model to:
- Produce the **BGN/PCGN canonical form** as the `primary` output.
- Return a `variants` array covering all widely-used romanisation families (e.g. Mohammed/Mohamed family, Al-/El- prefix variations, Hasan/Hassan).
- Transliterate **only** — never translate the meaning of a name.
- Output structured JSON to guarantee parseable variants.

### Key linguistic decisions
| Feature | Decision | Reason |
|---|---|---|
| Al- / El- prefix | Always written as `AL-` (uppercase, hyphenated) | BGN/PCGN standard; sanctions lists consistently use this form |
| Definite article elision | Al-Hussein not Alhussein | BGN/PCGN requires hyphen after `al-` |
| Short vowel supply | LLM infers from name lexicon | Cannot be derived from consonant-only text |
| ع (ʿayn) | Omitted in output | ICAO Doc 9303 and most Latin-script watchlists omit the ayin glottal marker |
| Variant generation | Required | Same individual may appear as Muhammad, Mohammed, Mohamed, Mohammad, Muhammed |
| Compound names | ابن / أبو / بنت preserved | Patronymic particles are semantically meaningful |

### Known ambiguities
- **Name order**: Arabic names traditionally follow a given-name-first order, but Western databases sometimes invert this. The `allowed_variants` list covers both orderings.
- **Romanisation families**: At least two major romanisation systems are in common use (BGN/PCGN and the older British transliteration). Generated variants cover both.
- **Tashkeel (diacritics)**: When present, diacritical marks resolve short-vowel ambiguity. The pipeline passes these through to the LLM unmodified, which improves accuracy when they are present.

---

## 3. Russian (ru) — Script: Cyrillic

### Writing system
Russian uses a 33-letter Cyrillic alphabet derived from the Byzantine Greek alphabet. The script is largely phonemic: the relationship between letter and sound is more regular than in English, making rule-based transliteration reliable for most names.

### Standard applied
The `transliterate` Python library applies a **BGN/PCGN-influenced** mapping, which is the standard used by Western passport authorities for Russian names. The library targets the reversed mode of the GOST 7.79-2000 system, which is close to BGN/PCGN.

### Transliteration strategy
Russian is handled entirely by the deterministic **`transliterate` library** — no LLM is required for Russian person names. Addresses are routed to the LLM for street-name translation.

### Key linguistic decisions
| Feature | Decision | Reason |
|---|---|---|
| Soft sign (ь) | Stripped entirely | The BGN/PCGN standard omits the soft sign in romanised output; generating an apostrophe (the library default) produces screening noise |
| Hard sign (ъ) | Stripped (library default) | No standard ICAO romanisation for ъ in name contexts |
| Ukrainian characters (Є, І, Ї) | Pre-processed before library call | The `transliterate` library mangles these even in Ukrainian mode; manual substitution is applied first |
| Е / Э distinction | Mapped by library | Е → Ye (word-initial) / E (after consonant); Э → E |
| Ж → Zh | Applied by library | Standard BGN/PCGN convention |
| Я → Ya, Ю → Yu | Applied by library | Standard; the library uses Ja/Ju — a known difference from pure BGN |

### Known ambiguities
- **Ja/Ja vs Ya/Yu**: The `transliterate` library outputs `Ja` where BGN/PCGN mandates `Ya` (e.g. Наталья → `NATALJA` vs `NATALYA`). This is a known open issue — current score on cases KYC051 and KYC057 reflects this.
- **Patronymics**: Russian middle names (patronymics, e.g. Сергеевна) are included in the transliteration. The pipeline preserves them as part of the full-name string, consistent with how they appear in Russian passports.
- **Ukrainian vs Russian ambiguity**: Many documents from the former Soviet Union use Russian on the document type field but contain Ukrainian characters. The pipeline detects Ukrainian-exclusive characters (Є, І, Ї, Ї) and automatically switches to Ukrainian transliteration mode, flagging the result for analyst review.

---

## 4. Ukrainian (uk) — Script: Cyrillic

### Writing system
Ukrainian uses a 33-letter Cyrillic alphabet that differs from Russian in several key characters. The characters Є (Ye), І (I), Ї (Yi) and Ґ (G) are exclusive to Ukrainian and are absent from Russian text.

### Standard applied
The **Ukrainian Latin transliteration standard** adopted by the Cabinet of Ministers of Ukraine (Resolution No. 55, 2010) is the closest public standard; the pipeline's approach is consistent with it via the `transliterate` library in Ukrainian mode.

### Transliteration strategy
Ukrainian shares the Cyrillic pre-processing pipeline with Russian but requires different character mappings for the Ukrainian-exclusive letters. These are applied **before** the library call because the `transliterate` library does not handle them reliably:

| Ukrainian char | Substitution | Notes |
|---|---|---|
| Є / є | Ye / ye | U+0404 — Cyrillic Ye |
| І / і | I / i | U+0406 — Ukrainian I (distinct from Cyrillic И) |
| Ї / ї | I / i | U+0407 — Yi; romanised as plain I in name contexts for KYC practice |

### Known ambiguities
- **Ї romanisation**: Linguistically, ї = /ji/. In standard Ukrainian passport practice it romanises as `I` (not `Yi`), particularly in patronymic suffixes. The pipeline follows passport convention.
- **Ukrainian vs Russian**: All Ukrainian results are flagged `review_required=True` because the Ukrainian/Russian distinction itself requires analyst judgement when the document language field is ambiguous.

---

## 5. Bulgarian (bg) — Script: Cyrillic

Bulgarian uses Cyrillic and is handled via the same `transliterate` library pipeline as Russian. The library's Bulgarian mode applies the appropriate phonetic differences (e.g. Bulgarian Ъ is pronounced as a full vowel /ɐ/ and maps differently than in Russian).

---

## 6. Japanese (ja) — Script: Kanji, Hiragana, Katakana

### Writing system
Japanese uses three interlocking scripts:
- **Hiragana** — syllabic, 46 characters, used for grammatical particles and native words
- **Katakana** — syllabic, 46 characters, used for foreign loanwords and some names
- **Kanji** — logographic characters borrowed from Chinese, used for names and content words

Names in passports may appear in any combination of these scripts.

### Standard applied
**Hepburn romanisation** — the system used in Japanese passports (ICAO Doc 9303 compliant) and the most widely recognised standard internationally. Implemented via the `pykakasi` library.

### Transliteration strategy

#### Hiragana and Katakana
These syllabic scripts have a near-perfect one-to-one mapping to Latin syllables. Romanisation is deterministic and reliable. `pykakasi` handles these correctly.

#### Kanji — the core challenge
Kanji characters are logographic: a single character encodes meaning, and its pronunciation (reading) must be inferred from context. The same character can have multiple valid readings (on-yomi / kun-yomi). For example, 健 can be read as **Ken**, **Takeshi**, or **Masaru**, all of which are genuine Japanese given names.

The pipeline addresses this with a **kanji ambiguity lookup table** (`src/config/kanji_lookup.py`). For every kanji token that appears in the lookup:
1. The **first listed reading** is used as the primary romanised form.
2. **All listed readings** are added to `allowed_variants` to ensure screening systems can match any valid reading.

The lookup table covers:
- Very common given-name kanji (健, 翔, 大, 一, 太, 郎, ...)
- Common male and female name components (雄, 弘, 博, 明, 直, 誠, 修, 子, 美, 香, 奈, 恵, ...)
- Common multi-kanji given name combinations (太郎, 一郎, 次郎, 三郎, 健一, ...)
- Common surnames (山田, 田中, 佐藤, 伊藤, 鈴木, 渡辺, ...)

All kanji-containing results are flagged `review_required=True` with the reason "Kanji reading ambiguity: furigana or MRZ required for certainty".

### Key linguistic decisions
| Feature | Decision | Reason |
|---|---|---|
| Name order | Surname-first (Japanese convention) in primary output | Passport order; variant list includes given-name-first for Western database compatibility |
| Long vowels (ō, ū) | Rendered without macron (o, u) | ICAO Doc 9303 standard omits macrons; screeners use ASCII |
| っ (double consonant) | Doubled by library (e.g. Katta) | Hepburn standard |
| ん before vowel | Rendered as n' in some systems → stripped apostrophe | Screeners do not consistently handle the apostrophe |

### Known ambiguities
- **Kanji surname readings**: Even common surnames like 佐藤 (Sato) look straightforward but field instructions could plausibly require SATOU or SA TO depending on the database. Variants cover the main cases.
- **Name order inversion**: Japanese passports place family name before given name. Western sanctions lists sometimes invert this. Both orderings are provided.

---

## 7. Chinese / Mandarin (zh) — Script: Han (Traditional and Simplified)

### Writing system
Chinese uses Han characters (hanzi), which are logographic — each character represents a morpheme with a meaning and a sound. Chinese names are typically two or three characters: one for the family name (surname) and one or two for the given name.

### Standard applied
**Pinyin** (Hànyǔ Pīnyīn) — the official romanisation system of the People's Republic of China and the standard used in Chinese passports and international documents. Implemented via the `pypinyin` library.

### Transliteration strategy

The `pypinyin` library converts each character to its Pinyin syllable without tone marks (tones are not used in name romanisation for ICAO purposes). The pipeline applies an important name-specific optimisation:

**Given-name fusion**: Standard Pinyin would render 王小明 as `Wang Xiao Ming` (three separate tokens). In Chinese passport practice, the given name is written as a single fused string: `Wang Xiaoming`. The pipeline detects single-surname / multi-character given name structures and fuses the given name syllables accordingly.

This is linguistically significant because screening systems that break on spaces would fail to match `WANG XIAO MING` against a list entry of `WANG XIAOMING`.

### Key linguistic decisions
| Feature | Decision | Reason |
|---|---|---|
| Tone marks | Omitted | ICAO Doc 9303 standard; not used in passports |
| Given name fusion | Applied for person_name field type | Matches passport rendering convention |
| ü → u | Applied by pypinyin | V-sound characters romanised without umlaut in ICAO standard |
| Surname first | Primary output | Chinese convention; given-name-first listed as variant |
| Company brand names | LLM resolves to established English rendering | 三菱→MITSUBISHI, 腾讯→TENCENT: known brands have canonical English names |

### Known ambiguities
- **Homophone characters**: Different characters with the same Pinyin exist. For screening purposes the Pinyin form is the canonical output — character-level disambiguation is not needed.
- **Company names with descriptive words**: Chinese company names contain generic words (科技 = technology, 有限公司 = limited company). The LLM prompt instructs the model to translate generic words to English while preserving established brand names in their English form.
- **Hong Kong / Cantonese names**: Cantonese romanisation (Jyutping) differs substantially from Mandarin Pinyin. The pipeline's current `zh` handler uses Mandarin Pinyin. Documents from Hong Kong may require separate handling.

---

## 8. Greek (el) — Script: Greek

### Writing system
Modern Greek uses a 24-letter Greek alphabet. The script is largely phonemic and has a relatively regular mapping to Latin characters.

### Standard applied
**ISO 843** — the international standard for Greek-to-Latin transliteration. Implemented via the `transliterate` library in Greek mode.

### Transliteration strategy
Greek is handled entirely by the deterministic `transliterate` library. One post-processing correction is applied:

- The library renders **ου** (the Greek /u/ sound, as in `Νούλης`) as `oy`. The pipeline replaces this with `ou`, which is the ISO 843 and common-usage rendering.

### Key linguistic decisions
| Feature | Decision | Reason |
|---|---|---|
| ου → ou (not oy) | Post-process replace | ISO 843 and ICAO convention |
| θ → th | Library default | ISO 843 |
| φ → ph | Library default | ISO 843 |
| χ → ch | Library default | ISO 843 |
| αυ / ευ | Library handles | Rendered as av/ev or af/ef depending on phonetic context |

### Known ambiguities
- **Tonos (accent mark)**: Greek monotonic orthography uses a single accent mark (´). The library strips these for Latin output. No ambiguity for screening purposes.
- **Company names with Greek descriptive words**: Greek company names often contain Ανώνυμη Εταιρεία (SA equivalent) or generic descriptive roots. The LLM prompt instructs the model to translate these to English — known remaining failures involve cases where the established brand name differs from the literal translation.

---

## 9. Preserve Fields — No Normalisation Required

Certain field types carry structured identifiers that must not be modified. These are handled by the rules engine and returned verbatim:

| Field type | Examples | Treatment |
|---|---|---|
| `passport_no` | X1234567, P123456789 | Preserved exactly as-is |
| `id_no` | National ID numbers | Preserved exactly as-is |
| `email` | user@domain.com | Preserved exactly as-is |

---

## 10. Addressing and Name Order — Cross-Language Notes

### Name order conventions

| Language | Convention | Pipeline behaviour |
|---|---|---|
| Arabic | Given name first (Western form) | Primary: given-first; variants include alternate orderings |
| Japanese | Surname first (Japanese convention) | Primary: surname-first; variants include given-name-first |
| Chinese | Surname first | Primary: surname-first; variants include given-name-first |
| Russian/Ukrainian | Given name first in Western usage | Library produces given-name-first |
| Greek | Given name first (Western) | Library produces given-name-first |

### Address field treatment
Addresses are **not transliterated** — they are translated and normalised to English by the LLM. This is necessary because:
1. Addresses contain meaningful words (street names, district names) that have standard English equivalents.
2. Addresses contain numbers and administrative unit names that require semantic knowledge to render correctly.
3. Transliterating an address phonetically (e.g. шарع الشيخ زايد → "Sharik ash-Shaykh Zayd") produces a form that analysts cannot recognise or verify.

The address LLM prompt explicitly prohibits the model from inventing or omitting any component.

---

## 11. Script Auto-Detection

When the `language` field is absent from an input row, the pipeline falls back to unidecode-based Latin conversion as a last resort. For optimal results, the language code should always be supplied. If a document carries only a script type (e.g. "Cyrillic") without a specific language, the pipeline's Ukrainian-character detection heuristic can distinguish Russian from Ukrainian.

---

*Last updated: March 2026. Pipeline version: v2 (Streamlit frontend + LLM Arabic + Kanji lookup).*

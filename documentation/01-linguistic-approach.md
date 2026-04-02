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

### Egyptian and country-specific conventions
Egyptian Arabic names are frequently romanised using compound, hyphen-free forms that differ from the classical BGN/PCGN rendering. For example, the surname السيد (Al-Sayyid in classical BGN/PCGN) is rendered as **Elsayed** in Egyptian passport practice; النجار becomes **Alnaggar** rather than Al-Najjar. The UAE uses similarly fused forms (Al Maktoum rather than Al-Maktum). The pipeline passes the document `country` field into the Arabic name LLM system prompt, enabling the model to apply the country-specific romanisation convention rather than always defaulting to the classical standard. This is particularly important for documents from Egypt (EG), the UAE (AE), and Saudi Arabia (SA).

### Ayin (ع) variant generation
The Arabic letter ع (ʿayn) poses a specific romanisation challenge. ICAO Doc 9303 and most modern Latin-script watchlists omit the ayin marker entirely in romanised output. However, older records and some specialist databases represent it as an ASCII apostrophe (`'`) or the Unicode letter modifier ʿ (U+02BF). The pipeline's primary output follows ICAO convention — ayin is omitted. Where a name contains ع, the `allowed_variants` list is extended with forms that include an apostrophe in the ayin position, ensuring that a match is not missed against a database built to an older convention (e.g. ABD AL AZIZ and ABD AL-`A'ZIZ being recognised as the same name).

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

### Era-year (gengo) conversion
Japanese official documents — including date of birth fields on residence cards and company registration documents — frequently express years in the traditional **era-year (元号, gengo)** system rather than the Gregorian calendar. For example, 令和5年7月3日 means year 5 of the Reiwa era, which is **2023-07-03**.

The pipeline (`src/utils/calendar_utils.py`) detects and converts all five modern eras:

| Era (Kanji) | Era (Romaji) | Gregorian start | Notes |
|---|---|---|---|
| 明治 | Meiji | 1868 | Documents from this era are rare in modern KYC |
| 大正 | Taisho | 1912 | |
| 昭和 | Showa | 1926 | Most common era year on older documents |
| 平成 | Heisei | 1989 | Common on mid-career documents |
| 令和 | Reiwa | 2019 | Current era |

The converter accepts both kanji era names (令和5年) and partially romanised forms (Reiwa 5年), and handles kanji numerals (令和五年). The output is always in ISO 8601 Gregorian format (YYYY-MM-DD or YYYY where month and day are absent). A `calendar_conversion` metadata field records the original era name and year for traceability.

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

## 9. German (de) — Script: Latin

### Writing system
German is written in Latin script with four additional characters: three umlaut vowels (Ä, Ö, Ü) and the ligature ß (eszett / sharp-s). These characters do not exist in ASCII and are handled inconsistently across databases and legacy systems.

### Standard applied
**Umlaut expansion** (Ä→AE, Ö→OE, Ü→UE, ß→SS) is the primary standard used in German passports prior to 2013 and remains the most common form on watchlists and screening databases. A secondary **umlaut-drop** form (Ä→A, Ö→O, Ü→U, ß→S) is generated as a variant to match databases that applied a simpler ASCII reduction.

### Transliteration strategy
German names are Latin-script and require **normalisation** rather than transliteration. The pipeline applies deterministic character mapping via `config.language_normalisation_tables.GERMAN_UMLAUT_EXPANSIONS` and `GERMAN_UMLAUT_DROPS`. No LLM is required.

### Key linguistic decisions
| Feature | Decision | Reason |
|---|---|---|
| Ä/Ö/Ü | Primary: AE/OE/UE; variant: A/O/U | Passport standard is expansion; legacy databases often use drop |
| ß | Primary: SS; variant: S | German government standard since 2013 is SS |
| Hyphenated given names | Primary: hyphen retained; variant: space-separated | Screening tools split on either delimiter |
| Noble particles (von/van/zu) | Preserved in primary; capitalised variant generated | German convention: particle lowercase unless leading the name |

### Known ambiguities
- **Database inconsistency**: Pre-2013 German passports issued by different federal states applied different conventions. Both expansion (MUELLER) and drop (MULLER) forms are generated as variants.
- **Swiss/Austrian names**: Switzerland and Austria use the same umlaut conventions but may include additional characters. The same handler applies to all German-language documents.

---

## 10. French (fr) — Script: Latin

### Writing system
French uses Latin script with extensive diacritic marks (accents): acute (é), grave (è, à, ù), circumflex (â, ê, î, ô, û), cedilla (ç), and diaeresis (ë, ï, ü). Two ligatures (œ, æ) also appear. French names also use typographic apostrophes for elision (d', l').

### Standard applied
**Accent stripping** to bare ASCII is the standard for KYC screening contexts. All diacritics are removed; ligatures are expanded (œ→OE, æ→AE). This follows the ICAO Doc 9303 standard and matches how French names appear on watchlists.

### Transliteration strategy
French is handled by the deterministic `_normalise_french()` function using `config.language_normalisation_tables.FRENCH_ACCENT_STRIP`. No LLM is required.

### Key linguistic decisions
| Feature | Decision | Reason |
|---|---|---|
| é/è/ê/ë → E | All forms stripped to E | ICAO and watchlist standard |
| ç → C | Cedilla stripped | Standard ASCII reduction |
| œ → OE, æ → AE | Ligature expansion | ISO/ICAO standard |
| d' / l' (elision) | Primary: apostrophe retained as space (D AVIGNON); variants include fused (DAVIGNON) and space forms | Screening databases use both forms inconsistently |
| de / du / de la / des | Preserved in primary; particle-dropped variant generated | Noble particles may be omitted in some databases |
| Hyphenated names | Primary: hyphen retained; variant: space-separated | Standard variant generation |

### Known ambiguities
- **Particle capitalisation**: When a French particle (de, du) begins the name in a record, it may be capitalised (De Gaulle vs de Gaulle). Both forms are in `allowed_variants`.

---

## 11. Spanish (es) — Script: Latin

### Writing system
Spanish uses Latin script with five accented vowel forms (á, é, í, ó, ú), the tilde letter ñ, and less commonly diaeresis ü. The inverted punctuation marks (¡, ¿) do not appear in personal names.

### Standard applied
**Accent stripping** to bare ASCII, with ñ mapped to N in the primary form. The ñ→NY variant is also generated because some romanisation systems and historical Spanish documents use the NY digraph (Señor → SENYOR / SENOR). ü is stripped to U.

### Transliteration strategy
Spanish is handled by the deterministic `_normalise_spanish()` function. No LLM is required.

### Key linguistic decisions
| Feature | Decision | Reason |
|---|---|---|
| á/é/í/ó/ú → A/E/I/O/U | Accent stripped | ICAO/watchlist standard |
| ñ → N | Primary form | Least-ambiguous ASCII reduction |
| ñ → NY | Variant | Older Spanish system; some watchlists use this form |
| Two-surname system | Both names preserved in full primary | Spanish naming convention; first surname (paternal) is the primary family identifier |
| de / del / de la / de los / de las | Preserved in primary; particle-dropped variant generated | Spanish noble/place-of-origin particles may be omitted in databases |

### Known ambiguities
- **Two-surname ordering**: Some databases store only the first (paternal) surname; others retain both. The `allowed_variants` list includes single-surname forms for cases where only one surname was indexed.

---

## 12. Italian (it) — Script: Latin

### Writing system
Italian uses Latin script with grave accents on certain vowels (à, è, ì, ò, ù) — primarily word-finally (città, perché) and in certain names. Apostrophe particles (D', Dell', L') are common in southern Italian surnames.

### Standard applied
**Grave accent stripping** to bare ASCII. Apostrophe handling follows Italian passport practice: the apostrophe is retained as a space in the primary form (D'Angelo → D ANGELO), with fused (DANGELO) and particle-dropped (ANGELO) variants.

### Transliteration strategy
Italian is handled by the deterministic `_normalise_italian()` function using `config.language_normalisation_tables.ITALIAN_ACCENT_STRIP`. No LLM is required.

### Key linguistic decisions
| Feature | Decision | Reason |
|---|---|---|
| à/è/ì/ò/ù → A/E/I/O/U | Grave accent stripped | Standard ASCII reduction |
| D'/Dell'/Dall'/L'/De'/Degli' | Primary: space (D ANGELO); variants: fused (DANGELO) and dropped (ANGELO) | Italian passport practice; databases use all three forms |
| Double consonants | Preserved exactly | Linguistically meaningful: Bianchi ≠ Bianci; Conti ≠ Contt |

### Known ambiguities
- **Southern Italian particles**: D', De', Di (without apostrophe) are common and treated differently. Di is retained as a word (DI STEFANO); D'/De' use the apostrophe stripping rule.

---

## 13. Korean (ko) — Script: Hangul (한글)

### Writing system
Korean uses Hangul, a featural alphabet developed in the 15th century. Hangul syllable blocks are composed of consonant and vowel jamo characters. Each syllable block is written as a single typographic unit (e.g. 한 = H+A+N), making it structurally different from European alphabets.

### Standard applied
**Revised Romanisation of Korea (RR)** — the official South Korean government standard (2000), used in passports since 2000 and on international databases. The pipeline implements RR via the `config.language_normalisation_tables.romanise_hangul()` function as a built-in fallback, with the `korean-romanizer` library used when available.

**McCune–Reischauer (MR)** variants are generated where surnames have documented MR forms, because older databases and North Korean documents use the MR system.

### Surname variant table
Korean has a small number of very common surnames, each with multiple documented romanisation variants across different systems and historical practice. The pipeline's `KOREAN_SURNAME_VARIANTS` lookup covers the most frequent:

| Hangul | RR (primary) | Documented variants |
|---|---|---|
| 이 | I | Yi, Lee, Rhee, Ri, Rhie |
| 박 | Bak | Park, Pak |
| 최 | Choe | Choi, Ch'oe |
| 류 | Ryu | Yu, Yoo, Lyu |
| 유 | Yu | Yoo, Ryu |
| 정 | Jeong | Jung, Chung, Chŏng |
| 권 | Gwon | Kwon, Kwŏn |
| 윤 | Yun | Yoon |
| 임 | Im | Lim |
| 조 | Jo | Cho |
| 신 | Sin | Shin |
| 노 | No | Roh |

All surname variants are added to `allowed_variants` to ensure matching against databases that use any of the documented forms.

### Name order
Korean names follow surname-first convention (e.g. 박지훈 = BAK JIHUN where BAK is the surname). The primary output follows Korean convention; `allowed_variants` includes the western given-name-first form (JIHUN BAK).

### Review requirement
All Korean results are flagged `review_required=True` because surname romanisation ambiguity is inherent and non-trivial. An analyst should confirm the specific romanisation form used in the source document.

### Key linguistic decisions
| Feature | Decision | Reason |
|---|---|---|
| RR as primary | Matches current South Korean passport standard | |
| Surname variant table | Hard-coded, not AI-generated | Variants are documented, finite, and well-established |
| Given name: fused vs hyphenated | Both variants generated | Korean passports fuse given names (JIHUN); some databases hyphenate (JI-HUN) |
| North Korean documents | MR forms included in variants where documented | Databases may use older MR forms for DPRK nationals |

---

## 14. English (en) — Script: Latin

### Writing system
Modern English uses the basic 26-letter Latin alphabet with no diacritics in standard usage. Relevant edge cases for KYC normalisation include: apostrophes in surnames (O'Brien, D'Souza), Mac/Mc prefix variants, St/Saint abbreviation pairs, and hyphenated given names.

### Standard applied
**Minimal normalisation** — uppercase conversion and NFKC Unicode normalisation. All meaningful characters are preserved. The processing layer is Layer 1 (RULE) for PRESERVE fields and Layer 2 (TRANSLITERATE / normalise) for person names and aliases.

### Transliteration strategy
English names are handled by the deterministic `_normalise_english()` function. No LLM is required.

### Key linguistic decisions
| Feature | Decision | Reason |
|---|---|---|
| Apostrophe (O'Brien) | Primary: retained (O'BRIEN); variants: O BRIEN, OBRIEN | All three forms appear on watchlists |
| Mac/Mc prefix | Both-case variants generated (MACDONALD, MCDONALD) | Historic databases use both forms inconsistently |
| Saint / St | Both forms generated as variants (ST JAMES, SAINT JAMES) | Addresses and surnames use both |
| Hyphens | Primary: hyphen retained; variants: space and fused | Jean-Pierre may appear as JEAN PIERRE or JEANPIERRE |
| Full-width characters | NFKC normalisation applied | Japanese/Chinese documents sometimes use full-width ASCII in name fields |

---

## 15. Preserve Fields — No Normalisation Required

Certain field types carry structured identifiers that must not be modified. These are handled by the rules engine and returned verbatim:

| Field type | Examples | Treatment |
|---|---|---|
| `passport_no` | X1234567, P123456789 | Preserved exactly as-is |
| `id_no` | National ID numbers | Preserved exactly as-is |
| `email` | user@domain.com | Preserved exactly as-is |

---

## 16. Addressing and Name Order — Cross-Language Notes

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

## 17. Script Auto-Detection

When the `language` field is absent from an input row, the pipeline falls back to unidecode-based Latin conversion as a last resort. For optimal results, the language code should always be supplied. If a document carries only a script type (e.g. "Cyrillic") without a specific language, the pipeline's Ukrainian-character detection heuristic can distinguish Russian from Ukrainian.

---

*Last updated: April 2026. Pipeline version: v3 (expanded language support: de, fr, es, it, ko, en; Belarusian handler; Japanese era-year conversion; HK Cantonese surname variants).*

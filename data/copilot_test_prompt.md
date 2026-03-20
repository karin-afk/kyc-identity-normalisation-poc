# KYC Identity Field Completion — Prompt for LLM

## Your task

You will receive a CSV file called `copilot_test.csv`. It contains 212 rows of identity fields extracted from KYC source documents. Each row has:
- `case_id` — unique identifier (do not change)
- `original_text` — the raw text exactly as it appears on the source document (do not change)
- Several **empty columns** that you must complete: `language`, `script`, `field_type`, `treatment`, `transliteration`, `variants`, `english`, `normalised`

You must return the **complete CSV** with all empty columns filled in, following the rules below exactly. Do not add or remove rows. Do not change `case_id` or `original_text`.

---

## Column definitions and rules

### `language`
ISO 639-1 two-letter code for the language of the `original_text`.

Accepted values: `ar` (Arabic), `ja` (Japanese), `ru` (Russian or Ukrainian), `zh` (Chinese — Mandarin), `el` (Greek), `en` (English)

- Detect from the script of `original_text`.
- If the text is in Latin script but contains Japanese characters like "KUSAKA HIROSHI", use `ja`.
- If the text is in Cyrillic and contains Ukrainian-exclusive characters (Є, І, Ї, Ґ), use `ru` (the pipeline handles both under the same code).
- If the text is already in Latin characters and is clearly an alphanumeric identifier (e.g. `A20799893`, `563982174`, `john.doe@test.com`), use `en`.

---

### `script`
The name of the writing system. Accepted values: `Arabic`, `Kanji`, `Katakana`, `Hiragana`, `Latin`, `Cyrillic`, `Han`, `Greek`

- Use `Han` for Chinese characters (simplified or traditional).
- Use `Latin` for text already in Latin characters regardless of which language.
- Mixed scripts in one cell: report the dominant script.

---

### `field_type`
The semantic type of the identity field. Accepted values:

| Value | When to use |
|---|---|
| `person_name` | Full name of an individual (given name, family name, patronymic) |
| `alias` | Alternative name, nickname, or "also known as" entry |
| `company_name` | Name of a legal entity, organisation, or corporation |
| `address` | Street address, city, district, country, or geographic location |
| `passport_no` | Passport or travel document number |
| `id_no` | National identity card number or similar structured ID |
| `email` | Email address |

Infer from the `original_text` content and, where helpful, from the `case_id` prefix patterns.

---

### `treatment`
The processing action the pipeline should apply. Accepted values:

| Value | When to use |
|---|---|
| `PRESERVE` | `passport_no`, `id_no`, `email` — output must exactly equal input |
| `TRANSLITERATE` | Person names and aliases written in a non-Latin script that have no standard English translation — convert sound to Latin letters |
| `TRANSLATE_NORMALISE` | Addresses and company names — semantically translate and normalise to standard English |
| `TRANSLATE_ANALYST` | Alias entries that contain descriptive phrases mixed with a name (e.g. "nicknamed", "also known as", "по прозвищу") — these require human analyst review |

---

### `transliteration`
The **primary romanised form** of the `original_text`, using the standard for that language. Leave empty for `PRESERVE` and `TRANSLATE_NORMALISE` cases.

Standards by language:
- **Arabic** — BGN/PCGN romanisation. Supply short vowels from name knowledge. Al-/El- prefix written as `Al-` (capitalised, hyphenated). ع (ayin) omitted.
- **Russian** — BGN/PCGN. Soft sign (ь) omitted. Ж→Zh, Х→Kh, Я→Ya, Ю→Yu, Ё→Yo.
- **Ukrainian** — Cabinet of Ministers 2010 standard. Є→Ye, І→I, Ї→I, Г→H, Г→H.
- **Japanese** — Hepburn romanisation (ICAO Doc 9303). Surname first. Long vowels without macrons (ō→o, ū→u). Kanji: use most common reading.
- **Chinese** — Pinyin without tone marks. Surname first. Given name fused (王小明 → Wang Xiaoming, not Wang Xiao Ming).
- **Greek** — ISO 843. ου→ou, θ→th, φ→ph, χ→ch.

---

### `variants`
A pipe-separated (`|`) list of **other accepted romanisations** that a KYC screening system should also accept as a match. Leave empty for `PRESERVE` cases.

Include variants for:
- **Arabic**: cover Mohammed/Mohamed/Muhammad/Mohammad family; Al-/El- variations; Hasan/Hassan etc.
- **Russian**: ei/ey/ij endings (Sergei/Sergey/Sergej); patronymic spelling variants.
- **Japanese**: given-name-first order; long vowel spellings (Taro/Tarou/Taroo); alternate kanji readings.
- **Chinese**: given-name-first order; split given name (Xiaoming / Xiao Ming); Wade-Giles variants for traditional characters.
- **Greek**: Ch/H variants (Christos/Hristos); Ev/Eu variants.
- Addresses and company names: include common abbreviations (St/Street, Ave/Avenue, Co/Company), word-order variants, legal suffix variants (Co Ltd / Corporation / Corp).

Separate values with `|`. No trailing pipe. If no meaningful variant exists, leave empty.

---

### `english`
The natural English rendering — the form a human analyst would write or recognise. Rules:
- For **person names**: same as `transliteration` (the romanised name is the English form). May differ in capitalisation convention — use title case here (e.g. "Muhammad Ali Hasan").
- For **addresses**: the translated English address in natural form with commas (e.g. "Sheikh Zayed Road, Dubai").
- For **company names**: the established English trade name if one exists (e.g. "Toyota Co Ltd", "Mitsubishi Corporation"); otherwise a literal translation in title case.
- For **aliases**: the full semantic English rendering including any descriptive phrase (e.g. "Abu Muhammad al-Julani", "Alexander nicknamed Sasha").
- For **PRESERVE** fields: same as `original_text`.
- Leave empty only if the field is ambiguous and cannot be determined.

---

### `normalised`
The **uppercase screener form** — the primary form used for exact string matching against sanctions lists. Rules:
- Take the `transliteration` (or the translated English for addresses/company names).
- Uppercase everything.
- Remove hyphens from Al-/El- prefixes → `AL JULANI` not `AL-JULANI`.
- Remove commas and full stops.
- Remove legal suffix punctuation (S.A. → SA).
- For addresses: include the key location components separated by spaces. Drop administrative suffixes like "District", "City", "Province" unless they are part of the canonical place name.
- For `PRESERVE` fields: same as `original_text` (keep as-is, including case).

---

## Linguistic rules — language by language

### Arabic person names
- BGN/PCGN primary output with vowels supplied from name knowledge.
- Always generate a rich `variants` list — Arabic names have 4–8 common variant spellings.
- `Al-` prefix: write as `AL` (no hyphen) in `normalised`.
- Compound elements: `Abd al-Rahman` → `ABDULRAHMAN` or `ABDEL RAHMAN` (both forms in variants).
- Ibn/Bin particle: both forms in variants.

### Japanese person names
- Surname first in `normalised` (e.g. `YAMADA TARO`, not `TARO YAMADA`).
- Given-name-first form goes in `variants`.
- Long vowels (ō → O, not OU/OO): primary form uses single letter; OU/OO variants go in `variants`.
- For Kanji: use the most common reading as primary; alternate readings go in `variants`.

### Chinese person names  
- Surname first, given name fused: `WANG XIAOMING`, not `WANG XIAO MING`.
- Given-name-first and split-given-name forms go in `variants`.
- Traditional characters (TW): both Pinyin and Wade-Giles variants should be represented.

### Russian/Ukrainian person names
- Full name including patronymic if present.
- Soft sign (ь) → omit (do not produce apostrophe or Y).
- Я → YA (not JA), Ю → YU (not JU), Й → Y.
- Ukrainian Є → YE, І → I.

### Greek person names
- ISO 843 mapping.
- ου → OU (not OY).
- θ → TH, φ → PH, χ → CH.

### Addresses (all languages)
- Translate all components to English.
- Preserve proper names that have standard English forms (e.g. "Shinjuku" stays "Shinjuku", not translated).
- Use standard English geographic terms (Street, Avenue, Road, Boulevard, District).
- English word order: number first, then street name (UK/US convention).
- `normalised`: all caps, no commas, drop administrative suffixes (District, City, Province, Prefecture) unless they are part of the canonical name.

### Company names (all languages)
- Translate to established English name if a well-known English form exists (Toyota, Mitsubishi, Tencent, TSMC).
- If no established English name, translate the descriptive components and map the legal suffix:
  - 有限公司 → Co Ltd
  - 株式会社 → Co Ltd (or KK if not resolved)
  - ООО → LLC
  - Ανώνυμη Εταιρεία → SA
  - شركة ... المحدودة → Co Ltd
- `normalised`: all caps, no punctuation in legal suffixes (CO LTD, LLC, SA).

### PRESERVE fields
- `treatment` = PRESERVE
- `transliteration`, `variants`, `english` = leave empty or copy `original_text`
- `normalised` = exact copy of `original_text`

### TRANSLATE_ANALYST aliases
- `treatment` = TRANSLATE_ANALYST
- `transliteration` = leave empty
- `english` = full semantic translation of the entire phrase (translate descriptive words, transliterate the name component)
- `normalised` = uppercase of `english`, no commas

---

## Output format

Return the **complete CSV** with all 212 rows and all 10 columns. Maintain the exact same column order:

```
case_id,original_text,language,script,field_type,treatment,transliteration,variants,english,normalised
```

Rules for CSV formatting:
- Enclose any field containing a comma or pipe `|` in double-quotes.
- Do not add extra columns.
- Do not change `case_id` or `original_text` values.
- Use UTF-8 encoding.
- One row per case, 212 rows total.

---

## Quality checklist before returning

- [ ] Every row has a non-empty `language`, `script`, `field_type`, `treatment`, and `normalised`.
- [ ] `PRESERVE` rows: `normalised` = `original_text` exactly.
- [ ] Arabic person names: `variants` has at least 3 entries.
- [ ] Japanese Kanji names: `variants` includes given-name-first form.
- [ ] Chinese names: given name is fused in `normalised` (not split).
- [ ] Addresses: `normalised` is all caps, no commas, administrative suffixes dropped.
- [ ] Company names with well-known brands: `normalised` uses the established English name (TOYOTA, MITSUBISHI, TENCENT, TAIWAN SEMICONDUCTOR MANUFACTURING).
- [ ] `TRANSLATE_ANALYST` rows: `treatment` = TRANSLATE_ANALYST, `english` is fully translated.

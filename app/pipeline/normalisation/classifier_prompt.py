"""GPT-4o-mini field type classifier prompt.

Used when CLASSIFIER_MODE=llm in .env. The deterministic regex
classifier is used when CLASSIFIER_MODE=regex.
"""

CLASSIFIER_SYSTEM_PROMPT = """You are a field-type classifier for a KYC (Know Your Customer) identity normalisation pipeline used by a regulated bank for sanctions screening. Your job is to look at a single piece of text extracted from an identity document, registry record, or invoice, and classify it into exactly one field type and one source language.

You MUST return a JSON object and nothing else. No preamble, no explanation, no code fences. Schema:

{
  "field_type": "<one of the values below>",
  "language": "<one of the ISO codes below>",
  "confidence": <float between 0.0 and 1.0>
}

# FIELD TYPES (return exactly one, case-sensitive)

Identity & person fields:
- "person_name"       — a person's name (given + surname, in any order, any script). Including patronymics, lineage markers (bint, bin, ibn, ben), titles attached to names.
- "alias"             — an alternative name with a connector phrase ("also known as", "aka", "dit", "detto", "又名", "по прозвищу", "γνωστός ως", "별칭", "别名"). If the text contains BOTH a name and a connector, it is an alias.
- "nationality"       — a country name or nationality adjective (Germany, German, ألمانيا, 日本人, Saudi).
- "city"              — a city or settlement name without street/number context (Tokyo, القاهرة, 北京, 서울).
- "address"           — a street address. Contains street name + house/building number, OR district + city, OR multiple address components. Postal codes alone count.

Document identifiers (each preserved verbatim — DO NOT confuse them):
- "passport_no"       — passport number. Typically 1-2 letters + 6-9 digits (TK1234567, MJ0991103, A20799893). Sometimes purely numeric (Russian: 703819524). NOT to be confused with iban.
- "iban"              — International Bank Account Number. Starts with 2 letters (country code) + 2 check digits + up to 30 alphanumeric. Often spaced into groups of 4 (GB29 NWBK 6016 1331 9268 19). Must be 15-34 chars total.
- "lei_code"          — Legal Entity Identifier. EXACTLY 20 alphanumeric characters, no spaces (529900T8BM49AURSDO55).
- "id_number"         — any national/government identity number (social security, NI number, CURP, residence card, ID card). Use this for ALL of: НI number, SSN, CURP, NIF, DNI, residency cards, codice fiscale, MyNumber, Hong Kong HKID, alien registration. Do NOT invent variants like "id_no", "national_id", "ssn" — always return "id_number".
- "tax_id"            — tax identification number (VAT, UTR, ИНН, Steuer-ID, Steuernummer, NIF tax form). German VAT numbers start with "DE".
- "registration_no"   — company registration number from a registry (Companies House number, OGRN, HRB, SIREN, Partita IVA, hojin bango).
- "reference_no"      — invoice or document reference (REF-2024-001, FT-..., INV-...).
- "phone_number"      — telephone number, with or without country code, in any script.
- "email"             — contains an "@" with text on both sides.

Dates:
- "date_of_birth"     — a date intended as a birth date. If the text is plainly a date and there is no contextual evidence it's an expiry or issue date, default to date_of_birth.
- "issue_date"        — explicitly labelled as an issue date.
- "expiry_date"       — explicitly labelled as an expiry date.

Corporate registry fields:
- "company_name"      — a company name, with or without legal-form suffix/prefix.
- "legal_form"        — a legal form designator on its own (株式会社, GmbH, ООО, S.p.A., S.A.R.L., Α.Ε., 주식회사, شركة محدودة). If the legal form is embedded in a longer company name, classify as company_name.
- "status"            — a company status word/phrase (active, dissolved, in liquidation, struck off, 現役, منتهي, действующая, dissoute, 存续, 吊销, aufgelöst, en liquidación).
- "role"              — a corporate role/title (director, auditor, general manager, Gérant, 取締役, 代表取締役, 監査役, 監事, 監査役, مدير عام, Генеральный директор).

Financial values (treat as numeric formats):
- "share_capital"     — a financial amount in a share-capital context, usually with currency symbol or label.
- "total_assets"      — a financial amount in a balance-sheet context (assets, liabilities, equity, revenue, expenses). Use when in doubt for amounts with thousands separators that are not clearly share_capital.

Free text:
- "free_text"         — prose, narrative, multi-clause sentences. Invoice lines with date+amount+label ("Payment due X amount Y"), narrative descriptions, anything that is a sentence rather than a single field.

Fallback:
- "unknown"           — use ONLY when the text genuinely does not fit any category above. Better to return unknown than to guess wrongly.

# LANGUAGES (return exactly one ISO 639-1 code, lowercase)

"ar" Arabic, "de" German, "el" Greek, "en" English, "es" Spanish, "fa" Persian/Farsi, "fr" French, "he" Hebrew, "it" Italian, "ja" Japanese, "ko" Korean, "nl" Dutch, "no" Norwegian, "pl" Polish, "pt" Portuguese, "ru" Russian, "th" Thai, "tr" Turkish, "uk" Ukrainian, "zh" Chinese, "unknown"

Disambiguation rules for language:
- Cyrillic with Ї/Є/І → "uk" (Ukrainian-specific characters)
- Cyrillic with Ў → "be" (Belarusian); if "be" is not in the list above, return "unknown"
- Cyrillic otherwise → "ru"
- Han characters with hiragana/katakana → "ja", even if mostly kanji
- Han characters without kana → "zh"
- Hangul → "ko"
- Pure ASCII/Latin with no diacritics and no language-specific words → "en" by default
- Latin script with German-specific characters (ß, ä, ö, ü) → "de"
- Latin script with French-specific characters (ç, é-è-ê combinations, French words like "rue", "Société") → "fr"
- Latin script with Spanish-specific characters (ñ, accented vowels, Spanish words like "Calle", "Sociedad") → "es"
- Latin script with Italian words ("Via", "S.p.A.", "Società") → "it"
- Latin script with Portuguese tilde (ã, õ) → "pt"
- For a pure number or pure identifier with no script signal, infer from any country prefix (DE→de, GB→en, FR→fr) or default to "en"
- Mixed-script inputs: choose the language of the meaningful content, not the digits

# FIELD TYPE DISAMBIGUATION RULES (apply in order)

1. If text contains "@" with content on both sides → email.
2. If text is 20 alphanumeric chars, no spaces, no special chars → lei_code.
3. If text starts with 2 letters + 2 digits + 11-30 alphanumerics (possibly spaced into groups of 4) → iban.
4. If text contains a connector phrase ("also known as", "aka", "alias", "dit ", "detto ", "又名", "по прозвищу", "별칭", "γνωστός ως") → alias.
5. If text is a multi-clause sentence with verbs, labels, and values → free_text.
6. If text is 1-2 letters followed by 6-9 digits (possibly with the letter at the start) → passport_no UNLESS clearly an IBAN (rule 3) or LEI (rule 2).
7. If text contains a currency symbol (¥ € $ £ ﷼ ₩ ₽) or "EUR"/"USD"/"GBP"/"JPY"/"RUB"/"KRW"/"SAR" followed by a number → share_capital.
8. If text contains a financial-context label ("total assets", "revenue", "総資産", "Aktiva", "доход") with a number → total_assets.
9. If text is purely a number with thousands separators (Western 12,500 / European 12.500 / French 12 500 / Swiss 1'234'567 / Arabic ١٢٬٥٠٠ / Han 五千) → share_capital or total_assets depending on context; if no context, default to total_assets.
10. If text is a date pattern (DD/MM/YYYY, DD.MM.YYYY, YYYY-MM-DD, era markers like 令和/昭和/پ.ش./พ.ศ./Reiwa/Showa, Han/Hebrew/Arabic-Indic numerals for years) → date_of_birth UNLESS the surrounding text explicitly labels it as issue or expiry.
11. If text is just a number 6-15 digits, with or without internal spaces/dashes/brackets, and not a date → id_number for natural persons context, registration_no for company context. When unclear, return id_number.
12. If text is a phone-formatted number (starts with + or 0, includes country code or area code formatting) → phone_number.
13. If text is a single word that is a known country/place → city if a city name, nationality if a country/nationality adjective. Adjectival forms ("سعودي", "日本人") still classify as nationality.
14. If text is a known legal form on its own → legal_form. If embedded in a longer name → company_name.
15. If text is a name (one or more capitalised words, possibly with particles like "von", "de", "al-", "bin") → person_name.

# CONFIDENCE CALIBRATION

- 0.95+ : The input has a strong unambiguous signal (an "@" sign, a clear IBAN pattern, an era marker, a legal-form word). Apply only when at least one rule above fires cleanly.
- 0.80-0.94 : Clear field type from structure but not from a specific marker (e.g. a date in a common format, a name in capitalised words, an amount with a currency symbol).
- 0.60-0.79 : Inferred field type from context (e.g. "12,500" with no currency could be total_assets or share_capital; pure number could be id_number, passport_no, or registration_no).
- 0.40-0.59 : Genuine uncertainty; the input could plausibly fit 2-3 field types.
- Below 0.4 : Return "unknown" instead.

# DO NOT

- Do not return any field_type or language value not in the lists above.
- Do not invent suffixes like "id_no", "national_id", "ssn", "full_name", "family_name", "given_name", "accounting_policies", "unstructured_text". The valid set is fixed.
- Do not return confidence 0.95 unless a hard rule fires.
- Do not wrap the JSON in code fences or add commentary.
- Do not classify free_text as date_of_birth or amount fields just because they contain dates or amounts — if it's a full sentence with multiple clauses, it is free_text."""


CLASSIFIER_USER_PROMPT_TEMPLATE = """Classify this text:

{text}

Return JSON only."""


# ── Few-shot examples (optional but improves consistency) ─────────────────────
# Add as messages alternating user/assistant if you use the chat completions
# format. These cover the ambiguity cases that the unprimed model gets wrong.

FEW_SHOT_EXAMPLES = [
    # IBAN vs passport vs tax_id disambiguation
    ("GB29 NWBK 6016 1331 9268 19",
     '{"field_type":"iban","language":"en","confidence":0.98}'),
    ("DE811100090",
     '{"field_type":"tax_id","language":"de","confidence":0.92}'),
    ("529900T8BM49AURSDO55",
     '{"field_type":"lei_code","language":"en","confidence":0.97}'),
    ("TK1234567",
     '{"field_type":"passport_no","language":"en","confidence":0.92}'),

    # id_number canonicalisation (NEVER return id_no)
    ("NI AB 12 34 56 C",
     '{"field_type":"id_number","language":"en","confidence":0.95}'),
    ("A123456(3)",
     '{"field_type":"id_number","language":"zh","confidence":0.85}'),
    ("٢٩٨٠٣١٤١٥٠١٢٣٤",
     '{"field_type":"id_number","language":"ar","confidence":0.90}'),

    # person_name (NEVER return full_name / family_name / given_name)
    ("Иванова Наталья Александровна",
     '{"field_type":"person_name","language":"ru","confidence":0.95}'),
    ("Ірина Миколаївна Шевченко",
     '{"field_type":"person_name","language":"uk","confidence":0.95}'),
    ("Muñoz",
     '{"field_type":"person_name","language":"es","confidence":0.85}'),
    ("Łódź",
     '{"field_type":"city","language":"pl","confidence":0.90}'),
    ("İstanbul",
     '{"field_type":"city","language":"tr","confidence":0.95}'),

    # alias detection by connector word
    ("Александр по прозвищу Саша",
     '{"field_type":"alias","language":"ru","confidence":0.95}'),
    ("Pierre-Henri Lefèvre dit Le Vieux",
     '{"field_type":"alias","language":"fr","confidence":0.95}'),
    ("Mario De Luca detto Il Professore",
     '{"field_type":"alias","language":"it","confidence":0.95}'),
    ("王强又名王小强",
     '{"field_type":"alias","language":"zh","confidence":0.95}'),
    ("John Michael Smith also known as Johnny Smith",
     '{"field_type":"alias","language":"en","confidence":0.97}'),

    # free_text (multi-clause prose with dates/amounts)
    ("支払期限は二〇二六年九月五日、金額は五千円です。",
     '{"field_type":"free_text","language":"ja","confidence":0.95}'),
    ("Срок оплаты: 05.09.2026, сумма: 12 500 руб.",
     '{"field_type":"free_text","language":"ru","confidence":0.95}'),
    ("Zahlungsziel: 05.09.2026, Betrag: 12.500 EUR",
     '{"field_type":"free_text","language":"de","confidence":0.95}'),
    ("지급기한: 2026년 09월 05일, 금액: 12,500 원",
     '{"field_type":"free_text","language":"ko","confidence":0.95}'),

    # share_capital with currency symbol
    ("¥1,234,567",
     '{"field_type":"share_capital","language":"ja","confidence":0.92}'),
    ("﷼500,000",
     '{"field_type":"share_capital","language":"ar","confidence":0.92}'),

    # nationality vs city
    ("日本",
     '{"field_type":"nationality","language":"ja","confidence":0.85}'),
    ("日本人",
     '{"field_type":"nationality","language":"ja","confidence":0.93}'),
    ("東京",
     '{"field_type":"city","language":"ja","confidence":0.92}'),
    ("北京",
     '{"field_type":"city","language":"zh","confidence":0.92}'),
    ("سعودي",
     '{"field_type":"nationality","language":"ar","confidence":0.88}'),

    # legal_form (standalone) vs company_name (embedded)
    ("株式会社",
     '{"field_type":"legal_form","language":"ja","confidence":0.97}'),
    ("S.A.R.L.",
     '{"field_type":"legal_form","language":"fr","confidence":0.95}'),
    ("S.A.B. de C.V.",
     '{"field_type":"legal_form","language":"es","confidence":0.93}'),
    ("شركة محدودة",
     '{"field_type":"legal_form","language":"ar","confidence":0.92}'),
    ("三菱商事株式会社",
     '{"field_type":"company_name","language":"ja","confidence":0.95}'),
    ("ПАО Газпром",
     '{"field_type":"company_name","language":"ru","confidence":0.95}'),

    # phone_number with full-width digits
    ("０８０−１２３４−５６７８",
     '{"field_type":"phone_number","language":"ja","confidence":0.95}'),
    ("+٩٧١ ٥٠ ١٢٣ ٤٥٦٧",
     '{"field_type":"phone_number","language":"ar","confidence":0.95}'),

    # Numeric without language script — infer from country prefix
    ("12 500",
     '{"field_type":"share_capital","language":"en","confidence":0.55}'),
    ("12,500",
     '{"field_type":"share_capital","language":"en","confidence":0.55}'),

    # OCR ambiguity — return unknown rather than guess
    ("REF-Ι23O5",
     '{"field_type":"reference_no","language":"el","confidence":0.65}'),
    ("СЧЕТ 5O12А8",
     '{"field_type":"reference_no","language":"ru","confidence":0.65}'),

    # ISO 8601 compact date
    ("20250508",
     '{"field_type":"date_of_birth","language":"en","confidence":0.70}'),

    # Short ambiguous string
    ("SA",
     '{"field_type":"legal_form","language":"fr","confidence":0.55}'),

    # Compact non-Gregorian dates — classifier must return the date field type
    # so the CALENDAR strategy can apply the right conversion (T3-4)
    ("2568/5/8",
     '{"field_type":"date_of_birth","language":"th","confidence":0.85}'),
    ("1404/2/15",
     '{"field_type":"date_of_birth","language":"fa","confidence":0.85}'),
    ("114/5/8",
     '{"field_type":"date_of_birth","language":"zh","confidence":0.80}'),

    # Accounting-format negatives — △ and full-width parentheses (T3-5)
    ("\u25b34,191",
     '{"field_type":"share_capital","language":"ja","confidence":0.88}'),
    ("\uff084,191\uff09",
     '{"field_type":"share_capital","language":"ja","confidence":0.88}'),

    # Space-separated European/Russian thousands (T3-6)
    ("1 234 567",
     '{"field_type":"share_capital","language":"fr","confidence":0.70}'),

    # Han spoken-digit phone sequence — per-character digit string, not positional (T3-7)
    ("\u4e00\u4e09\u516b\u96f6\u96f6\u4e00\u4e09\u516b\u96f6\u96f6\u96f6",
     '{"field_type":"phone_number","language":"zh","confidence":0.85}'),

    # Short German person name — prevents misclassification as free_text (T9-G2)
    ("Stra\u00dfe",
     '{"field_type":"person_name","language":"de","confidence":0.75}'),
]
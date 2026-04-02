"""Cantonese surname map for KYC identity normalisation.

Pipeline layer: Layer 2 (deterministic) — used to generate Cantonese (Jyutping)
surname variants for Hong Kong (HK) documents when standard Mandarin Pinyin
romanisation would produce the wrong form.

Example: 黃 romanises as "Huang" in Mandarin Pinyin but as "Wong" in Cantonese,
which is the form that appears on Hong Kong identity documents and bank records.
"""

# ---------------------------------------------------------------------------
# Cantonese surname map: Hanzi → Jyutping romanisation
# ---------------------------------------------------------------------------
# Key: Traditional Chinese surname character (as used in HK documents)
# Value: Standard Cantonese (Jyutping) romanisation as found on HK documents
# ---------------------------------------------------------------------------

CANTONESE_SURNAME_MAP: dict[str, str] = {
    "黃": "Wong",    # Mandarin: Huang
    "陳": "Chan",    # Mandarin: Chen
    "李": "Lee",     # Mandarin: Li
    "張": "Cheung",  # Mandarin: Zhang
    "劉": "Lau",     # Mandarin: Liu
    "林": "Lam",     # Mandarin: Lin
    "吳": "Ng",      # Mandarin: Wu
    "鄭": "Cheng",   # Mandarin: Zheng
    "楊": "Yeung",   # Mandarin: Yang
    "許": "Hui",     # Mandarin: Xu
    "何": "Ho",      # Mandarin: He
    "梁": "Leung",   # Mandarin: Liang
    "鄧": "Tang",    # Mandarin: Deng
    "蔡": "Choi",    # Mandarin: Cai
    "謝": "Tse",     # Mandarin: Xie
    "曾": "Tsang",   # Mandarin: Zeng
    "蕭": "Siu",     # Mandarin: Xiao
    "江": "Kong",    # Mandarin: Jiang
    "潘": "Poon",    # Mandarin: Pan
    "羅": "Law",     # Mandarin: Luo
    "余": "Yu",      # Mandarin: Yu (same)
    "孫": "Suen",    # Mandarin: Sun
    "馬": "Ma",      # Mandarin: Ma (same)
    "朱": "Chu",     # Mandarin: Zhu
    "胡": "Wu",      # Mandarin: Hu
    "高": "Ko",      # Mandarin: Gao
    "郭": "Kwok",    # Mandarin: Guo
    "周": "Chow",    # Mandarin: Zhou
    "唐": "Tong",    # Mandarin: Tang
    "徐": "Tsui",    # Mandarin: Xu
}

# ---------------------------------------------------------------------------
# Wade-Giles initial consonant substitutions (for TW documents)
# ---------------------------------------------------------------------------
# These are the most common systematic differences between Pinyin and Wade-Giles.
# Applied to the full name string to generate a TW variant.

WADE_GILES_INITIALS: list[tuple[str, str]] = [
    ("zh", "ch"),
    ("x",  "hs"),
    ("q",  "ch"),
    ("z",  "ts"),
    ("c",  "ts"),
    ("r",  "j"),
]

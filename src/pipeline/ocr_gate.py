"""
OCR Gate — GPT-4o Vision implementation.

Accepts a path to a document image (passport, ID card, proof of address, etc.)
and returns a list of extracted field rows ready for process_field().

Each row matches the golden dataset schema:
    field_type, original_text, language, document_type, ocr_confidence

Requires OPENAI_API_KEY in .env.
Supports: jpg, jpeg, png, webp, gif (static).
"""

import base64
import json
import os
from pathlib import Path

import openai

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.75"))
MODEL = "gpt-4o"

_EXTRACT_PROMPT = """\
You are a KYC document analyst. Extract all identity fields from this document image.

Return a JSON array. Each element must have exactly these keys:
  "field_type"      — one of: person_name, alias, passport_no, id_no, email,
                      address, company_name, date_of_birth, nationality,
                      place_of_birth, issuing_authority
  "original_text"   — exact text as it appears in the document, in its original script
  "language"        — ISO 639-1 code of the script language (e.g. en, ar, ja, ru, zh, el)
  "document_type"   — one of: passport, id_card, proof_of_address, corporate_registry,
                      sanctions_profile
  "ocr_confidence"  — your confidence in the extraction accuracy, 0.0 to 1.0

Rules:
- NEVER translate or normalise values. Extract exactly as printed.
- NEVER invent values. If a field is not visible, omit it.
- Passport/ID numbers must be copied character-for-character.
- Output ONLY the JSON array. No explanation, no markdown fences.

Example output:
[
  {"field_type": "person_name", "original_text": "山田 太郎", "language": "ja",
   "document_type": "passport", "ocr_confidence": 0.95},
  {"field_type": "passport_no", "original_text": "TK1234567", "language": "en",
   "document_type": "passport", "ocr_confidence": 0.99}
]
"""


def _image_to_base64(image_path: str) -> tuple[str, str]:
    """Return (base64_string, mime_type) for the given image file."""
    suffix = Path(image_path).suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime = mime_map.get(suffix, "image/jpeg")
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8"), mime


def check_ocr_confidence(row: dict) -> bool:
    """Return True if the row's OCR confidence meets the threshold."""
    return float(row.get("ocr_confidence", 1.0)) >= OCR_CONFIDENCE_THRESHOLD


def extract_fields_from_image(image_path: str) -> list[dict]:
    """
    Extract structured identity fields from a document image using GPT-4o Vision.

    Returns a list of field dicts ready to pass to process_field().
    Fields with ocr_confidence below OCR_CONFIDENCE_THRESHOLD are flagged
    but still returned — the pipeline will mark them review_required=True.

    Raises EnvironmentError if OPENAI_API_KEY is not set.
    Raises ValueError if GPT-4o returns unparseable output.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    b64, mime = _image_to_base64(image_path)

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _EXTRACT_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                ],
            }
        ],
        max_tokens=1000,
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if the model wraps output despite instructions
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        fields: list[dict] = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"GPT-4o returned non-JSON output for {image_path}:\n{raw}"
        ) from exc

    # Add source image path for traceability
    for field in fields:
        field.setdefault("source_image", str(Path(image_path).name))

    return fields


For the model — GPT-4o-mini. It is more than sufficient for a classification task (selecting from a fixed list of field types and a fixed list of language codes). It is fast, cheap, and reliable for structured output. GPT-4o is overkill for this — you are not doing translation or reasoning, just classification.

Copilot instructions — Paste tab LLM classification
1. Remove from app/templates/paste.html
Remove the field type dropdown and the language hint dropdown entirely. The textarea and the submit button remain. The character counter remains.

2. Add to app/pipeline/normalisation/field_type_detector.py
Replace the existing heuristic detect_field_type() function with an LLM-based classifier. The existing file and function name stay the same so no other code needs to change.
pythonimport os
import json
from openai import OpenAI

_client = OpenAI()  # reads OPENAI_API_KEY from environment

FIELD_TYPES = [
    "person_name", "company_name", "address", "date_of_birth",
    "nationality", "legal_form", "status", "role",
    "nature_of_business", "issuing_authority", "unstructured_text"
]

LANGUAGE_CODES = [
    "ar", "be", "bg", "da", "de", "el", "en", "es", "fa",
    "fr", "he", "it", "ja", "ko", "nl", "no", "pl", "pt",
    "ru", "sv", "th", "tr", "uk", "zh"
]

def detect_field_type(text: str, language: str = "") -> tuple[str, float, str]:
    """
    Use GPT-4o-mini to classify the field type and language of pasted text.

    Returns:
        Tuple of (field_type: str, confidence: float, language_code: str)

    Falls back to ("unstructured_text", 0.5, "en") on any error so the
    pipeline never crashes — it simply routes to native speaker review.
    """
    try:
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=60,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a KYC data classifier. Given a text snippet, "
                        "return ONLY a JSON object with three fields: "
                        "'field_type' (one of: " + ", ".join(FIELD_TYPES) + "), "
                        "'language_code' (ISO 639-1, one of: " + ", ".join(LANGUAGE_CODES) + "), "
                        "'confidence' (float 0.0-1.0). "
                        "No explanation. No markdown. JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": text[:500]  # cap input to keep cost low
                }
            ]
        )
        result = json.loads(response.choices[0].message.content)
        field_type = result.get("field_type", "unstructured_text")
        language   = result.get("language_code", "en")
        confidence = float(result.get("confidence", 0.5))

        # Validate against known lists
        if field_type not in FIELD_TYPES:
            field_type = "unstructured_text"
        if language not in LANGUAGE_CODES:
            language = "en"

        return field_type, confidence, language

    except Exception:
        return "unstructured_text", 0.5, "en"

3. Update app/routes/paste.py
The POST /paste/translate endpoint calls detect_field_type() unconditionally (no more if field_type == "auto" branch). Then passes the detected values straight to the orchestrator.
python@paste_bp.route("/translate", methods=["POST"])
def translate():
    text = request.form.get("text", "").strip()

    if not text:
        return '<p class="notice notice-flag">Please enter some text.</p>', 400
    if len(text) > 2000:
        return '<p class="notice notice-flag">Text exceeds 2,000 characters. Please upload as a file instead.</p>', 400

    # Step 1 — classify with LLM
    from app.pipeline.normalisation.field_type_detector import detect_field_type
    field_type, classification_confidence, language = detect_field_type(text)

    # Step 2 — normalise with orchestrator
    try:
        from app.pipeline.orchestrator import process_field_row
        result = process_field_row({
            "original_text": text,
            "field_type":    field_type,
            "language":      language,
        })
        result["detected_field_type"]            = field_type
        result["detected_language"]              = language
        result["classification_confidence"]      = classification_confidence

        return render_template("partials/paste_result.html",
                               result=result,
                               original=text)

    except Exception as e:
        return f'<p class="notice notice-flag">Error: {e}</p>', 400

4. Update app/templates/partials/paste_result.html
Add two metadata items to the result display — detected language and detected field type — alongside the existing method, confidence, and variants:
Language:    Japanese (ja)
Field type:  Person name
Method:      TRANSLITERATION
Confidence:  90%

5. .env note
OPENAI_API_KEY must be set for the paste tab to work. If it is not set, detect_field_type() catches the exception and returns ("unstructured_text", 0.5, "en") — the paste tab still works but routes everything to native speaker review. No crash.

Acceptance criteria

The paste tab has no dropdowns — textarea and submit button only.
Submitting text calls GPT-4o-mini, which returns field type and language.
These are passed to the existing orchestrator unchanged.
The result partial shows detected language, detected field type, normalisation method, confidence, normalised form, and variants.
If OPENAI_API_KEY is missing, the tab degrades gracefully to native speaker review without crashing.

---

Implementation TODO (tracked in this repo)
- [x] Confirm active template path and map instruction from paste.html to the runtime template.
- [x] Remove field-type and language dropdowns from paste tab UI while keeping textarea, submit button, and character counter.
- [x] Replace heuristic detect_field_type() with GPT-4o-mini classifier that returns field_type, language_code, and confidence.
- [x] Keep graceful fallback to ("unstructured_text", 0.5, "en") when OPENAI_API_KEY is missing or any API/parsing error occurs.
- [x] Update POST /paste/translate to always classify via detect_field_type() and pass detected values to orchestrator.
- [x] Update paste result metadata to show detected language and detected field type with existing method/confidence output.
- [x] Add/adjust tests for UI rendering, route behavior, detector parsing, and fallback behavior.
- [ ] Run tests, commit on a dedicated branch, push, and run local deployment for validation.
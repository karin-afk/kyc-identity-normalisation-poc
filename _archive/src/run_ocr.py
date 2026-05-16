"""
Run OCR + pipeline against a single document image.

Usage:
    python src/run_ocr.py data/images/passport/my_passport.jpg

Each extracted field is passed through the normalisation pipeline and
the results are printed and saved to data/output/ocr_<filename>_<timestamp>.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pipeline.ocr_gate import check_ocr_confidence, extract_fields_from_image
from pipeline.pipeline import process_field

_OUTPUT_DIR = Path(__file__).parent.parent / "data" / "output"


def run_ocr_pipeline(image_path: str) -> None:
    print(f"Processing: {image_path}")
    print("-" * 56)

    fields = extract_fields_from_image(image_path)
    print(f"Extracted {len(fields)} fields from image\n")

    results = []
    for field in fields:
        low_confidence = not check_ocr_confidence(field)
        result = process_field(field)

        if low_confidence:
            result["review_required"] = True
            result["review_reason"] = (
                f"OCR confidence {field.get('ocr_confidence')} below threshold"
            )

        results.append({**field, "pipeline_output": result})

        status = "REVIEW" if result.get("review_required") else "OK"
        print(
            f"  [{status}] {field['field_type']:20s} "
            f"{field['original_text']!r:30s} → {result.get('normalised_form', '')!r}"
        )

    # Save output
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = Path(image_path).stem
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = _OUTPUT_DIR / f"ocr_{stem}_{timestamp}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/run_ocr.py <image_path>")
        sys.exit(1)
    run_ocr_pipeline(sys.argv[1])

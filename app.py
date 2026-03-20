"""
KYC Identity Normalisation — Streamlit frontend
================================================
Run locally:  streamlit run app.py
Deploy:       Push to GitHub → connect Streamlit Community Cloud
              Add OPENAI_API_KEY in the Streamlit Cloud secrets dashboard.
"""

import os
import sys
import io
import csv

# ── Inject OPENAI_API_KEY from Streamlit secrets (cloud) ────────────────────
# Must happen before any pipeline import so llm_layer.py picks it up.
try:
    import streamlit as st
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass  # Running locally — .env will be loaded by llm_layer.py

import streamlit as st

# ── Add src/ to path so pipeline imports work ────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pipeline.pipeline import process_field  # noqa: E402

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KYC Identity Normalisation",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 KYC Identity Normalisation")
st.caption("Transliterate and normalise multilingual identity fields for KYC screening.")

# ── Sidebar: field type + language reference ─────────────────────────────────
with st.sidebar:
    st.header("Settings")
    FIELD_TYPES = ["person_name", "alias", "company_name", "address"]
    LANGUAGES = {
        "Auto-detect": "",
        "Arabic (ar)": "ar",
        "Chinese Mandarin (zh)": "zh",
        "Greek (el)": "el",
        "Japanese (ja)": "ja",
        "Russian (ru)": "ru",
        "Ukrainian (uk)": "uk",
        "English / Latin (en)": "en",
    }
    default_field = st.selectbox("Default field type", FIELD_TYPES, index=0)
    default_lang = st.selectbox("Default language", list(LANGUAGES.keys()), index=0)

    st.divider()
    st.markdown(
        "**Processing methods**\n"
        "- `RULE` — preserve as-is (dates, IDs)\n"
        "- `TRANSLIT` — deterministic transliteration\n"
        "- `LLM` — GPT-4o normalisation\n"
    )

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_single, tab_batch = st.tabs(["Single field", "Batch CSV"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single field
# ════════════════════════════════════════════════════════════════════════════
with tab_single:
    col1, col2 = st.columns([2, 1])

    with col1:
        text_input = st.text_area(
            "Original text",
            placeholder="e.g.  山田 太郎  /  Андрей Юрьевич  /  نهاد إبراهيم",
            height=100,
        )

    with col2:
        field_type = st.selectbox("Field type", FIELD_TYPES, key="single_ft",
                                  index=FIELD_TYPES.index(default_field))
        language = st.selectbox("Language", list(LANGUAGES.keys()), key="single_lang",
                                index=list(LANGUAGES.keys()).index(default_lang))

    if st.button("Normalise", type="primary", use_container_width=True):
        if not text_input.strip():
            st.warning("Please enter some text.")
        else:
            row = {
                "original_text": text_input.strip(),
                "field_type": field_type,
                "language": LANGUAGES[language],
            }
            with st.spinner("Processing…"):
                try:
                    result = process_field(row)
                    st.success("Done")

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Normalised form", result.get("normalised_form", "—"))
                    m2.metric("Method", result.get("processing_method", "—"))
                    m3.metric("Confidence", f"{result.get('confidence', 0):.0%}")

                    if result.get("review_required"):
                        st.warning(f"⚠️ Manual review required: {result.get('review_reason', '')}")

                    if result.get("allowed_variants"):
                        st.info("**Allowed variants:** " + "  |  ".join(result["allowed_variants"]))

                except Exception as exc:
                    st.error(f"Pipeline error: {exc}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Batch CSV
# ════════════════════════════════════════════════════════════════════════════
with tab_batch:
    st.markdown(
        "Upload a CSV with columns: **`original_text`**, **`field_type`**, **`language`** (optional).  \n"
        "Additional columns are passed through unchanged."
    )

    template_rows = [
        {"original_text": "山田 太郎", "field_type": "person_name", "language": "ja"},
        {"original_text": "Андрей Юрьевич Ковалев", "field_type": "person_name", "language": "ru"},
        {"original_text": "نهاد إبراهيم النجار", "field_type": "person_name", "language": "ar"},
        {"original_text": "Mitsubishi Corporation", "field_type": "company_name", "language": ""},
        {"original_text": "18 Tiyu East Road Tianhe District", "field_type": "address", "language": "zh"},
    ]
    template_buf = io.StringIO()
    writer = csv.DictWriter(template_buf, fieldnames=["original_text", "field_type", "language"])
    writer.writeheader()
    writer.writerows(template_rows)
    st.download_button(
        "⬇ Download template CSV",
        data=template_buf.getvalue().encode("utf-8"),
        file_name="kyc_template.csv",
        mime="text/csv",
    )

    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded is not None:
        content = uploaded.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        input_rows = list(reader)

        if "original_text" not in (reader.fieldnames or []):
            st.error("CSV must contain an `original_text` column.")
        elif "field_type" not in (reader.fieldnames or []):
            st.error("CSV must contain a `field_type` column.")
        else:
            st.write(f"Loaded **{len(input_rows)} rows**. Preview:")
            st.dataframe(input_rows[:5], use_container_width=True)

            if st.button("Run normalisation", type="primary", use_container_width=True):
                results = []
                progress = st.progress(0, text="Processing…")

                for i, row in enumerate(input_rows):
                    if not row.get("language"):
                        row["language"] = LANGUAGES.get(default_lang, "")
                    try:
                        out = process_field(row)
                    except Exception as exc:
                        out = {
                            "normalised_form": "",
                            "processing_method": "ERROR",
                            "confidence": 0.0,
                            "review_required": True,
                            "review_reason": str(exc),
                            "allowed_variants": [],
                        }
                    results.append({**row, **{
                        "normalised_form": out.get("normalised_form", ""),
                        "processing_method": out.get("processing_method", ""),
                        "confidence": f"{out.get('confidence', 0):.0%}",
                        "review_required": out.get("review_required", False),
                        "review_reason": out.get("review_reason", ""),
                        "allowed_variants": " | ".join(out.get("allowed_variants") or []),
                    }})
                    progress.progress((i + 1) / len(input_rows),
                                      text=f"Processing {i + 1}/{len(input_rows)}…")

                progress.empty()
                st.success(f"Processed {len(results)} rows")
                st.dataframe(results, use_container_width=True)

                # Download button
                out_buf = io.StringIO()
                fieldnames = list(results[0].keys()) if results else []
                out_writer = csv.DictWriter(out_buf, fieldnames=fieldnames)
                out_writer.writeheader()
                out_writer.writerows(results)
                st.download_button(
                    "⬇ Download results CSV",
                    data=out_buf.getvalue().encode("utf-8"),
                    file_name="kyc_normalised.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

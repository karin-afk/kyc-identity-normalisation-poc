"""
KYC Identity Normalisation — Streamlit frontend (v2)
====================================================
Tabs:
  1. 🆔 KYC Normalise  — transliterate/normalise a single identity field
  2. 📄 Documents       — upload passport scans / PDFs / DOCX / TXT and
                          auto-extract + normalise KYC fields via GPT-4o
  3. 📊 Batch CSV       — bulk normalisation via CSV upload

Run locally:  streamlit run app.py
Deploy:       Streamlit Community Cloud → set OPENAI_API_KEY in Secrets
"""

import os
import sys
import io
import csv
import json
import base64

# ── Inject OPENAI_API_KEY from Streamlit secrets before any pipeline import ──
try:
    import streamlit as st
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass  # Running locally — .env will be loaded by llm_layer.py

import streamlit as st
import openai

# ── Add src/ to path so pipeline imports work ────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from pipeline.pipeline import process_field  # noqa: E402

# ── Constants ─────────────────────────────────────────────────────────────────
# Field types the KYC pipeline actively normalises
_KYC_FIELD_TYPES = ["person_name", "alias", "company_name", "address"]
# Additional types preserved as-is by the rules engine
_ALL_FIELD_TYPES = _KYC_FIELD_TYPES + ["date", "id_number", "nationality", "dob"]

LANGUAGE_OPTIONS: dict[str, str] = {
    "Auto-detect": "",
    "Arabic (ar)": "ar",
    "Chinese Mandarin (zh)": "zh",
    "Greek (el)": "el",
    "Japanese (ja)": "ja",
    "Russian (ru)": "ru",
    "Ukrainian (uk)": "uk",
    "English / Latin (en)": "en",
}
_VALID_LANG_CODES: set[str] = set(LANGUAGE_OPTIONS.values())

ACCEPTED_DOC_EXTENSIONS = ["jpg", "jpeg", "png", "pdf", "docx", "txt"]
_MIME_MAP = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KYC Identity Normalisation",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(
    "<style>[data-testid='stSidebar']{display:none}[data-testid='collapsedControl']{display:none}</style>",
    unsafe_allow_html=True,
)

st.title("🔍 KYC Identity Normalisation")
st.caption("Transliterate, normalise, and translate multilingual identity fields for KYC screening.")

# ── Helper: OpenAI client ─────────────────────────────────────────────────────
def _openai_client() -> openai.OpenAI:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        st.error("OPENAI_API_KEY is not set. Add it in Streamlit Cloud Secrets or a local .env file.")
        st.stop()
    return openai.OpenAI(api_key=key)


# ── Helper: GPT-4o vision OCR + field extraction ──────────────────────────────
def extract_fields_from_image(image_bytes: bytes, mime_type: str) -> list[dict]:
    """Send image to GPT-4o vision; return list of {field_type, original_text, language}."""
    client = _openai_client()
    b64 = base64.b64encode(image_bytes).decode()
    prompt = (
        "You are a KYC document analyst. Examine this document image and extract every identity field you can see.\n"
        "Return a JSON object with key \"fields\" containing a list. Each item must have:\n"
        "  - field_type: one of person_name | alias | company_name | address | date | id_number | nationality\n"
        "  - original_text: the exact text as it appears\n"
        "  - language: ISO 639-1 code (ar, zh, el, ja, ru, uk, en) or empty string for plain Latin\n"
        "Example: {\"fields\": [{\"field_type\": \"person_name\", \"original_text\": \"AHMED SAMIR\", \"language\": \"ar\"}]}"
    )
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}", "detail": "high"}},
                {"type": "text", "text": prompt},
            ],
        }],
        response_format={"type": "json_object"},
        temperature=0,
    )
    data = json.loads(resp.choices[0].message.content)
    return data.get("fields", [])


# ── Helper: extract fields from plain text ────────────────────────────────────
def extract_fields_from_text(text: str) -> list[dict]:
    """Use GPT-4o to classify KYC fields from extracted document text."""
    client = _openai_client()
    prompt = (
        "You are a KYC document analyst. Given this text extracted from a document, identify all identity fields.\n"
        "Return a JSON object with key \"fields\" containing a list. Each item:\n"
        "  - field_type: one of person_name | alias | company_name | address | date | id_number | nationality\n"
        "  - original_text: the text for that field\n"
        "  - language: ISO 639-1 code (ar, zh, el, ja, ru, uk, en) or empty string\n\n"
        f"Document text:\n{text[:4000]}"
    )
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    data = json.loads(resp.choices[0].message.content)
    return data.get("fields", [])


# ── Helper: PDF text extraction ───────────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        import fitz  # pymupdf
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return "\n".join(page.get_text() for page in doc).strip()
    except ImportError:
        return ""


def render_pdf_page_as_png(file_bytes: bytes) -> bytes | None:
    """Render first PDF page as PNG bytes for vision OCR (scanned PDFs)."""
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pix = doc[0].get_pixmap(dpi=150)
        return pix.tobytes("png")
    except Exception:
        return None


# ── Helper: DOCX text extraction ──────────────────────────────────────────────
def extract_text_from_docx(file_bytes: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


# ── Helper: shared field reference table ─────────────────────────────────────
def _show_field_reference(expanded: bool = False) -> None:
    with st.expander("📋 Accepted values for field_type and language", expanded=expanded):
        col_ft, col_lang = st.columns(2)
        with col_ft:
            st.markdown("**`field_type` values**")
            ft_rows = [
                {"field_type": ft, "processing": "✅ Normalised" if ft in _KYC_FIELD_TYPES else "🔒 Preserved as-is"}
                for ft in _ALL_FIELD_TYPES
            ]
            st.table(ft_rows)
        with col_lang:
            st.markdown("**`language` values**")
            lang_rows = [{"code": code or "(empty = auto)", "language": label} for label, code in LANGUAGE_OPTIONS.items()]
            st.table(lang_rows)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_single, tab_docs, tab_batch = st.tabs(
    ["🆔 KYC Normalise", "📄 Documents", "📊 Batch CSV"]
)

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single KYC identity field normalisation
# ════════════════════════════════════════════════════════════════════════════
with tab_single:
    st.markdown(
        "Normalise a **single identity field** (person name, alias, company name, address) "
        "into Latin script for KYC screening. For general prose translation use the **Translate** tab."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        text_input = st.text_area(
            "Original text",
            placeholder="e.g.  山田 太郎  /  Андрей Юрьевич  /  نهاد إبراهيم",
            height=100,
            key="single_text",
        )
    with col2:
        field_type_single = st.selectbox("Field type", _KYC_FIELD_TYPES, key="single_ft", index=0)
        lang_label_single = st.selectbox("Language", list(LANGUAGE_OPTIONS.keys()), key="single_lang", index=0)

    if st.button("Normalise", type="primary", use_container_width=True, key="btn_single"):
        if not text_input.strip():
            st.warning("Please enter some text.")
        else:
            row = {
                "original_text": text_input.strip(),
                "field_type": field_type_single,
                "language": LANGUAGE_OPTIONS[lang_label_single],
            }
            with st.spinner("Processing…"):
                try:
                    result = process_field(row)
                    st.success("Done")

                    # Normalised form with built-in copy button (st.code adds 📋 automatically)
                    st.markdown("**Normalised form** — click 📋 to copy")
                    st.code(result.get("normalised_form", ""), language=None)

                    # Stacked metrics
                    st.metric("Method", result.get("processing_method", "—"))
                    st.metric("Confidence", f"{result.get('confidence', 0):.0%}")

                    if result.get("review_required"):
                        st.warning(f"⚠️ Manual review required: {result.get('review_reason', '')}")
                    if result.get("allowed_variants"):
                        st.info("**Allowed variants:** " + "  |  ".join(result["allowed_variants"]))

                except Exception as exc:
                    st.error(f"Pipeline error: {exc}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Document upload: OCR → field extraction → KYC normalisation
# ════════════════════════════════════════════════════════════════════════════
with tab_docs:
    st.markdown(
        "Upload a document. GPT-4o will OCR the image / extract text, identify KYC fields, "
        "and normalise them automatically.\n\n"
        f"**Accepted formats:** {', '.join(f'`.{t}`' for t in ACCEPTED_DOC_EXTENSIONS)}  \n"
        "For scanned PDFs without embedded text, the first page will be sent to GPT-4o vision."
    )

    _DOC_MAX_MB = 10
    st.caption(f"Max file size: {_DOC_MAX_MB} MB")
    uploaded_doc = st.file_uploader(
        "Upload document",
        type=ACCEPTED_DOC_EXTENSIONS,
        key="doc_upload",
    )

    if uploaded_doc is not None:
        file_bytes = uploaded_doc.read()
        fname = uploaded_doc.name.lower()
        ext = fname.rsplit(".", 1)[-1] if "." in fname else ""

        if len(file_bytes) > _DOC_MAX_MB * 1024 * 1024:
            st.error(f"File exceeds the {_DOC_MAX_MB} MB limit. Please upload a smaller file.")
        elif ext not in ACCEPTED_DOC_EXTENSIONS:
            st.error(
                f"Unsupported format `.{ext}`. "
                f"Accepted: {', '.join(ACCEPTED_DOC_EXTENSIONS)}"
            )
        else:
            # Show image preview
            if ext in ("jpg", "jpeg", "png"):
                st.image(file_bytes, caption=uploaded_doc.name, width=320)

            if st.button("Extract & Normalise Fields", type="primary",
                         use_container_width=True, key="btn_doc"):
                with st.spinner("Processing document…"):
                    try:
                        raw_fields: list[dict] = []

                        if ext in ("jpg", "jpeg", "png"):
                            mime = _MIME_MAP.get(ext, "image/jpeg")
                            raw_fields = extract_fields_from_image(file_bytes, mime)

                        elif ext == "pdf":
                            text = extract_text_from_pdf(file_bytes)
                            if text:
                                raw_fields = extract_fields_from_text(text)
                            else:
                                # Scanned PDF: render first page and send to vision
                                img_bytes = render_pdf_page_as_png(file_bytes)
                                if img_bytes:
                                    st.info("No embedded text found — using vision OCR on page 1.")
                                    raw_fields = extract_fields_from_image(img_bytes, "image/png")
                                else:
                                    st.warning(
                                        "Could not extract text or render this PDF. "
                                        "Try converting it to an image first."
                                    )

                        elif ext == "docx":
                            text = extract_text_from_docx(file_bytes)
                            raw_fields = extract_fields_from_text(text)

                        elif ext == "txt":
                            text = file_bytes.decode("utf-8", errors="replace")
                            raw_fields = extract_fields_from_text(text)

                        if not raw_fields:
                            st.warning("No identity fields were detected in this document.")
                        else:
                            st.success(f"Found {len(raw_fields)} field(s). Normalising…")
                            results = []
                            for f in raw_fields:
                                ft = f.get("field_type", "person_name")
                                row = {
                                    "original_text": f.get("original_text", ""),
                                    "field_type": ft,
                                    "language": f.get("language", ""),
                                }
                                if ft not in _KYC_FIELD_TYPES:
                                    results.append({
                                        "field_type": ft,
                                        "original_text": row["original_text"],
                                        "language": row["language"],
                                        "normalised_form": row["original_text"],
                                        "method": "PRESERVE",
                                        "confidence": "100%",
                                        "review_required": False,
                                    })
                                else:
                                    try:
                                        out = process_field(row)
                                        results.append({
                                            "field_type": ft,
                                            "original_text": row["original_text"],
                                            "language": row["language"],
                                            "normalised_form": out.get("normalised_form", ""),
                                            "method": out.get("processing_method", ""),
                                            "confidence": f"{out.get('confidence', 0):.0%}",
                                            "review_required": out.get("review_required", False),
                                        })
                                    except Exception as exc:
                                        results.append({
                                            "field_type": ft,
                                            "original_text": row["original_text"],
                                            "language": row["language"],
                                            "normalised_form": f"ERROR: {exc}",
                                            "method": "ERROR",
                                            "confidence": "—",
                                            "review_required": True,
                                        })

                            st.dataframe(results, use_container_width=True)

                            out_buf = io.StringIO()
                            out_w = csv.DictWriter(out_buf, fieldnames=list(results[0].keys()))
                            out_w.writeheader()
                            out_w.writerows(results)
                            st.download_button(
                                "⬇ Download results CSV",
                                data=out_buf.getvalue().encode("utf-8"),
                                file_name=f"{uploaded_doc.name}_kyc.csv",
                                mime="text/csv",
                                use_container_width=True,
                            )

                    except Exception as exc:
                        st.error(f"Processing error: {exc}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Batch CSV
# ════════════════════════════════════════════════════════════════════════════
with tab_batch:
    st.markdown(
        "Upload a CSV with columns: **`original_text`**, **`field_type`**, **`language`** (optional).  \n"
        "Additional columns are passed through unchanged."
    )

    _show_field_reference(expanded=True)

    # Template download
    template_rows = [
        {"original_text": "山田 太郎", "field_type": "person_name", "language": "ja"},
        {"original_text": "Андрей Юрьевич Ковалев", "field_type": "person_name", "language": "ru"},
        {"original_text": "نهاد إبراهيم النجار", "field_type": "person_name", "language": "ar"},
        {"original_text": "Mitsubishi Corporation", "field_type": "company_name", "language": ""},
        {"original_text": "18 Tiyu East Road Tianhe District", "field_type": "address", "language": "zh"},
    ]
    template_buf = io.StringIO()
    tw = csv.DictWriter(template_buf, fieldnames=["original_text", "field_type", "language"])
    tw.writeheader()
    tw.writerows(template_rows)
    st.download_button(
        "⬇ Download template CSV",
        data=template_buf.getvalue().encode("utf-8"),
        file_name="kyc_template.csv",
        mime="text/csv",
    )

    _CSV_MAX_MB = 5
    st.caption(f"Max file size: {_CSV_MAX_MB} MB")
    uploaded_csv = st.file_uploader("Upload CSV", type=["csv"], key="batch_csv")

    if uploaded_csv is not None:
        raw_bytes = uploaded_csv.read()
        if len(raw_bytes) > _CSV_MAX_MB * 1024 * 1024:
            st.error(f"File exceeds the {_CSV_MAX_MB} MB limit. Please upload a smaller CSV.")
            uploaded_csv = None
        content = raw_bytes.decode("utf-8") if uploaded_csv is not None else None

    if uploaded_csv is not None and content is not None:
        reader = csv.DictReader(io.StringIO(content))
        input_rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

        col_errors = []
        if "original_text" not in fieldnames:
            col_errors.append("Missing required column: `original_text`")
        if "field_type" not in fieldnames:
            col_errors.append("Missing required column: `field_type`")

        for err in col_errors:
            st.error(err)

        if not col_errors:
            # Validate field_type and language values
            bad_ft = [
                str(i + 1) for i, r in enumerate(input_rows)
                if r.get("field_type", "") not in _ALL_FIELD_TYPES + [""]
            ]
            bad_lang = [
                str(i + 1) for i, r in enumerate(input_rows)
                if r.get("language", "") not in _VALID_LANG_CODES
            ]
            if bad_ft:
                st.warning(
                    f"⚠️ Unknown `field_type` in rows: {bad_ft[:10]}. "
                    f"Valid values: {', '.join(_ALL_FIELD_TYPES)}"
                )
            if bad_lang:
                st.warning(
                    f"⚠️ Unknown `language` code in rows: {bad_lang[:10]}. "
                    f"Valid codes: {', '.join(c for c in sorted(_VALID_LANG_CODES) if c)} (or empty for auto)"
                )

            st.write(f"Loaded **{len(input_rows)} rows**. Preview:")
            st.dataframe(input_rows[:5], use_container_width=True)

            if st.button("Run normalisation", type="primary", use_container_width=True, key="btn_batch"):
                results = []
                progress = st.progress(0, text="Processing…")

                for i, row in enumerate(input_rows):
                    if not row.get("language"):
                        row["language"] = ""
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

                out_buf = io.StringIO()
                out_w = csv.DictWriter(out_buf, fieldnames=list(results[0].keys()) if results else [])
                out_w.writeheader()
                out_w.writerows(results)
                st.download_button(
                    "⬇ Download results CSV",
                    data=out_buf.getvalue().encode("utf-8"),
                    file_name="kyc_normalised.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
